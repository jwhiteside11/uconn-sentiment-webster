# Frontend Flask application for Webster Bank

The frontend consists of a Flask application with HTML views and a client for accessing the backend API. The frontend is deployed as an App Engine service in the `sentiment-test` project. 

The backend API client that assumes the backend services are running on the `sentiment-prod` VM in the `sentiment-analysis` project (see backend [Deployment](/backend#Deployment) guide). 

## Quick start

To run the frontend locally, run as a Flask server or as a gunicorn server.

```bash
# Install dependencies
pip install -r requirements.txt
# Run using Flask
python3 app.py
# OR run using gunicorn - used for production deployment
gunicorn --bind 0.0.0.0:8080 app:app
```

Visit `localhost:8080` in a browser to view the login page. 

**Note:** The frontend can't do much without the backend running, but this can be useful for development.

## Deployment

First, verify that you are working on the `sentiment-test` project:

```bash
gcloud config get-value project
```

Then, deploy the application as an App Engine service based on the configuration in `app.yaml`:

```bash
gcloud app deploy
```

## Routes

### /login

### /search_news

### /graph_news
