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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## API Endpoints

### Authentication

- POST `/auth/register` - Register a new user
- POST `/auth/login` - User login
- POST `/auth/admin/login` - Admin login

### User

- GET `/user/me` - Get current user profile (Protected)
- GET `/user/admin/profile` - Get admin profile (Admin only)
- GET `/user/protected` - Test user protection (Protected)
- GET `/user/admin/protected` - Test admin protection (Admin only)

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Database

The application uses SQLite with SQLAlchemy ORM. The database file will be created automatically when you first run the application.

## Admin Account

An admin account is automatically created during the first run with credentials specified in the `.env` file. 