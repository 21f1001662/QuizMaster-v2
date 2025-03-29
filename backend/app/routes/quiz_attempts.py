from flask import Blueprint, request, jsonify
from app.models.quiz import Quiz, Question, Attempt, Response
from app.models.user import User
from app.models.subject import Chapter, Subject
from app import db
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc
import os
from app.tasks import send_quiz_report_email

quiz_attempts = Blueprint('quiz_attempts', __name__)

@quiz_attempts.route('/quizzes/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    user_id = get_jwt_identity()
    
    # Check if quiz exists
    quiz = Quiz.query.get_or_404(quiz_id)
    
    # Check if user has already attempted this quiz
    existing_attempt = Attempt.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
    if existing_attempt:
        return jsonify({'error': 'You have already attempted this quiz'}), 400
    
    # Check if quiz is currently active using local time
    current_time = datetime.now()  # This will use local time
    quiz_start_time = quiz.date_of_quiz
    quiz_end_time = quiz.date_of_quiz + timedelta(minutes=quiz.duration)
    
    if current_time < quiz_start_time:
        return jsonify({
            'error': 'Quiz has not started yet'
        }), 400
    
    if current_time > quiz_end_time:
        return jsonify({
            'error': 'Quiz has ended'
        }), 400
    
    # Create new attempt
    attempt = Attempt(
        quiz_id=quiz_id,
        user_id=user_id,
        status='started'
    )
    db.session.add(attempt)
    
    # Create blank submissions for all questions
    for question in quiz.questions:
        response = Response(
            attempt_id=attempt.id,
            question_id=question.id,
            is_attempted=False
        )
        db.session.add(response)
    
    db.session.commit()
    return jsonify(attempt.to_dict()), 201

# To-Do: Implement queue for quiz submission
@quiz_attempts.route('/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_quiz(attempt_id):
    user_id = int(get_jwt_identity())
    
    # Get attempt
    attempt = Attempt.query.get_or_404(attempt_id)
    
    # Verify ownership
    if attempt.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if already completed
    if attempt.status == 'completed':
        return jsonify({'error': 'Quiz already submitted'}), 400
    
    # Check if time limit exceeded
    quiz = attempt.quiz
    if datetime.now() > quiz.date_of_quiz + timedelta(minutes=quiz.duration):
        return jsonify({'error': 'Time limit exceeded'}), 400
    
    # Process all questions and calculate score
    total_score = 0
    for question in quiz.questions:
        response = Response.query.filter_by(
            attempt_id=attempt_id,
            question_id=question.id
        ).first()
        
        if not response:
            # Create unattempted response
            response = Response(
                attempt_id=attempt_id,
                question_id=question.id,
                is_attempted=False,
                is_correct=False
            )
            db.session.add(response)
            continue
        
        # Check if answer is correct
        if question.type == 'mcq':
            if response.mcq_question_answer:
                # Find the selected option from the options list
                selected_option = next(
                    (opt for opt in question.mcq_question.options if opt.id == response.mcq_question_answer),
                    None
                )
                if selected_option and selected_option.is_correct:
                    response.is_correct = True
                    total_score += question.mcq_question.correct_marks
                else:
                    total_score += question.mcq_question.incorrect_marks
        else:  # numeric question
            if response.numeric_question_answer is not None:
                if (question.numeric_question.answer_lower_bound <= response.numeric_question_answer <= 
                    question.numeric_question.answer_upper_bound):
                    response.is_correct = True
                    total_score += question.numeric_question.correct_marks
                else:
                    total_score += question.numeric_question.incorrect_marks
    
    # Update attempt status and score
    attempt.status = 'completed'
    attempt.score = total_score
    attempt.completed_at = datetime.now()
    
    db.session.commit()
    return jsonify(attempt.to_dict())

@quiz_attempts.route('/attempts/<int:attempt_id>/questions/<int:question_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_question(attempt_id, question_id):
    user_id = int(get_jwt_identity())

    # Get attempt and verify ownership
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if attempt is still active
    if attempt.status != 'started':
        return jsonify({'error': 'Quiz attempt is not active'}), 400
    
    # Check if quiz time is still valid
    quiz = attempt.quiz
    current_time = datetime.now()
    if current_time > quiz.date_of_quiz + timedelta(minutes=quiz.duration):
        attempt.status = 'completed'  # Auto-complete if time exceeded
        attempt.completed_at = current_time
        db.session.commit()
        return jsonify({'error': 'Quiz time has ended'}), 400
    
    # Get question
    question = Question.query.get_or_404(question_id)
    if question.quiz_id != attempt.quiz_id:
        return jsonify({'error': 'Question does not belong to this quiz'}), 400
    
    # Get or create response
    response = Response.query.filter_by(
        attempt_id=attempt_id,
        question_id=question_id
    ).first()
    
    # Update response based on question type
    data = request.get_json()
    if question.type == 'mcq':
        if 'option_id' not in data:
            return jsonify({'error': 'Option ID is required for MCQ questions'}), 400
        response.mcq_question_answer = data['option_id']
        response.is_attempted = True
    else:  # numeric question
        if 'answer' not in data:
            return jsonify({'error': 'Answer is required for numeric questions'}), 400
        response.numeric_question_answer = float(data['answer'])
        response.is_attempted = True

    db.session.add(response)
    db.session.commit()
    
    return jsonify(response.to_dict())

@quiz_attempts.route('/attempts', methods=['GET'])
@jwt_required()
def get_attempt_details():
    user_id = int(get_jwt_identity())
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    search = request.args.get('search', '')
    quiz_id = request.args.get('quiz_id', type=int)
    chapter_id = request.args.get('chapter_id', type=int)
    attempt_id = request.args.get('attempt_id', type=int)
    subject_id = request.args.get('subject_id', type=int)  # New subject_id filter
    
    # Base query with joins
    query = Attempt.query.join(Quiz).join(Chapter).join(Subject).filter(Attempt.user_id == user_id)
    
    # Apply filters if provided
    if quiz_id:
        query = query.filter(Attempt.quiz_id == quiz_id)
    
    if chapter_id:
        query = query.filter(Quiz.chapter_id == chapter_id)
    
    if attempt_id:
        query = query.filter(Attempt.id == attempt_id)
    
    if subject_id:
        query = query.filter(Chapter.subject_id == subject_id)
    
    # Apply search filter if provided
    if search:
        query = query.filter(Quiz.name.ilike(f'%{search}%'))
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(desc(getattr(Attempt, sort_by)))
    else:
        query = query.order_by(getattr(Attempt, sort_by))
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    attempts = pagination.items
    
    # Prepare response with detailed attempt information
    attempts_data = []
    for attempt in attempts:
        attempt_dict = attempt.to_dict()
        # Add quiz details
        attempt_dict['quiz'] = {
            'id': attempt.quiz.id,
            'name': attempt.quiz.name,
            'date_of_quiz': attempt.quiz.date_of_quiz.isoformat(),
            'duration': attempt.quiz.duration,
            'total_questions': attempt.quiz.total_questions,
            'total_score': attempt.quiz.total_score,
            'chapter': {
                'id': attempt.quiz.chapter.id,
                'name': attempt.quiz.chapter.name,
                'description': attempt.quiz.chapter.description,
                'subject': {
                    'id': attempt.quiz.chapter.subject.id,
                    'name': attempt.quiz.chapter.subject.name,
                    'description': attempt.quiz.chapter.subject.description
                }
            }
        }
        attempts_data.append(attempt_dict)
    
    # Prepare response
    response = {
        'attempts': attempts_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total
        }
    }
    
    return jsonify(response)

@quiz_attempts.route('/attempts/<int:attempt_id>/responses', methods=['GET'])
@jwt_required()
def get_attempt_responses(attempt_id):
    user_id = int(get_jwt_identity())
    
    # Get attempt and verify ownership
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all responses for this attempt with their questions
    responses = Response.query.filter_by(attempt_id=attempt_id).all()
    
    # Prepare detailed response data
    responses_data = []
    for response in responses:
        question = response.question
        response_dict = {
            'id': response.id,
            'is_attempted': response.is_attempted,
            'is_correct': response.is_correct,
            'created_at': response.created_at.isoformat(),
            'updated_at': response.updated_at.isoformat(),
            'question': {
                'id': question.id,
                'type': question.type,
                'created_at': question.created_at.isoformat(),
                'updated_at': question.updated_at.isoformat()
            }
        }
        
        # Add question details based on type
        if question.type == 'mcq':
            mcq_question = question.mcq_question
            response_dict['question']['details'] = {
                'id': mcq_question.id,
                'question_text': mcq_question.question_text,
                'correct_marks': mcq_question.correct_marks,
                'incorrect_marks': mcq_question.incorrect_marks,
                'options': [{
                    'id': option.id,
                    'text': option.text,
                    'is_correct': option.is_correct
                } for option in mcq_question.options]
            }
            
            # Find selected option
            selected_option = next(
                (opt for opt in mcq_question.options if opt.id == response.mcq_question_answer),
                None
            )
            
            response_dict['answer'] = {
                'option_id': response.mcq_question_answer,
                'selected_option': {
                    'id': selected_option.id,
                    'text': selected_option.text,
                    'is_correct': selected_option.is_correct
                } if selected_option else None
            }
        else:  # numeric question
            numeric_question = question.numeric_question
            response_dict['question']['details'] = {
                'id': numeric_question.id,
                'question_text': numeric_question.question_text,
                'answer_lower_bound': numeric_question.answer_lower_bound,
                'answer_upper_bound': numeric_question.answer_upper_bound,
                'correct_marks': numeric_question.correct_marks,
                'incorrect_marks': numeric_question.incorrect_marks
            }
            response_dict['answer'] = {
                'value': response.numeric_question_answer
            }
        
        responses_data.append(response_dict)
    
    # Prepare final response
    response = {
        'attempt_id': attempt_id,
        'quiz_id': attempt.quiz_id,
        'user_id': attempt.user_id,
        'status': attempt.status,
        'score': attempt.score,
        'started_at': attempt.started_at.isoformat(),
        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
        'quiz': attempt.quiz.to_dict(),  # Add quiz object using to_dict() method
        'responses': responses_data
    }
    
    return jsonify(response)

@quiz_attempts.route('/stats', methods=['GET'])
@jwt_required()
def get_student_stats():
    user_id = int(get_jwt_identity())
    current_time = datetime.now()
    
    # Get all attempts for the user
    attempts = Attempt.query.filter_by(user_id=user_id).all()
    
    # Calculate total quizzes attempted
    total_quizzes_attempted = len(attempts)
    
    # Calculate average score percentage
    total_score = sum(attempt.score for attempt in attempts)
    total_possible_score = sum(attempt.quiz.total_score for attempt in attempts)
    average_score_percentage = (total_score / total_possible_score * 100) if total_possible_score > 0 else 0
    
    # Get upcoming quizzes (quizzes that haven't started yet)
    upcoming_quizzes = Quiz.query.filter(
        Quiz.date_of_quiz > current_time
    ).order_by(Quiz.date_of_quiz).all()
    
    # Get recent performance (last 5 completed quizzes)
    recent_attempts = Attempt.query.filter(
        Attempt.user_id == user_id,
        Attempt.status == 'completed'
    ).order_by(Attempt.completed_at.desc()).limit(5).all()
    
    recent_performance = []
    for attempt in recent_attempts:
        score_percentage = (attempt.score / attempt.quiz.total_score * 100) if attempt.quiz.total_score > 0 else 0
        recent_performance.append({
            'quiz_name': attempt.quiz.name,
            'date': attempt.completed_at.isoformat(),
            'score_percentage': score_percentage
        })
    
    # Calculate subject-wise performance
    subject_performance = {}
    for attempt in attempts:
        if attempt.status == 'completed':
            subject = attempt.quiz.chapter.subject
            if subject.id not in subject_performance:
                subject_performance[subject.id] = {
                    'subject_name': subject.name,
                    'total_score': 0,
                    'total_possible_score': 0,
                    'quizzes_taken': 0
                }
            
            subject_performance[subject.id]['total_score'] += attempt.score
            subject_performance[subject.id]['total_possible_score'] += attempt.quiz.total_score
            subject_performance[subject.id]['quizzes_taken'] += 1
    
    # Convert subject performance to list and calculate percentages
    subject_performance_list = []
    for subject_id, data in subject_performance.items():
        average_percentage = (data['total_score'] / data['total_possible_score'] * 100) if data['total_possible_score'] > 0 else 0
        subject_performance_list.append({
            'subject_name': data['subject_name'],
            'average_percentage': average_percentage,
            'quizzes_taken': data['quizzes_taken']
        })
    
    # Prepare final response
    response = {
        'total_quizzes_attempted': total_quizzes_attempted,
        'average_score_percentage': average_score_percentage,
        'total_upcoming_quizzes': len(upcoming_quizzes),
        'recent_performance': recent_performance,
        'subject_performance': subject_performance_list
    }
    
    return jsonify(response)

@quiz_attempts.route('/quizzes/<int:quiz_id>/report/csv', methods=['GET'])
@jwt_required()
def get_quiz_attempt_csv(quiz_id):
    user_id = get_jwt_identity()
    
    # Get the quiz attempt for this user
    attempt = Attempt.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
    if not attempt:
        return jsonify({'error': 'You have not attempted this quiz'}), 400
        
    if attempt.status != 'completed':
        return jsonify({'error': 'Quiz attempt is not completed'}), 400
    
    # Get quiz details
    quiz = attempt.quiz
    chapter = quiz.chapter
    subject = chapter.subject
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename using quiz name, user id and timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"quiz_report_{quiz.name.replace(' ', '_')}_{user_id}_{timestamp}.csv"
    filepath = os.path.join(reports_dir, filename)
    
    # Generate CSV content
    csv_content = []
    
    # Header row
    header = "Quiz name,Subject name,Chapter name,Total Questions,Score,Max score,Attempted on\n"
    csv_content.append(header)
    
    # Quiz summary row
    summary = f"{quiz.name},{subject.name},{chapter.name},{quiz.total_questions},{attempt.score},{quiz.total_score},{attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    csv_content.append(summary)
    
    # Empty row
    csv_content.append("\n")
    
    # Responses header
    responses_header = "Qn No,Question text,Question type,Your answer,Correct answer\n"
    csv_content.append(responses_header)
    
    # Get all responses sorted by question ID
    responses = Response.query.filter_by(attempt_id=attempt.id).join(Question).order_by(Question.id).all()
    
    for idx, response in enumerate(responses, 1):
        question = response.question
        question_text = question.mcq_question.question_text if question.type == 'mcq' else question.numeric_question.question_text
        question_type = question.type
        
        if question.type == 'mcq':
            your_answer = response.selected_option.text if response.selected_option else "Not attempted"
            correct_option = next((opt.text for opt in question.mcq_question.options if opt.is_correct), "")
            correct_answer = correct_option
        else:  # numeric
            your_answer = str(response.numeric_question_answer) if response.numeric_question_answer is not None else "Not attempted"
            correct_answer = f"Range: {question.numeric_question.answer_lower_bound} to {question.numeric_question.answer_upper_bound}"
        
        # Escape any commas in text fields
        question_text = f'"{question_text}"' if ',' in question_text else question_text
        your_answer = f'"{your_answer}"' if ',' in str(your_answer) else your_answer
        correct_answer = f'"{correct_answer}"' if ',' in str(correct_answer) else correct_answer
        
        response_row = f"{idx},{question_text},{question_type},{your_answer},{correct_answer}\n"
        csv_content.append(response_row)
    
    # Write to file
    with open(filepath, 'w', newline='') as f:
        f.write("".join(csv_content))
    
    # Send email asynchronously using Celery
    task = send_quiz_report_email.delay(quiz_id, user_id, filepath)
    
    return jsonify({
        'message': 'Quiz report is being generated and will be sent to your email shortly',
        'task_id': task.id
    }) 