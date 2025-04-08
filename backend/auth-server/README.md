# Auth Server

This service handles user authentication and token validation for the UConn Sentiment Webster web application. It is containerized as a Flask application and is exposed through Nginx at the `/auth` endpoint.

## Overview

The `auth-server` provides two primary endpoints:

- `POST /authenticate` – Authenticates user credentials and returns a JWT token.
- `POST /validate` – Validates a JWT token and returns the associated username if valid.

This service is used internally by other microservices like `data-fetchers` and `reverse-proxy` to enforce secure access to the API.

---

## Files

- **`app.py`** – Defines the Flask server and HTTP routes.
- **`auth_utils.py`** – Contains the `Authenticator` class for handling logic related to authentication and token validation.

---

## Running Locally

To start the server locally (for testing):

1. Install dependencies:
   ```bash
   pip install flask flask-cors bcrypt pyjwt
   ```
2. ```bash
   docker compose up
   ```
3. In another terminal window:
   ```bash
   curl -X POST http://localhost:5200/authenticate -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}'
   ```
4. ```bash
   curl -X POST http://localhost:5200/validate -H "Content-Type: application/json" -d '{"passkey": "<JWT_TOKEN>"}'
   ```

