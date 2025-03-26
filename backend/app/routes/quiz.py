from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.quiz import Quiz, Question, MCQQuestion, NumericQuestion, Option
from app.models.subject import Chapter
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
    required_fields = ['name', 'chapter_id', 'date_of_quiz', 'duration']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    try:
        date_of_quiz = datetime.fromisoformat(data['date_of_quiz'])
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use ISO format'}), 400
    
    quiz = Quiz(
        name=data['name'],
        chapter_id=data['chapter_id'],
        date_of_quiz=date_of_quiz,
        duration=data['duration'],
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
    # Get query parameters with defaults
    quiz_id = request.args.get('quiz_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)
    name = request.args.get('name', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_lb = request.args.get('date_lb', type=str)
    date_ub = request.args.get('date_ub', type=str)
    sort_by = request.args.get('sort_by', 'date_of_quiz')  # Default sort by date
    sort = request.args.get('sort', 'asc').lower()  # Default ascending order
    
    # Validate sort_by parameter
    valid_sort_fields = ['date_of_quiz', 'name', 'duration', 'total_questions', 'created_at', 'updated_at']
    if sort_by not in valid_sort_fields:
        return jsonify({'message': f'Invalid sort_by. Must be one of: {", ".join(valid_sort_fields)}'}), 400
    
    # Validate sort direction
    if sort not in ['asc', 'desc']:
        return jsonify({'message': 'Invalid sort. Must be either "asc" or "desc"'}), 400
    
    # Base query
    query = Quiz.query
    
    # Apply date range filters if provided
    if date_lb:
        try:
            date_lb = datetime.fromisoformat(date_lb)
            query = query.filter(Quiz.date_of_quiz >= date_lb)
        except ValueError:
            return jsonify({'message': 'Invalid date_lb format. Use ISO format (YYYY-MM-DD)'}), 400
    
    if date_ub:
        try:
            date_ub = datetime.fromisoformat(date_ub)
            query = query.filter(Quiz.date_of_quiz <= date_ub)
        except ValueError:
            return jsonify({'message': 'Invalid date_ub format. Use ISO format (YYYY-MM-DD)'}), 400
    
    # Apply filters
    if quiz_id:
        query = query.filter_by(id=quiz_id)
    if chapter_id:
        query = query.filter_by(chapter_id=chapter_id)
    if name:
        # Fuzzy search on quiz name
        query = query.filter(Quiz.name.ilike(f'%{name}%'))
    
    # Apply sorting
    sort_column = getattr(Quiz, sort_by)
    if sort == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'quizzes': [quiz.to_dict() for quiz in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'sort_by': sort_by,
        'sort': sort
    }), 200

@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    if 'name' in data:
        quiz.name = data['name']
    if 'date_of_quiz' in data:
        try:
            quiz.date_of_quiz = datetime.fromisoformat(data['date_of_quiz'])
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use ISO format'}), 400
    
    if 'duration' in data:
        quiz.duration = data['duration']
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
        if not all(field in data for field in ['question_text', 'answer_lower_bound', 'answer_upper_bound', 'correct_marks', 'incorrect_marks']):
            return jsonify({'message': 'Missing required fields for numeric question'}), 400
        
        numeric = NumericQuestion(
            question_text=data['question_text'],
            answer_lower_bound=data['answer_lower_bound'],
            answer_upper_bound=data['answer_upper_bound'],
            correct_marks=data['correct_marks'],
            incorrect_marks=data['incorrect_marks']
        )
        db.session.add(numeric)
        db.session.flush()  # Get the ID of numeric
        
        question = Question(
            quiz_id=quiz_id,
            type='numeric',
            numeric_question_id=numeric.id
        )
    
    db.session.add(question)
    # Increment total questions count
    quiz.total_questions += 1
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
        if 'correct_marks' in data:
            numeric.correct_marks = data['correct_marks']
        if 'incorrect_marks' in data:
            numeric.incorrect_marks = data['incorrect_marks']
    
    db.session.commit()
    return jsonify(question.to_dict()), 200

@quiz_bp.route('/quizzes/<int:quiz_id>/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(quiz_id, question_id):
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
    quiz = question.quiz
    
    # Delete related records based on question type
    if question.type == 'mcq':
        # Delete all options first
        Option.query.filter_by(mcq_question_id=question.mcq_question_id).delete()
        # Delete the MCQ question
        MCQQuestion.query.filter_by(id=question.mcq_question_id).delete()
    else:  # numeric question
        # Delete the numeric question
        NumericQuestion.query.filter_by(id=question.numeric_question_id).delete()
    
    # Decrement total questions count
    quiz.total_questions -= 1
    
    # Finally delete the question record
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question and related records deleted successfully'}), 200

@quiz_bp.route('/student/quizzes', methods=['GET'])
@jwt_required()
def get_student_quizzes():
    # Get query parameters with defaults
    quiz_id = request.args.get('quiz_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)
    name = request.args.get('name', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_lb = request.args.get('date_lb', type=str)
    date_ub = request.args.get('date_ub', type=str)
    sort_by = request.args.get('sort_by', 'date_of_quiz')  # Default sort by date
    sort = request.args.get('sort', 'asc').lower()  # Default ascending order
    
    # Validate sort_by parameter
    valid_sort_fields = ['date_of_quiz', 'name', 'duration', 'total_questions']
    if sort_by not in valid_sort_fields:
        return jsonify({'message': f'Invalid sort_by. Must be one of: {", ".join(valid_sort_fields)}'}), 400
    
    # Validate sort direction
    if sort not in ['asc', 'desc']:
        return jsonify({'message': 'Invalid sort. Must be either "asc" or "desc"'}), 400
    
    # Base query
    query = Quiz.query
    
    # Apply date range filters if provided
    if date_lb:
        try:
            date_lb = datetime.fromisoformat(date_lb)
            query = query.filter(Quiz.date_of_quiz >= date_lb)
        except ValueError:
            return jsonify({'message': 'Invalid date_lb format. Use ISO format (YYYY-MM-DD)'}), 400
    
    if date_ub:
        try:
            date_ub = datetime.fromisoformat(date_ub)
            query = query.filter(Quiz.date_of_quiz <= date_ub)
        except ValueError:
            return jsonify({'message': 'Invalid date_ub format. Use ISO format (YYYY-MM-DD)'}), 400
    
    # Apply filters
    if quiz_id:
        query = query.filter_by(id=quiz_id)
    if chapter_id:
        query = query.filter_by(chapter_id=chapter_id)
    if name:
        # Fuzzy search on quiz name
        query = query.filter(Quiz.name.ilike(f'%{name}%'))
    
    # Apply sorting
    sort_column = getattr(Quiz, sort_by)
    if sort == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'quizzes': [quiz.to_dict_student() for quiz in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'sort_by': sort_by,
        'sort': sort
    }), 200 