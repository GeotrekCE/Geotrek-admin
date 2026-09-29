#!/usr/bin/env bash
set -euo pipefail

# Définir le répertoire de travail comme sécurisé pour git (si exécuté en root dans un volume monté)
git config --global --add safe.directory /workspace 2>/dev/null || true

TARGET_DIR="/opt/geotrek-admin"
PKG_ROOT="/tmp/pkg-dist"
VERSION="${DEB_VERSION:-$(git describe --tags --always 2>/dev/null | sed 's/^v//' || echo "1.0.0")}"
PYTHON_VERSION="${PYTHON_VERSION:-3.13}"

echo "=== 1. Résolution et installation des dépendances de build (mk-build-deps) ==="
apt-get update

# Génère un paquet dummy (geotrek-admin-build-deps_*.deb) basé sur debian/control
# --install (-i) l'installe via apt-get avec toutes ses dépendances
# --remove (-r) supprime le paquet dummy après l'installation des dépendances
mk-build-deps --install --remove \
    --tool='apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y' \
    debian/control

# Nettoyage des fichiers temporaires laissés par mk-build-deps si existants
rm -f geotrek-admin-build-deps_*

echo "=== 2. Préparation du runtime Python ${PYTHON_VERSION} via uv ==="
rm -rf "${TARGET_DIR}" "${PKG_ROOT}"
mkdir -p "${TARGET_DIR}/runtime" "${PKG_ROOT}"

export UV_PYTHON_INSTALL_DIR="${TARGET_DIR}/runtime"
uv python install "${PYTHON_VERSION}" --install-dir "${UV_PYTHON_INSTALL_DIR}"

PYTHON_BIN=$(find "${UV_PYTHON_INSTALL_DIR}" -name python3 -perm -111 | head -n 1)
if [ -z "${PYTHON_BIN}" ]; then
    echo "ERREUR : Binaire python3 introuvable dans ${UV_PYTHON_INSTALL_DIR}" >&2
    exit 1
fi
echo "Interpréteur Python utilisé : ${PYTHON_BIN}"

echo "=== 3. Création du venv et installation des dépendances ==="
# Le venv est créé directement dans TARGET_DIR pour reproduire la structure historique dh-virtualenv
uv venv "${TARGET_DIR}" --allow-existing --python "${PYTHON_BIN}"
# Lien de compatibilité si un outil ou script référence /opt/geotrek-admin/venv
ln -sfn . "${TARGET_DIR}/venv"

echo "Installation des dépendances depuis requirements.txt..."
uv pip install -r requirements.txt --python "${TARGET_DIR}/bin/python"

echo "Compilation des messages gettext..."
"${TARGET_DIR}/bin/django-admin" compilemessages || "${TARGET_DIR}/bin/python" manage.py compilemessages || true

echo "Installation du paquet Geotrek dans l'environnement..."
uv pip install --no-deps . --python "${TARGET_DIR}/bin/python"

echo "=== 4. Optimisation de l'arborescence ==="
find "${TARGET_DIR}/runtime" -type d -name "test" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}/runtime" -type d -name "tests" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "=== 5. Préparation de l'arborescence du paquet (staging) ==="
mkdir -p "${PKG_ROOT}/opt" \
         "${PKG_ROOT}/DEBIAN" \
         "${PKG_ROOT}/etc/logrotate.d" \
         "${PKG_ROOT}/lib/systemd/system" \
         "${PKG_ROOT}/usr/sbin"

# 5.1 Fichiers de configuration et arborescence var/
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
    echo "Note : frontend/dist non présent dans le workspace, dossier var/frontend créé vide."
fi

# Copie de l'arborescence /opt/geotrek-admin
cp -a "${TARGET_DIR}" "${PKG_ROOT}/opt/"

# 5.2 Lien symbolique usr/sbin/geotrek
ln -sf /opt/geotrek-admin/bin/manage.py "${PKG_ROOT}/usr/sbin/geotrek"

# 5.3 Fichiers systemd et logrotate
cp debian/geotrek*.service "${PKG_ROOT}/lib/systemd/system/"
cp debian/geotrek-admin.logrotate "${PKG_ROOT}/etc/logrotate.d/geotrek-admin"

# 5.4 Fichiers de contrôle DEBIAN
# conffiles
cp debian/conffiles "${PKG_ROOT}/DEBIAN/conffiles"
echo "/etc/logrotate.d/geotrek-admin" >> "${PKG_ROOT}/DEBIAN/conffiles"
sort -u "${PKG_ROOT}/DEBIAN/conffiles" -o "${PKG_ROOT}/DEBIAN/conffiles"

# debconf : config et templates (sans préfixe geotrek-admin.)
cp debian/geotrek-admin.config "${PKG_ROOT}/DEBIAN/config"
chmod 755 "${PKG_ROOT}/DEBIAN/config"

cp debian/geotrek-admin.templates "${PKG_ROOT}/DEBIAN/templates"
chmod 644 "${PKG_ROOT}/DEBIAN/templates"

if [ -f debian/geotrek-admin.triggers ]; then
    cp debian/geotrek-admin.triggers "${PKG_ROOT}/DEBIAN/triggers"
    chmod 644 "${PKG_ROOT}/DEBIAN/triggers"
fi

# Scripts postinst, prerm, postrm avec intégration systemd
sed '/#DEBHELPER#/d' debian/postinst > "${PKG_ROOT}/DEBIAN/postinst"
cat << 'EOF' >> "${PKG_ROOT}/DEBIAN/postinst"

# Intégration systemd
if [ "$1" = "configure" ] || [ "$1" = "abort-upgrade" ] || [ "$1" = "abort-deconfigure" ] || [ "$1" = "abort-remove" ] ; then
	if [ -d /run/systemd/system ]; then
		systemctl --system daemon-reload >/dev/null 2>&1 || true
		systemctl enable geotrek.service geotrek-ui.service geotrek-api.service geotrek-celery.service >/dev/null 2>&1 || true
		systemctl restart geotrek.service >/dev/null 2>&1 || true
	fi
fi
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

cat << 'EOF' > "${PKG_ROOT}/DEBIAN/prerm"
#!/bin/sh -e
if [ "$1" = "remove" ] || [ "$1" = "upgrade" ] || [ "$1" = "deconfigure" ]; then
	if [ -d /run/systemd/system ]; then
		systemctl stop geotrek.service geotrek-ui.service geotrek-api.service geotrek-celery.service >/dev/null 2>&1 || true
	fi
fi
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/prerm"

sed '/#DEBHELPER#/d' debian/postrm > "${PKG_ROOT}/DEBIAN/postrm"
cat << 'EOF' >> "${PKG_ROOT}/DEBIAN/postrm"

if [ "$1" = "purge" ]; then
	if which deb-systemd-helper >/dev/null 2>&1; then
		deb-systemd-helper purge 'geotrek.service' >/dev/null 2>&1 || true
	fi
fi
if [ -d /run/systemd/system ]; then
	systemctl --system daemon-reload >/dev/null 2>&1 || true
fi
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postrm"

# DEBIAN/control binaire
INSTALLED_SIZE=$(du -sk "${PKG_ROOT}" | awk '{print $1}')
DEPENDS=$(awk '
    /^Package:/ { in_pkg=1 }
    in_pkg && /^Depends:/ { in_dep=1; next }
    in_dep && /^[A-Za-z0-9_-]*:/ { in_dep=0; in_pkg=0 }
    in_dep { print }
' debian/control | tr -d '\n' | sed -e 's/\${[^}]*},*//g' -e 's/^[ ,]*//' -e 's/[ ,]*$//' -e 's/  */ /g' -e 's/, *,/, /g')

cat << EOF > "${PKG_ROOT}/DEBIAN/control"
Package: geotrek-admin
Version: ${VERSION}
Architecture: amd64
Maintainer: Geotrek Team <support.geotrek@makina-corpus.com>
Installed-Size: ${INSTALLED_SIZE}
Depends: ${DEPENDS}
Section: misc
Priority: optional
Homepage: https://github.com/GeotrekCE/Geotrek-admin/
Description: Manage and promote your trails and tourist content and activities.
EOF
chmod 644 "${PKG_ROOT}/DEBIAN/control"

echo "=== 6. Construction du paquet .deb ==="
DEB_FILE="/workspace/geotrek-admin_${VERSION}_amd64.deb"
dpkg-deb --build --root-owner-group "${PKG_ROOT}" "${DEB_FILE}"

echo "=== Inspection du paquet généré ==="
dpkg-deb -I "${DEB_FILE}"

# Nettoyage du répertoire temporaire de staging
rm -rf "${PKG_ROOT}"

echo "=== Succès : ${DEB_FILE} généré avec succès ==="