# UConn Sentiment Webster Project

![alt text](/devops/images/dashboard.png)

This repository contains the full stack web application built for the UConn Stamford Sentiment Analysis Webster Project.

## Quick start

This application is dependent on Google Cloud, even when running locally. At the bare minimum, you must have access to the `sentiment-test` project and must have `gcloud` (the Google Cloud CLI) installed locally. Once installed, run the following command to provide authorization for your machine. 

```bash
gcloud auth application-default login
```

To run the full application locally, use `docker compose`.

```bash
docker compose -f docker-compose-local.yml up
```

The frontend is visible at `localhost:8080`, and the backend at `localhost:5100`.

## Deployment

The frontend is deployed to App Engine, while the backend is deployed to Compute Engine. Select a folder for detailed deployment notes.

## Architecture Overview

![alt text](/devops/images/architecture.png)

A full stack web application backed by microservices running on Google Cloud.