# Geotrek-admin mobile

TODO intoduction

## Installation

Il convient de créer une variable d'environnement et définir l'host de l'URL du Geotrek-Admin
connecté et la langue par défaut de l'application

```sh
cp .env.dist .env
```

Installation des packages nécessaires à l'application

```sh
nvm use
npm ci
```

## Développement

### Linting

```sh
npm run lint
npm run tsc
```

### Environnement de développement

```sh
npm run dev
```

## Environnement de production

## Avec DOCKER (recommandé)

TODO

### Sans DOCKER

```sh
npm run build
```

Créer une règle serveur pour pointer la route `/offline` vers le dossier
`/frontend/dist`.

Exemple de règle avec `nginx`

```sh
location /offline {
  alias /opt/geotrek-admin/frontend/dist;
}
```
