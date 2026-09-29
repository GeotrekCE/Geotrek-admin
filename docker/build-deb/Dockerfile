FROM ubuntu:jammy

ENV DEBIAN_FRONTEND=noninteractive

# Outils stricts nécessaires pour parser debian/control et résoudre Build-Depends
RUN apt-get update && apt-get install -y --no-install-recommends \
    devscripts \
    equivs \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# uv pour le runtime Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV TARGET_DIR=/opt/geotrek-admin
WORKDIR /workspace

COPY docker/build-deb/build.sh /usr/local/bin/build-deb.sh
RUN chmod +x /usr/local/bin/build-deb.sh

# Utilise le script monté dans /workspace si disponible (permet d'itérer sans rebuild de l'image),
# ou bascule sur le script copié dans l'image.
RUN printf '#!/bin/sh\nif [ -f /workspace/docker/build-deb/build.sh ]; then\n    exec /workspace/docker/build-deb/build.sh "$@"\nelse\n    exec /usr/local/bin/build-deb.sh "$@"\nfi\n' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]