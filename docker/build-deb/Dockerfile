FROM ubuntu:jammy

ENV DEBIAN_FRONTEND=noninteractive

# Minimal tools required to parse debian/control and resolve Build-Depends
RUN apt-get update && apt-get install -y --no-install-recommends \
    devscripts \
    equivs \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# uv for Python runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV TARGET_DIR=/opt/geotrek-admin
WORKDIR /workspace

COPY docker/build-deb/build.sh /usr/local/bin/build-deb.sh
RUN chmod +x /usr/local/bin/build-deb.sh

# Use script mounted in /workspace if available (allows quick iteration without rebuilding image),
# or fallback to script baked into image.
RUN printf '#!/bin/sh\nif [ -f /workspace/docker/build-deb/build.sh ]; then\n    exec /workspace/docker/build-deb/build.sh "$@"\nelse\n    exec /usr/local/bin/build-deb.sh "$@"\nfi\n' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]