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

# Question Routes
@quiz_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
@admin_required
def create_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    if 'type' not in data or data['type'] not in ['mcq', 'numeric']:
        return jsonify({'message': 'Invalid question type'}), 400
    
    if data['type'] == 'mcq':
        if not all(field in data for field in ['question_text', 'correct_marks', 'incorrect_marks', 'options']):
            return jsonify({'message': 'Missing required fields for MCQ question'}), 400
        
        mcq = MCQQuestion(
            question_text=data['question_text'],
            correct_marks=data['correct_marks'],
            incorrect_marks=data['incorrect_marks']
        )
        db.session.add(mcq)
        db.session.flush()  # Get the ID of mcq
        
        # Add options
        for option_data in data['options']:
            option = Option(
                mcq_question_id=mcq.id,
                text=option_data['text'],
                is_correct=option_data.get('is_correct', False)
            )
            db.session.add(option)
        
        question = Question(
            quiz_id=quiz_id,
            type='mcq',
            mcq_question_id=mcq.id
        )
        
    else:  # numeric question
        if not all(field in data for field in ['question_text', 'answer_lower_bound', 'answer_upper_bound']):
            return jsonify({'message': 'Missing required fields for numeric question'}), 400
        
        numeric = NumericQuestion(
            question_text=data['question_text'],
            answer_lower_bound=data['answer_lower_bound'],
            answer_upper_bound=data['answer_upper_bound']
        )
        db.session.add(numeric)
        db.session.flush()  # Get the ID of numeric
        
        question = Question(
            quiz_id=quiz_id,
            type='numeric',
            numeric_question_id=numeric.id
        )
    
    db.session.add(question)
    db.session.commit()
    
    return jsonify(question.to_dict()), 201

@quiz_bp.route('/quizzes/<int:quiz_id>/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_question(quiz_id, question_id):
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
    data = request.get_json()
    
    if question.type == 'mcq':
        mcq = question.mcq_question
        if 'question_text' in data:
            mcq.question_text = data['question_text']
        if 'correct_marks' in data:
            mcq.correct_marks = data['correct_marks']
        if 'incorrect_marks' in data:
            mcq.incorrect_marks = data['incorrect_marks']
        if 'options' in data:
            # Delete existing options
            Option.query.filter_by(mcq_question_id=mcq.id).delete()
            # Add new options
            for option_data in data['options']:
                option = Option(
                    mcq_question_id=mcq.id,
                    text=option_data['text'],
                    is_correct=option_data.get('is_correct', False)
                )
                db.session.add(option)
    else:
        numeric = question.numeric_question
        if 'question_text' in data:
            numeric.question_text = data['question_text']
        if 'answer_lower_bound' in data:
            numeric.answer_lower_bound = data['answer_lower_bound']
        if 'answer_upper_bound' in data:
            numeric.answer_upper_bound = data['answer_upper_bound']
    
    db.session.commit()
    return jsonify(question.to_dict()), 200

@quiz_bp.route('/quizzes/<int:quiz_id>/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(quiz_id, question_id):
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Question deleted successfully'}), 200 