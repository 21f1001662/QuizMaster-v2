import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_test_email():
    """
    Send a test email using Gmail SMTP
    Returns True if email was sent successfully, False otherwise
    """
    try:
        # Email configuration
        sender_email = os.getenv('GMAIL_USERNAME')
        sender_password = os.getenv('GMAIL_PASSWORD')
        receiver_email = "21f1001662@ds.study.iitm.ac.in"
        
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