# UConn Sentiment Webster Backend

This repository holds the backend code for the UConn Sentiment Webster web application. 

The project is structured into subfolders that each represent a microservices. These services are designed to run as Docker containers on the Google Compute Engine production instance. Select a service for more information.

To run the backend locally, refer to the application [Quick start](/#Quick+start).

## Deployment

**Note:** Only one instance of the application should be deployed on the VM at one time. Make sure any existing containers are stopped before deploying a new version.

First, SSH into the `sentiment-prod` VM instance in the `sentiment-analysis` project.

From there, pull the code into the VM.
```bash
# if you don't already have the code base on your VM
git clone https://github.com/jwhiteside11/uconn-sentiment-webster.git

# if you DO already have the code, the following will update
git pull https://github.com/jwhiteside11/uconn-sentiment-webster.git
```

Run all services as a daemon:
```bash
sudo docker compose up -d
# (Ctrl + B) + D
```

This will run the `docker-compose.yml` file, building the Docker images and running the containers for each service. The backend is now up and running.

To stop the daemon:
```bash
sudo docker compose down
# (Ctrl + B) + D
```

The main API is `data-fetchers` service, exposed through Nginx by the `/api` endpoint. Refer to the [API reference](/backend/data-fetchers#api-reference) for useful API endpoints. **Note:** each request must contain `WBS-API-PASSKEY` as either a header or a cookie for authorization.

The `auth-server` is exposed through Nginx by the `/auth` endpoint. Refer to the [API reference](/backend/auth-server#api-reference) for authorization endpoints.
  

**Containerized Services**:
- `auth-server` - Flask server for authenticating and validating user credentials for the login page and subsequently each API request. Used by `data-fetchers` and `reverse-proxy`.
- `data-fetchers` - Flask server for scraping news data, interfacing with Datastore, interfacing with Typesense, and interfacing with the sentiment model. Used by `reverse-proxy`.
- `sentiment-model` - Flask server for scoring and summarizing sentiment in text, interacting with model; code from original ckury repo. Used by `data-fetchers`.
- `reverse-proxy` - Nginx server exposing public services,`data-fetchers` and `auth-server`.
- `typesense` - Typesense server for searching news data. Used by `data-fetchers`.

