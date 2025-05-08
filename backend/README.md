# QuizMaster Backend

A Flask-based backend for the QuizMaster application with JWT authentication and role-based access control.

## Prerequisites

- Python 3.8+
- Redis server
- SQLite3

## Features

- User and Admin authentication
- JWT-based authentication
- Role-based access control
- SQLite database with SQLAlchemy ORM
- RESTful API endpoints

## API Doc:
[https://documenter.getpostman.com/view/32768981/2sB2cPk5ny](https://documenter.getpostman.com/view/32768981/2sB2cPk5ny)

## Setup

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Update the variables in `.env` with your values
   ```bash
   FLASK_APP=app
   FLASK_ENV=development
   FLASK_DEBUG=1
   SECRET_KEY=your-super-secret-key-change-in-production
   DATABASE_URL=sqlite:///quizmaster.db?timeout=30&check_same_thread=False&cached_statements=128
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin123
   ADMIN_FULLNAME=Administrator 
   OPEN_AI_KEY=<open ai key>
   GEMINI_API_KEY=<gemini API Key>
   GMAIL_USERNAME=shahbaz.ali.connect@gmail.com
   GMAIL_PASSWORD=<gmail app password>
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ```

## Running the Application

1. Start Redis server (if not already running):
```bash
sudo service redis-server start  # On Linux
# On Windows, start Redis server from the installed service
```

2. Start Celery worker (in a new terminal):
```bash
celery -A app.tasks worker --loglevel=info
```

3. Start Celery Beat (in a new terminal):
```bash  
celery -A app.tasks beat --loglevel=info
```

4. Start the Flask application (in another terminal):
```bash
flask run
```

The application will be available at `http://localhost:5000`

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
