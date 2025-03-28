# QuizMaster Backend

A Flask-based backend for the QuizMaster application with JWT authentication and role-based access control.

## Features

- User and Admin authentication
- JWT-based authentication
- Role-based access control
- SQLite database with SQLAlchemy ORM
- RESTful API endpoints

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the variables in `.env` as needed

4. Run the application:
```bash
flask run
```


## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Database

The application uses SQLite with SQLAlchemy ORM. The database file will be created automatically when you first run the application.

## Admin Account

An admin account is automatically created during the first run with credentials specified in the `.env` file.

## Database Migrations

### Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Migration Commands

#### Initialize Migrations (First Time Only)
```bash
flask db init
```

#### Create New Migration
```bash
flask db migrate -m "Description of changes"
```

#### Apply Migrations
```bash
flask db upgrade
```

#### Rollback Last Migration
```bash
flask db downgrade
```

#### View Migration History
```bash
flask db history
```

#### View Current Migration Version
```bash
flask db current
```