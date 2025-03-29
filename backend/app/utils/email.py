import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_email():
    try:
        # Email configuration
        sender_email = os.getenv('GMAIL_USERNAME')
        sender_password = os.getenv('GMAIL_PASSWORD')
        receiver_email = "21f1oo1662@ds.iitm.ac.in"
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Test Email from QuizMaster"
        
        # Email body
        body = """
        Hello,
        
        This is a test email from the QuizMaster application.
        
        Best regards,
        QuizMaster
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
        
        print(f"Test email sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"Error sending test email: {str(e)}")
        return False

def send_quiz_notification(quiz_name, chapter_name, subject_name, receiver_email, receiver_name):
    try:
        # Email configuration
        sender_email = os.getenv('GMAIL_USERNAME')
        sender_password = os.getenv('GMAIL_PASSWORD')
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"New Quiz Available: {quiz_name}"
        
        # Email body
        body = f"""
        Dear {receiver_name},

        A new quiz has been created for your course:

        Quiz: {quiz_name}
        Chapter: {chapter_name}
        Subject: {subject_name}

        Please log in to the QuizMaster application to take the quiz.

        Best regards,
        QuizMaster Team
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
        
        print(f"Quiz notification sent successfully to {receiver_email}")
        return True
        
    except Exception as e:
        print(f"Error sending quiz notification: {str(e)}")
        return False 