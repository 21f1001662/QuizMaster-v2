from celery import Celery
from app.utils.email import send_quiz_notification, send_inactive_user_notification, send_quiz_report, send_monthly_report
from app.models.user import User
from app.models.quiz import Quiz, Attempt
from app.models.subject import Subject, Chapter
from app.models.login_tracking import DailyLogin
from app import db, create_app
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from celery.utils.log import get_task_logger
from celery.schedules import crontab
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from sqlalchemy import func, desc

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_task_logger(__name__)

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

# Configure the Celery Beat Schedule
celery.conf.beat_schedule = {
    'send-inactive-users-email': {
        'task': 'app.tasks.check_inactive_users',
        'schedule': crontab(hour=20, minute=0),  # Run daily at 8 PM local time
    },
    'generate-monthly-report': {
        'task': 'app.tasks.generate_and_send_monthly_report',
        'schedule': crontab(day_of_month=30, hour=0, minute=0),  # Run on 27th day of every month at midnight
    },
}

# @celery.task
# def hello_world():
#     logger.info("Hello world")
#     return "Hello world printed successfully"

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
        # print("Checking inactive users")
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
                # print(f"Last login for {user.full_name}: {last_login}")
                if not last_login or (today - last_login.login_date).days >= 1:
                    inactive_users.append(user)
            
            # Send notifications to inactive users
            for user in inactive_users:
                if user.email:  # Only send if user has an email
                    send_inactive_user_notification(user.full_name, user.email)
                    
            return f"Checked {len(users)} users, found {len(inactive_users)} inactive users,"
            
    except Exception as e:
        return f"Error checking inactive users: {str(e)}"

@celery.task
def send_quiz_report_email(quiz_id, user_id, csv_filepath):
    try:
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Get quiz and user details
            quiz = Quiz.query.get(quiz_id)
            user = User.query.get(user_id)
            
            if not quiz or not user:
                return f"Quiz or User not found: quiz_id={quiz_id}, user_id={user_id}"
            
            if not user.email:
                return f"User {user_id} does not have an email address"
            
            # Send email with report
            success = send_quiz_report(
                quiz_name=quiz.name,
                receiver_email=user.email,
                receiver_name=user.full_name,
                csv_filepath=csv_filepath
            )
            
            if success:
                return f"Quiz report sent successfully to {user.email}"
            else:
                return f"Failed to send quiz report to {user.email}"
            
    except Exception as e:
        return f"Error sending quiz report: {str(e)}"

@celery.task
def generate_and_send_monthly_report():
    try:
        # Create Flask application context
        app = create_app()
        
        with app.app_context():
            # Get admin user
            admin = User.query.filter_by(is_admin=True).first()
            if not admin or not admin.email:
                return "Admin user not found or has no email"

            # Get current date and first day of the month
            today = datetime.now()
            first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Generate filename
            filename = f"monthly_report_{today.strftime('%Y_%m')}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            elements.append(Paragraph(f"Monthly Report - {today.strftime('%B %Y')}", title_style))
            
            # 1. Number of attempts in month
            attempts_count = Attempt.query.filter(
                Attempt.created_at >= first_day,
                Attempt.created_at <= today,
                Attempt.status == 'completed'  # Only count completed attempts
            ).count()
            
            # 2. Number of students registered in the month
            new_users = User.query.filter(
                User.created_at >= first_day,
                User.created_at <= today,
                User.is_admin == False  # Only count non-admin users
            ).count()
            
            # 3. Average quiz score in the month
            avg_score = db.session.query(func.avg(Attempt.score)).filter(
                Attempt.created_at >= first_day,
                Attempt.created_at <= today,
                Attempt.status == 'completed'
            ).scalar() or 0
            
            # Basic statistics table
            basic_stats = [
                ['Metric', 'Value'],
                ['Total Quiz Attempts', str(attempts_count)],
                ['New Student Registrations', str(new_users)],
                ['Average Quiz Score', f"{avg_score:.2f}%"]
            ]
            
            basic_stats_table = Table(basic_stats, [300, 200])
            basic_stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(basic_stats_table)
            elements.append(Spacer(1, 20))
            
            # 4. Subject-wise average score
            subject_scores = db.session.query(
                Subject.name,
                func.avg(Attempt.score).label('avg_score')
            ).join(Chapter, Subject.chapters)\
             .join(Quiz, Quiz.chapter_id == Chapter.id)\
             .join(Attempt, Attempt.quiz_id == Quiz.id)\
             .filter(
                Attempt.created_at >= first_day,
                Attempt.created_at <= today,
                Attempt.status == 'completed'
             )\
             .group_by(Subject.name)\
             .all()
            
            elements.append(Paragraph("Subject-wise Average Scores", styles['Heading2']))
            
            subject_data = [['Subject', 'Average Score']]
            for subject, score in subject_scores:
                subject_data.append([subject, f"{score:.2f}%" if score else "No attempts"])
            
            subject_table = Table(subject_data, [300, 200])
            subject_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(subject_table)
            elements.append(Spacer(1, 20))
            
            # 5. Top 5 attempted quizzes
            top_quizzes = db.session.query(
                Quiz.name,
                func.count(Attempt.id).label('attempt_count')
            ).join(Attempt)\
             .filter(
                Attempt.created_at >= first_day,
                Attempt.created_at <= today,
                Attempt.status == 'completed'
             )\
             .group_by(Quiz.id, Quiz.name)\
             .order_by(desc('attempt_count'))\
             .limit(5)\
             .all()
            
            elements.append(Paragraph("Top 5 Attempted Quizzes", styles['Heading2']))
            
            quiz_data = [['Quiz Name', 'Number of Attempts']]
            for quiz, count in top_quizzes:
                quiz_data.append([quiz, str(count)])
            
            quiz_table = Table(quiz_data, [300, 200])
            quiz_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(quiz_table)
            
            # Build PDF
            doc.build(elements)
            
            # Send email to admin
            month_year = today.strftime('%B %Y')
            success = send_monthly_report(
                receiver_email=admin.email,
                receiver_name=admin.full_name,
                pdf_filepath=filepath,
                month_year=month_year
            )
            
            if success:
                return f"Monthly report generated and sent successfully to {admin.email}"
            else:
                return f"Monthly report generated but failed to send email to {admin.email}"
            
    except Exception as e:
        return f"Error generating monthly report: {str(e)}" 