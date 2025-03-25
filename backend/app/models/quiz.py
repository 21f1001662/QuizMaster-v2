from app import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # duration in minutes
    remarks = db.Column(db.Text)
    instructions = db.Column(db.Text)
    total_questions = db.Column(db.Integer, default=0)  # Set default to 0
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    chapter = db.relationship('Chapter', backref='quizzes', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'chapter_id': self.chapter_id,
            'date_of_quiz': self.date_of_quiz.isoformat(),
            'duration': self.duration,
            'remarks': self.remarks,
            'instructions': self.instructions,
            'total_questions': self.total_questions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'questions': [question.to_dict() for question in self.questions]
        }

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'mcq' or 'numeric'
    mcq_question_id = db.Column(db.Integer, db.ForeignKey('mcq_questions.id'))
    numeric_question_id = db.Column(db.Integer, db.ForeignKey('numeric_questions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mcq_question = db.relationship('MCQQuestion', backref='question', lazy=True, uselist=False)
    numeric_question = db.relationship('NumericQuestion', backref='question', lazy=True, uselist=False)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if self.type == 'mcq':
            data['question_details'] = self.mcq_question.to_dict() if self.mcq_question else None
        else:
            data['question_details'] = self.numeric_question.to_dict() if self.numeric_question else None
            
        return data

class MCQQuestion(db.Model):
    __tablename__ = 'mcq_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    correct_marks = db.Column(db.Float, nullable=False)
    incorrect_marks = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('Option', backref='mcq_question', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'correct_marks': self.correct_marks,
            'incorrect_marks': self.incorrect_marks,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'options': [option.to_dict() for option in self.options]
        }

class NumericQuestion(db.Model):
    __tablename__ = 'numeric_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    answer_lower_bound = db.Column(db.Float, nullable=False)
    answer_upper_bound = db.Column(db.Float, nullable=False)
    correct_marks = db.Column(db.Float, nullable=False)
    incorrect_marks = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'answer_lower_bound': self.answer_lower_bound,
            'answer_upper_bound': self.answer_upper_bound,
            'correct_marks': self.correct_marks,
            'incorrect_marks': self.incorrect_marks,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Option(db.Model):
    __tablename__ = 'options'
    
    id = db.Column(db.Integer, primary_key=True)
    mcq_question_id = db.Column(db.Integer, db.ForeignKey('mcq_questions.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'is_correct': self.is_correct,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Attempt(db.Model):
    __tablename__ = 'attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='started')  # started, completed, result_declared
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quiz = db.relationship('Quiz', backref='attempts', lazy=True)
    user = db.relationship('User', backref='attempts', lazy=True)
    responses = db.relationship('Response', backref='attempt', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'score': self.score,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'responses': [response.to_dict() for response in self.responses]
        }

class Response(db.Model):
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    attempt_id = db.Column(db.Integer, db.ForeignKey('attempts.id'), nullable=False)
    mcq_question_answer = db.Column(db.Integer, db.ForeignKey('options.id'))
    numeric_question_answer = db.Column(db.Float)
    is_attempted = db.Column(db.Boolean, default=False)
    is_correct = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    question = db.relationship('Question', backref='responses', lazy=True)
    selected_option = db.relationship('Option', backref='responses', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'attempt_id': self.attempt_id,
            'mcq_question_answer': self.mcq_question_answer,
            'numeric_question_answer': self.numeric_question_answer,
            'is_attempted': self.is_attempted,
            'is_correct': self.is_correct,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 