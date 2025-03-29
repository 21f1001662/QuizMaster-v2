from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.quiz import Quiz, Question, MCQQuestion, NumericQuestion, Option, Attempt, Response
from app.models.subject import Chapter, Subject
from app.models.user import User
from app import db
from app.utils.helpers import admin_required
from app.utils.generative_ai import generate_mcq_question, generate_numeric_question
from sqlalchemy import or_, func, desc, distinct
from datetime import datetime, timedelta
from app.utils.cache import (
    cache_get, cache_set, clear_quizzes_cache, clear_question_cache,
    get_quizzes_cache_key, get_question_cache_key
)

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
    
    # Clear student quizzes cache
    clear_quizzes_cache()
    
    # Trigger notification task
    from app.tasks import notify_users_new_quiz
    notify_users_new_quiz.delay(quiz.id)
    
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
    
    # Clear student quizzes cache
    clear_quizzes_cache()
    
    return jsonify(quiz.to_dict()), 200

@quiz_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Delete all attempts and responses for this quiz
    attempts = Attempt.query.filter_by(quiz_id=quiz_id).all()
    
    for attempt in attempts:
        # Delete all responses for this attempt
        Response.query.filter_by(attempt_id=attempt.id).delete()
        # Delete the attempt
        db.session.delete(attempt)
    
    # Delete the quiz (this will cascade delete questions, options, etc.)
    db.session.delete(quiz)
    db.session.commit()
    
    # Clear student quizzes cache
    clear_quizzes_cache()
    
    return jsonify({'message': 'Quiz and all associated data deleted successfully'}), 200

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
    # Increment total questions count and update total score
    quiz.total_questions += 1
    quiz.total_score += data['correct_marks']  # Add correct marks to total score
    db.session.commit()
    
    # Clear student quizzes cache since total_questions changed
    clear_quizzes_cache()
    
    return jsonify(question.to_dict()), 201

@quiz_bp.route('/quizzes/<int:quiz_id>/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_question(quiz_id, question_id):
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
    data = request.get_json()
    
    # Store old correct marks for updating total score
    old_correct_marks = 0
    if question.type == 'mcq':
        old_correct_marks = question.mcq_question.correct_marks
    else:
        old_correct_marks = question.numeric_question.correct_marks
    
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
    
    # Update quiz total score if correct marks changed
    if 'correct_marks' in data:
        quiz = question.quiz
        quiz.total_score = quiz.total_score - old_correct_marks + data['correct_marks']
    
    db.session.commit()
    
    # Clear both question and quizzes cache
    clear_question_cache(question_id)
    clear_quizzes_cache()
    
    return jsonify(question.to_dict()), 200

@quiz_bp.route('/quizzes/<int:quiz_id>/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(quiz_id, question_id):
    question = Question.query.filter_by(id=question_id, quiz_id=quiz_id).first_or_404()
    quiz = question.quiz
    
    # Get correct marks before deletion for updating total score
    correct_marks = 0
    if question.type == 'mcq':
        correct_marks = question.mcq_question.correct_marks
    else:
        correct_marks = question.numeric_question.correct_marks
    
    # Update quiz total score and question count
    quiz.total_score -= correct_marks
    quiz.total_questions -= 1
    
    # Delete the question (cascade will handle related records)
    db.session.delete(question)
    db.session.commit()
    
    # Clear both question and quizzes cache
    clear_question_cache(question_id)
    clear_quizzes_cache()
    
    return jsonify({'message': 'Question deleted successfully'}), 200

@quiz_bp.route('/student/quizzes', methods=['GET'])
@jwt_required()
def get_student_quizzes():
    # Get query parameters with defaults
    quiz_id = request.args.get('quiz_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    name = request.args.get('name', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    date_lb = request.args.get('date_lb', type=str)
    date_ub = request.args.get('date_ub', type=str)
    sort_by = request.args.get('sort_by', 'date_of_quiz')  # Default sort by date
    sort = request.args.get('sort', 'asc').lower()  # Default ascending order
    
    # Try to get from cache
    cache_key = get_quizzes_cache_key(page, per_page, sort_by, sort, date_lb, date_ub, chapter_id, subject_id, name)
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200
    
    # Validate sort_by parameter
    valid_sort_fields = ['date_of_quiz', 'name', 'duration', 'total_questions']
    if sort_by not in valid_sort_fields:
        return jsonify({'message': f'Invalid sort_by. Must be one of: {", ".join(valid_sort_fields)}'}), 400
    
    # Validate sort direction
    if sort not in ['asc', 'desc']:
        return jsonify({'message': 'Invalid sort. Must be either "asc" or "desc"'}), 400
    
    # Base query with joins
    query = Quiz.query.join(Quiz.chapter).join(Chapter.subject)
    
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
        query = query.filter(Quiz.id == quiz_id)
    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)
    if subject_id:
        query = query.filter(Chapter.subject_id == subject_id)
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
    
    # Prepare response data
    response_data = {
        'quizzes': [quiz.to_dict_student() for quiz in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'sort_by': sort_by,
        'sort': sort
    }
    
    # Store in cache
    cache_set(cache_key, response_data)
    
    return jsonify(response_data), 200

@quiz_bp.route('/student/questions/<int:question_id>', methods=['GET'])
@jwt_required()
def get_student_question(question_id):
    # Try to get from cache
    cache_key = get_question_cache_key(question_id)
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200
    
    question = Question.query.get_or_404(question_id)
    
    # Check if the quiz has started
    quiz = question.quiz
    current_time = datetime.now()
    if current_time < quiz.date_of_quiz:
        return jsonify({'message': 'Quiz has not started yet'}), 403
    
    # Check if the quiz has ended
    if current_time > (quiz.date_of_quiz + timedelta(minutes=quiz.duration)):
        return jsonify({'message': 'Quiz has ended'}), 403
    
    # Prepare response data
    response_data = question.to_dict_student()
    
    # Store in cache with a shorter timeout (1 minute) since this is time-sensitive
    cache_set(cache_key, response_data, timeout=60)
    
    return jsonify(response_data), 200

@quiz_bp.route('/quizzes/<int:quiz_id>/ai/generate', methods=['POST'])
@jwt_required()
@admin_required
def generate_ai_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['num_questions', 'question_type', 'correct_marks', 'incorrect_marks', 'context']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    if data['question_type'] not in ['mcq', 'numeric']:
        return jsonify({'message': 'Invalid question type'}), 400
    
    # Get existing questions to avoid duplicates
    existing_questions = ""
    if data['question_type'] == 'mcq':
        existing_questions = " ".join([q.mcq_question.question_text for q in quiz.questions if q.type == 'mcq'])
    else:
        existing_questions = " ".join([q.numeric_question.question_text for q in quiz.questions if q.type == 'numeric'])
    
    # return jsonify({'message': 'Existing questions retrieved successfully', 'existing_questions': existing_questions}), 200
    generated_questions = []
    for _ in range(data['num_questions']):
        try:
            if data['question_type'] == 'mcq':
                question_data = generate_mcq_question(existing_questions, context=data['context'])
                if not question_data:
                    continue
                
                # Create MCQ question
                mcq = MCQQuestion(
                    question_text=question_data['question_text'],
                    correct_marks=data['correct_marks'],
                    incorrect_marks=data['incorrect_marks']
                )
                db.session.add(mcq)
                db.session.flush()
                
                # Add options
                for option_data in question_data['options']:
                    option = Option(
                        mcq_question_id=mcq.id,
                        text=option_data['text'],
                        is_correct=option_data['is_correct']
                    )
                    db.session.add(option)
                
                question = Question(
                    quiz_id=quiz_id,
                    type='mcq',
                    mcq_question_id=mcq.id
                )
            else:
                question_data = generate_numeric_question(existing_questions, context=data['context'])
                
                if not question_data:
                    continue
                
                # Create numeric question
                numeric = NumericQuestion(
                    question_text=question_data['question_text'],
                    answer_lower_bound=question_data['answer_lower_bound'],
                    answer_upper_bound=question_data['answer_upper_bound'],
                    correct_marks=data['correct_marks'],
                    incorrect_marks=data['incorrect_marks']
                )
                
                db.session.add(numeric)
                db.session.flush()
                
                question = Question(
                    quiz_id=int(quiz_id),
                    type='numeric',
                    numeric_question_id=int(numeric.id)
                )
            
            db.session.add(question)
            generated_questions.append({
                'id': question.id,
                'question_text': question_data['question_text'],
                'type': question.type,
                'correct_marks': data['correct_marks'],
                'incorrect_marks': data['incorrect_marks']
            })
            
            # Update existing questions string for next iteration
            existing_questions += " " + question_data['question_text']
            
        except Exception as e:
            print(f"Error generating question: {str(e)}")
            continue
    
    # Update quiz total questions and score
    quiz.total_questions += len(generated_questions)
    quiz.total_score += len(generated_questions) * data['correct_marks']
    db.session.commit()
    
    # Clear student quizzes cache since total_questions changed
    clear_quizzes_cache()
    
    return jsonify({
        'message': f'Successfully generated {len(generated_questions)} questions',
        'questions': generated_questions
    }), 201

@quiz_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_admin_stats():
    try:
        # Get total users (excluding admin)
        total_users = User.query.filter_by(is_admin=False).count()
        
        # Get total quizzes
        total_quizzes = Quiz.query.count()
        
        # Get total attempts
        total_attempts = Attempt.query.count()
        
        # Calculate subject-wise average scores
        subject_stats = db.session.query(
            Subject.id,
            Subject.name,
            func.count(distinct(Attempt.id)).label('total_attempts'),
            func.avg(Attempt.score).label('avg_score'),
            func.avg(Quiz.total_score).label('avg_total_score')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            Attempt, Quiz.id == Attempt.quiz_id
        ).filter(
            Attempt.status == 'completed'
        ).group_by(
            Subject.id, Subject.name
        ).all()
        
        subject_wise_scores = []
        for stat in subject_stats:
            avg_percentage = (stat.avg_score / stat.avg_total_score * 100) if stat.avg_total_score > 0 else 0
            subject_wise_scores.append({
                'subject_id': stat.id,
                'subject_name': stat.name,
                'total_attempts': stat.total_attempts,
                'average_score': round(stat.avg_score, 2),
                'average_percentage': round(avg_percentage, 2)
            })
        
        # Calculate total average score percentage
        overall_stats = db.session.query(
            func.avg(Attempt.score).label('avg_score'),
            func.avg(Quiz.total_score).label('avg_total_score')
        ).join(
            Quiz, Quiz.id == Attempt.quiz_id
        ).filter(
            Attempt.status == 'completed'
        ).first()
        
        total_average_percentage = 0
        if overall_stats.avg_total_score:
            total_average_percentage = (overall_stats.avg_score / overall_stats.avg_total_score * 100)
        
        # Get top 5 attempted quizzes
        top_quizzes = db.session.query(
            Quiz.id,
            Quiz.name,
            Chapter.name.label('chapter_name'),
            Subject.name.label('subject_name'),
            func.count(Attempt.id).label('attempt_count'),
            func.avg(Attempt.score).label('avg_score'),
            Quiz.total_score
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        ).join(
            Attempt, Quiz.id == Attempt.quiz_id
        ).filter(
            Attempt.status == 'completed'
        ).group_by(
            Quiz.id,
            Quiz.name,
            Chapter.name,
            Subject.name,
            Quiz.total_score
        ).order_by(
            desc('attempt_count')
        ).limit(5).all()
        
        top_attempted_quizzes = []
        for quiz in top_quizzes:
            avg_percentage = (quiz.avg_score / quiz.total_score * 100) if quiz.total_score > 0 else 0
            top_attempted_quizzes.append({
                'quiz_id': quiz.id,
                'quiz_name': quiz.name,
                'chapter_name': quiz.chapter_name,
                'subject_name': quiz.subject_name,
                'total_attempts': quiz.attempt_count,
                'average_score': round(quiz.avg_score, 2),
                'total_score': quiz.total_score,
                'average_percentage': round(avg_percentage, 2)
            })
        
        return jsonify({
            'total_users': total_users,
            'total_quizzes': total_quizzes,
            'total_attempts': total_attempts,
            'subject_wise_scores': subject_wise_scores,
            'total_average_percentage': round(total_average_percentage, 2),
            'top_attempted_quizzes': top_attempted_quizzes
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch admin stats',
            'message': str(e)
        }), 500 