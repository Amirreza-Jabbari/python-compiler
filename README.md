          
# Python Compiler Project Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Development Setup](#development-setup)
   - [Docker Setup](#docker-setup)
4. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
5. [Features](#features)
   - [User Authentication](#user-authentication)
   - [Code Execution](#code-execution)
   - [Interactive Input](#interactive-input)
6. [API Reference](#api-reference)
   - [Authentication API](#authentication-api)
   - [Compiler API](#compiler-api)
   - [WebSocket API](#websocket-api)
7. [Frontend Guide](#frontend-guide)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## Introduction

The Python Compiler is a web-based application that allows users to write, execute, and interact with Python code in a secure, isolated environment. The system provides real-time feedback, supports interactive input during code execution, and includes user authentication for personalized experiences.

This project is designed with a microservices architecture, consisting of separate services for authentication, code compilation/execution, and the frontend interface, all orchestrated using Docker and Docker Compose.

## System Architecture

![System Architecture](/architecture-diagram.png)

The Python Compiler consists of the following components:

1. **Auth Service**: A Django REST API service responsible for user registration, authentication, and JWT token management.

2. **Compiler Service**: A Django service that handles Python code execution, with the following components:
   - REST API for code submission
   - Celery workers for asynchronous code execution
   - WebSocket server for real-time communication with the frontend
   - Redis for caching and message queuing

3. **Frontend**: A React-based single-page application that provides the user interface.

4. **Nginx**: A reverse proxy that routes requests to the appropriate services and serves static files.

5. **PostgreSQL**: Database for the Auth Service.

6. **RabbitMQ**: Message broker for Celery tasks.

7. **Redis**: Cache for interactive prompts and user inputs during code execution.

## Installation

### Prerequisites

- Docker and Docker Compose
- Git

For local development:
- Python 3.8+
- Node.js 14+
- npm or yarn
- PostgreSQL
- Redis
- RabbitMQ

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/Amirreza-Jabbari/python-compiler.git
cd python-compiler
```

2. Set up the Auth Service:

```bash
cd auth_service
pip install -r requirements.txt
cp .env.example .env  # Edit the .env file with your configuration
python manage.py migrate
python manage.py runserver 8001
```

3. Set up the Compiler Service:

```bash
cd ../compiler_service
pip install -r requirements.txt
cp .env.example .env  # Edit the .env file with your configuration
python manage.py migrate
python manage.py runserver 8002
```

4. Start Celery worker for the Compiler Service:

```bash
cd ../compiler_service
celery -A compiler_service worker --loglevel=info
```

5. Set up the Frontend:

```bash
cd ../compiler-frontend
npm install
npm run dev
```

### Docker Setup

The easiest way to run the entire application is using Docker Compose:

```bash
docker-compose up -d
```

This will start all the services defined in the `docker-compose.yml` file. The application will be accessible at http://localhost.

## Configuration

### Environment Variables

#### Auth Service

Create a `.env` file in the `auth_service` directory with the following variables:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True  # Set to False in production
POSTGRES_DB=auth_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost  # Use 'postgres' for Docker
POSTGRES_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Compiler Service

Create a `.env` file in the `compiler_service` directory with the following variables:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
REDIS_HOST=localhost  # Use 'redis' for Docker
REDIS_PORT=6379
RABBITMQ_HOST=localhost  # Use 'rabbitmq' for Docker
RABBITMQ_PORT=5672
CODE_EXECUTION_MAX_TIME=5  # Maximum execution time in seconds
CODE_EXECUTION_MAX_MEMORY=100  # Maximum memory usage in MB
```

## Features

### User Authentication

The Python Compiler provides a complete authentication system with the following features:

- User registration with username, email, and password
- User login with JWT token authentication
- Token refresh mechanism

### Code Execution

The core feature of the Python Compiler is the ability to execute Python code:

- Secure execution in an isolated environment
- Resource limits (CPU time, memory usage)
- Code validation to prevent malicious code execution
- Asynchronous execution using Celery

### Interactive Input

The Python Compiler supports interactive input during code execution:

- Real-time communication using WebSockets
- Input prompts displayed to the user
- User can provide input that is sent back to the executing code

## API Reference

### Authentication API

#### Register a new user

```
POST /api/users/register/
```

Request body:
```json
{
  "username": "user123",
  "password": "securepassword",
  "password2": "securepassword",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "username": "user123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login

```
POST /api/users/login/
```

Request body:
```json
{
  "username": "user123",
  "password": "securepassword"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Compiler API

#### Execute Code

```
POST /api/compiler/execute/
```

Headers:
```
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "code": "print('Hello, World!')"
}
```

Response:
```json
{
  "message": "Code execution started",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### WebSocket API



## Frontend Guide

The frontend is built with React and uses the following libraries:

- React Router for navigation
- Axios for HTTP requests
- Material-UI for UI components
- Native WebSocket API for real-time communication

### Pages

1. **Login Page**: User authentication
2. **Register Page**: New user registration
3. **Code Executor Page**: Main interface for code execution

### Code Execution Flow

1. User enters Python code in the editor
2. User clicks "Execute Code" button
3. Frontend sends a POST request to `/api/compiler/execute/`
4. Backend starts asynchronous code execution
5. Frontend establishes WebSocket connection
6. If the code requires input, the backend sends a prompt via WebSocket
7. User enters input in the prompt field
8. Frontend sends the input back via WebSocket
9. Backend continues code execution with the provided input
10. Output is displayed in real-time

## Security Considerations

### Code Execution Security

- **Input Validation**: All Python code is validated before execution to prevent malicious code.
- **Resource Limits**: CPU time and memory usage are limited to prevent resource exhaustion.
- **Restricted Imports**: Dangerous modules like `os`, `subprocess`, and `sys` are blocked.

### Authentication Security

- **JWT Tokens**: Secure authentication using JWT tokens with expiration.
- **Password Hashing**: User passwords are securely hashed using Django's authentication system.
- **CORS Protection**: Cross-Origin Resource Sharing is restricted to allowed origins only.

### Network Security

- **HTTPS Support**: WebSocket connections support secure WebSocket protocol (WSS) when accessed via HTTPS.
- **Nginx as Reverse Proxy**: All requests are routed through Nginx, adding an extra layer of security.

## Troubleshooting

### Common Issues

#### WebSocket Connection Failed

- Check if the WebSocket server is running
- Ensure you're using the correct protocol (ws:// for HTTP, wss:// for HTTPS)
- Verify that the session ID is valid

#### Code Execution Timeout

- Check if your code has infinite loops
- Increase the `CODE_EXECUTION_MAX_TIME` value in the environment variables

#### Database Connection Issues

- Verify PostgreSQL credentials in the `.env` file
- Check if the PostgreSQL server is running

### Logs

To view logs in Docker:

```bash
docker-compose logs -f auth_service
docker-compose logs -f compiler_service_web
docker-compose logs -f compiler_service_worker
```

## Contributing

Contributions to the Python Compiler project are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write unit tests for new features
- Update documentation for significant changes

---

© 2025 Python Compiler Project. All rights reserved.

        