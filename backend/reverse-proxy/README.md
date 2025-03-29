# Nginx reverse proxy server

The Nginx server acting as a reverse proxy allows us to expose only one port yet access multiple different microservices. We expose the `data-fetchers` and `auth-server` services for public use.

# Quick start

As a proxy to other backend services, the full backend must be running. Use `docker compose` in the `/backend` folder to spin up all the services along with the Nginx server.

## Routes

### /auth

Routes to the `auth-server` service at port 5200.

#### Example
`localhost:5100/auth/authenticate` maps to `localhost:5200/authenticate`.

### /api

Routes to the `data-fetchers` service at port 5300.

#### Example
`localhost:5100/api/scrape_news` maps to `localhost:5300/scrape_news`.