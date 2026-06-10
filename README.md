# Flume

Hey there! Thanks for checking out Flume.

## Overview

This project gives you a robust foundation for building modern web applications, handling user authentication and running background tasks reliably. It lets you process data, send emails, and integrate with external services, all while giving you deep insights into how everything's performing under the hood.

## Description

Flume is a highly scalable and observable backend API, built to handle complex operations with ease. It features a sophisticated authentication system supporting both Google OAuth and magic links, asynchronous task processing with Celery for long-running jobs, and a comprehensive observability stack to give you full visibility into its operations. It's designed to be the reliable core of your next big idea.

## Installation

Let's get Flume running on your machine. We'll use Docker Compose to spin up all the services, including the database, message broker, and the full observability stack.

1.  **Clone the Repository**

    Start by cloning the project from GitHub:

    ```bash
    git clone https://github.com/ojogu/flume.git
    cd flume/backend # Navigate to the backend directory where the code lives
    ```

2.  **Create a `.env` file**

    You'll need to set up your environment variables. Create a file named `.env` in the `backend` directory (where `pyproject.toml` is located) with the following variables. Remember to replace placeholder values with your actual secrets and configurations.

    ```ini
    # Database
    DATABASE_URL="postgresql+asyncpg://user:password@db:5432/flumedb"

    # Redis
    REDIS_URL="redis://redis:6379/0"

    # JWT Authentication
    JWT_SECRET_KEY="your_super_secret_jwt_key_here"
    JWT_ALGO="HS256"
    ACCESS_TOKEN_EXPIRY=3600 # seconds (e.g., 1 hour)
    REFRESH_TOKEN_EXPIRY=7 # days

    # Frontend URL (for redirects)
    FRONTEND_URL="http://localhost:3000" # Or your actual frontend URL

    # Encryption (for sensitive data like refresh tokens)
    ENCRYPTION_KEY="your_fernet_encryption_key_here_must_be_base64_32_bytes" # e.g., Fernet.generate_key().decode()

    # Celery (Async Task Queue)
    CELERY_BROKER_URL="redis://redis:6379/0"
    CELERY_RESULT_BACKEND="redis://redis:6379/0"
    CELERY_BEAT_INTERVAL=60 # seconds, for scheduled tasks

    # Google OAuth
    CLIENT_ID="your_google_oauth