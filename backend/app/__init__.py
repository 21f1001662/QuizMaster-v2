from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import timedelta
import os

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configure Flask app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # Set token expiry to 24 hours
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})  # Enable CORS for all routes
    
    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.subject import subject_bp
    from app.routes.quiz import quiz_bp
    from app.routes.quiz_attempts import quiz_attempts
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(subject_bp, url_prefix='/api')
    app.register_blueprint(quiz_bp, url_prefix='/api')
    app.register_blueprint(quiz_attempts, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        create_admin()
    
    return app

def create_admin():
    from app.models.user import User
    from app.utils.helpers import hash_password
    
    # Check if admin already exists
    admin = User.query.filter_by(username=os.getenv('ADMIN_USERNAME')).first()
    if not admin:
        admin = User(
            username=os.getenv('ADMIN_USERNAME'),
            password=hash_password(os.getenv('ADMIN_PASSWORD')),
            full_name=os.getenv('ADMIN_FULLNAME'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit() 