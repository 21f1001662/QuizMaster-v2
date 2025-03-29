from celery import Celery
from app.utils.email import send_test_email, send_quiz_notification
from app.models.user import User
from app.models.quiz import Quiz
from app.models.login_tracking import DailyLogin
from app import db, create_app
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Celery
celery = Celery('quizmaster',
                broker=os.getenv('CELERY_BROKER_URL'),
                backend=os.getenv('CELERY_RESULT_BACKEND'))

# Optional configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# @celery.task
# def send_welcome_email():
#     try:
#         success = send_test_email()
#         if success:
#             return "Welcome email sent successfully"
#         return "Failed to send welcome email"
#     except Exception as e:
#         return f"Error sending welcome email: {str(e)}"

@celery.task
def notify_users_new_quiz(quiz_id):
    try:
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Get quiz details
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return f"Quiz with ID {quiz_id} not found"
            
            # Get all non-admin users
            users = User.query.filter_by(is_admin=False).all()
            
            # Send notification to each user
            for user in users:
                if user.email:  # Only send if user has an email
                    send_quiz_notification(
                        quiz_name=quiz.name,
                        chapter_name=quiz.chapter.name,
                        subject_name=quiz.chapter.subject.name,
                        receiver_email=user.email,
                        receiver_name=user.full_name
                    )
            
            return f"Quiz notifications sent to {len(users)} users"
            
    except Exception as e:
        return f"Error sending quiz notifications: {str(e)}"

@celery.task
def check_inactive_users():
    try:
        print("Checking inactive users")
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Get all non-admin users
            users = User.query.filter_by(is_admin=False).all()
            today = datetime.now().date()
            inactive_users = []
            
            # Check each user's last login
            for user in users:
                last_login = DailyLogin.get_last_login(user.id)
                if not last_login or (today - last_login.login_date).days >= 1:
                    inactive_users.append(user)
            
            # Send notifications to inactive users
            for user in inactive_users:
                if user.email:  # Only send if user has an email
                    # To do send email
                    print(f"Sending email to {user.full_name} at {user.email}") 
                    pass
            
            return f"Checked {len(users)} users, found {len(inactive_users)} inactive users"
            
    except Exception as e:
        return f"Error checking inactive users: {str(e)}" 