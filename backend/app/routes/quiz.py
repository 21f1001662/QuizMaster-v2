from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.quiz import Quiz, Question, MCQQuestion, NumericQuestion, Option
from app import db
from app.utils.helpers import admin_required
from sqlalchemy import or_
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

# Quiz Routes
@quiz_bp.route('/quizzes', methods=['POST'])
@jwt_required()
@admin_required
def create_quiz():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['chapter_id', 'date_of_quiz', 'duration', 'total_questions']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        date_of_quiz = datetime.fromisoformat(data['date_of_quiz'])
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use ISO format'}), 400
    
    quiz = Quiz(
        chapter_id=data['chapter_id'],
        date_of_quiz=date_of_quiz,
        duration=data['duration'],
        total_questions=data['total_questions'],
        remarks=data.get('remarks', ''),
        instructions=data.get('instructions', '')
    )
    
    db.session.add(quiz)
    db.session.commit()
    
    return jsonify(quiz.to_dict()), 201

@quiz_bp.route('/quizzes', methods=['GET'])
@jwt_required()
@admin_required
def get_quizzes():
    chapter_id = request.args.get('chapter_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query
    query = Quiz.query
    
    # Apply filters
    if chapter_id:
        query = query.filter_by(chapter_id=chapter_id)
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'quizzes': [quiz.to_dict() for quiz in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    if 'date_of_quiz' in data:
        try:
            quiz.date_of_quiz = datetime.fromisoformat(data['date_of_quiz'])
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use ISO format'}), 400
    
    if 'duration' in data:
        quiz.duration = data['duration']
    if 'total_questions' in data:
        quiz.total_questions = data['total_questions']
    if 'remarks' in data:
        quiz.remarks = data['remarks']
    if 'instructions' in data:
        quiz.instructions = data['instructions']
    
    db.session.commit()
    return jsonify(quiz.to_dict()), 200

@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz deleted successfully'}), 200
