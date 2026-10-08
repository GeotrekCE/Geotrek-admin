#!/usr/bin/env bash
set -euo pipefail

# Set workspace as safe directory for git (if running as root in a mounted volume)
git config --global --add safe.directory /workspace 2>/dev/null || true

TARGET_DIR="/opt/geotrek-admin"
PKG_ROOT="/tmp/pkg-dist"
VERSION="${DEB_VERSION:-$(git describe --tags --always 2>/dev/null | sed 's/^v//' || echo "1.0.0")}"
PYTHON_VERSION="${PYTHON_VERSION:-3.13}"

echo "=== 1. Resolving and installing build dependencies (mk-build-deps) ==="
apt-get update

# Generate a dummy package (geotrek-admin-build-deps_*.deb) based on debian/control
# --install (-i) installs it via apt-get along with all its dependencies
# --remove (-r) removes the dummy package after installing dependencies
mk-build-deps --install --remove \
    --tool='apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y' \
    debian/control

# Clean up temporary files left by mk-build-deps if any
rm -f geotrek-admin-build-deps_*

echo "=== 2. Preparing Python ${PYTHON_VERSION} runtime via uv ==="
rm -rf "${TARGET_DIR}" "${PKG_ROOT}"
mkdir -p "${TARGET_DIR}/runtime" "${PKG_ROOT}"

export UV_PYTHON_INSTALL_DIR="${TARGET_DIR}/runtime"
uv python install "${PYTHON_VERSION}" --install-dir "${UV_PYTHON_INSTALL_DIR}"

PYTHON_BIN=$(find "${UV_PYTHON_INSTALL_DIR}" -name python3 -perm -111 | head -n 1)
if [ -z "${PYTHON_BIN}" ]; then
    echo "ERROR: python3 binary not found in ${UV_PYTHON_INSTALL_DIR}" >&2
    exit 1
fi
echo "Python interpreter used: ${PYTHON_BIN}"

echo "=== 3. Creating venv and installing dependencies ==="
# Create venv directly in TARGET_DIR to replicate historical dh-virtualenv layout
uv venv "${TARGET_DIR}" --allow-existing --python "${PYTHON_BIN}"
# Compatibility symlink if a tool or script references /opt/geotrek-admin/venv
ln -sfn . "${TARGET_DIR}/venv"

echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt \
    --no-binary numpy \
    --config-settings-package numpy:setup-args="-Dcpu-baseline=none" \
    --python "${TARGET_DIR}/bin/python"

echo "Compiling gettext messages..."
"${TARGET_DIR}/bin/django-admin" compilemessages || "${TARGET_DIR}/bin/python" manage.py compilemessages || true

echo "Installing Geotrek package into environment..."
uv pip install --no-deps . --python "${TARGET_DIR}/bin/python"

echo "=== 4. Optimizing directory tree ==="
find "${TARGET_DIR}/runtime" -type d -name "test" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}/runtime" -type d -name "tests" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "=== 5. Preparing package directory tree (staging) ==="
mkdir -p "${PKG_ROOT}/opt" \
         "${PKG_ROOT}/DEBIAN" \
         "${PKG_ROOT}/etc/logrotate.d" \
         "${PKG_ROOT}/etc/apt/sources.list.d" \
         "${PKG_ROOT}/lib/systemd/system" \
         "${PKG_ROOT}/usr/sbin"
chmod 755 "${PKG_ROOT}/DEBIAN"

# 5.1 Configuration files and var/ directory layout
mkdir -p "${TARGET_DIR}/var/conf/extra_static" \
         "${TARGET_DIR}/var/log" \
         "${TARGET_DIR}/var/cache/sessions" \
         "${TARGET_DIR}/var/cache/api_v2" \
         "${TARGET_DIR}/var/cache/fat" \
         "${TARGET_DIR}/var/media/upload" \
         "${TARGET_DIR}/var/pid" \
         "${TARGET_DIR}/var/mobile" \
         "${TARGET_DIR}/var/tmp" \
         "${TARGET_DIR}/var/frontend"

cp conf/env.in "${TARGET_DIR}/var/conf/"
cp conf/nginx.conf.in "${TARGET_DIR}/var/conf/"
cp conf/gunicorn-geotrek.conf.py.in "${TARGET_DIR}/var/conf/"
cp conf/gunicorn-geotrek_api.conf.py.in "${TARGET_DIR}/var/conf/"

if [ -d "/workspace/frontend/dist" ]; then
    cp -a /workspace/frontend/dist "${TARGET_DIR}/var/frontend/"
else
    echo "Note: frontend/dist not found in workspace, creating empty var/frontend directory."
fi

# Copy /opt/geotrek-admin directory tree
cp -a "${TARGET_DIR}" "${PKG_ROOT}/opt/"

# 5.2 Symlink usr/sbin/geotrek
ln -sf /opt/geotrek-admin/bin/manage.py "${PKG_ROOT}/usr/sbin/geotrek"

# 5.3 System files (systemd, logrotate, apt sources)
cp debian/geotrek*.service "${PKG_ROOT}/lib/systemd/system/"
cp debian/geotrek-admin.logrotate "${PKG_ROOT}/etc/logrotate.d/geotrek-admin"
cp debian/geotrek.sources "${PKG_ROOT}/etc/apt/sources.list.d/"
install -Dm644 debian/apt.geotrek.gpg "${PKG_ROOT}/etc/apt/keyrings/apt.geotrek.gpg"

# 5.4 DEBIAN control files
cp debian/conffiles "${PKG_ROOT}/DEBIAN/conffiles"
chmod 644 "${PKG_ROOT}/DEBIAN/conffiles"

cp debian/geotrek-admin.config "${PKG_ROOT}/DEBIAN/config"
chmod 755 "${PKG_ROOT}/DEBIAN/config"

cp debian/geotrek-admin.templates "${PKG_ROOT}/DEBIAN/templates"
chmod 644 "${PKG_ROOT}/DEBIAN/templates"

if [ -f debian/geotrek-admin.triggers ]; then
    cp debian/geotrek-admin.triggers "${PKG_ROOT}/DEBIAN/triggers"
    chmod 644 "${PKG_ROOT}/DEBIAN/triggers"
fi

cp debian/postinst "${PKG_ROOT}/DEBIAN/postinst"
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

cp debian/prerm "${PKG_ROOT}/DEBIAN/prerm"
chmod 755 "${PKG_ROOT}/DEBIAN/prerm"

cp debian/postrm "${PKG_ROOT}/DEBIAN/postrm"
chmod 755 "${PKG_ROOT}/DEBIAN/postrm"

# Generate DEBIAN/control via dpkg-gencontrol from debian/control
dpkg-gencontrol -pgeotrek-admin -P"${PKG_ROOT}" -v"${VERSION}" -Vmisc:Depends="" -Vshlibs:Depends="" -USource -f"${PKG_ROOT}/files"
chmod 644 "${PKG_ROOT}/DEBIAN/control"
rm -f "${PKG_ROOT}/files"

echo "=== 6. Building .deb package ==="
DEB_FILE="/workspace/geotrek-admin_${VERSION}_amd64.deb"
dpkg-deb --build --root-owner-group "${PKG_ROOT}" "${DEB_FILE}"

echo "=== Inspecting generated package ==="
dpkg-deb -I "${DEB_FILE}"

# Clean up temporary staging directory
rm -rf "${PKG_ROOT}"

echo "=== Success: ${DEB_FILE} successfully generated ==="