# UConn Sentiment Webster Backend

This repository is a collective effort of UConn students to provide backend services for the Sentiment Analysis application. 

The project is structured into subfolders that each represent a Docker container. These containers are designed to run on the Google Compute Engine production instance. Select a service for more information.

## Docker Compose

First, install docker if necessary.

```bash
sudo apt install docker.io
sudo apt install docker-compose-v2
```

Then, to run all services:
```bash
tmux new-session -A -t backend

# from tmux session
sudo docker compose up
# (Ctrl + B) + D
```

This will run the `docker-compose.yml` file, building the Docker images and running the containers for each service. The images can taken about 10 minutes to build.

The backend is now up and running. You can confirm by testing the 'hello, world' endpoint:
```bash
curl 'http://localhost:5100/api' -H 'WBS-API-PASSKEY: ...'
```

The main API is `data-fetchers` service, exposed through Nginx by the `/api` endpoint. Refer to the [API reference](/data-fetchers#api-reference) for useful API endpoints. **Note:** each request must contain `WBS-API-PASSKEY` as either a header or a cookie for authorization.

The `auth-server` is exposed through Nginx by the `/auth` endpoint. Refer to the [API reference](/auth-server#api-reference) for authorization endpoints.
  

**Containerized Services**:
- `reverse-proxy` - Nginx server with routes pointing to `data-fetchers` service and `auth` service. These two are the only public facing services exposed, the rest should only be used internally.
- `data-fetchers` - Flask server for scraping news data, interfacing with Datastore, and interfacing with Typesense.
- `auth-server` - Flask server for authenticating and validating user credentials for the login page and subsequently each API request. Used by `data-fetchers`.
- `ckury-services` - Flask server for scoring and summarizing sentiment in text, interacting with model; code from original ckury repo. Used by `data-fetchers`.
- `typesense` - Typesense server for searching news data. Used by `data-fetchers`.

