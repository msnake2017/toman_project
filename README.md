# Toman Shop Project

This project is a Dockerized web application built with Django Ninja, featuring Nginx as a reverse proxy, PostgreSQL for database management, and Redis for caching and real-time operations.

## Features

- **FastAPI-like simplicity** with Django Ninja for building APIs.
- **Dockerized** for seamless deployment and environment consistency.
- **Redis** integration for caching and background tasks.
- **PostgreSQL** as the database backend for robust data storage.
- **Nginx** for handling HTTP requests and serving as a reverse proxy.
- **Interactive API Documentation** available at `/api/docs`.

---

## Prerequisites

To run this project, ensure you have the following:

- [Docker](https://www.docker.com/) installed on your system.
- Environment variables set up as listed below.

### Required Environment Variables

The following environment variables must be specified in a `.env` file or directly in the Docker environment:

```plaintext
DB_NAME=<your_database_name>
DB_USER=<your_database_user>
DB_PASSWORD=<your_database_password>
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Create a `.env` File

In the project root, create a `.env` file and add the required environment variables:

```bash
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
```

### 3. Build and Run Docker Containers

Run the following command to build and start the containers:

```bash
docker-compose up --build
```

This command will:
- Build the Django Ninja application.
- Start PostgreSQL, Redis, and Nginx containers.

### 4. Access the Application

- **API Base URL:** `http://localhost`
- **Interactive API Documentation:** `http://localhost/api/docs`

---

## Project Structure

```plaintext
.
├── core/                # Django Ninja application
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Dockerfile for Django app
├── .env                 # Environment variables file
└── README.md            # Project documentation
```

---

## API Documentation

The API documentation is auto-generated and accessible at `/api/docs` once the application is running. Use this interface to test endpoints and view available API methods.

---

## Troubleshooting

1. **Container Fails to Start:**
   - Ensure the `.env` file is correctly configured with the required variables.
   - Check Docker logs for specific error messages using:
     ```bash
     docker-compose logs
     ```

2. **Cannot Access API Documentation:**
   - Verify that the Nginx container is running properly.
   - Ensure you are visiting `http://localhost/api/docs` in your browser.

---


## Acknowledgments

- [Django Ninja](https://django-ninja.rest-framework.com/) for its simplicity and speed.
- [Docker](https://www.docker.com/) for containerization.
- [Redis](https://redis.io/) for caching solutions.
- [PostgreSQL](https://www.postgresql.org/) for robust database management.
- [Nginx](https://www.nginx.com/) for efficient request handling.
