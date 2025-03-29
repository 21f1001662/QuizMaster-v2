from datetime import datetime
from app import db

class DailyLogin(db.Model):
    __tablename__ = 'daily_logins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship with User model
    user = db.relationship('User', backref=db.backref('daily_logins', lazy=True))
    
    def __repr__(self):
        return f'<DailyLogin {self.user_id} {self.login_date}>'
    
    @classmethod
    def get_last_login(cls, user_id):
        """Get the last login date for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.login_date.desc()).first()
    
    @classmethod
    def record_login(cls, user_id):
        """Record a new login for a user"""
        today = datetime.now().date()
        
        # Check if user already logged in today
        existing_login = cls.query.filter_by(
            user_id=user_id,
            login_date=today
        ).first()
        
        if not existing_login:
            new_login = cls(user_id=user_id, login_date=today)
            db.session.add(new_login)
            db.session.commit()
            return True
        return False 