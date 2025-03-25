from flask import Blueprint, request, jsonify
from app.models.quiz import Quiz, Question, Attempt, Response
from app.models.user import User
from app import db
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity

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
    
    # Check if quiz is currently active
    current_time = datetime.utcnow()
    print(current_time)
    if current_time < quiz.date_of_quiz:
        return jsonify({'error': 'Quiz has not started yet'}), 400
    
    if current_time > quiz.date_of_quiz + timedelta(minutes=quiz.duration):
        return jsonify({'error': 'Quiz has ended'}), 400
    
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
    if datetime.utcnow() > quiz.date_of_quiz + timedelta(minutes=quiz.duration):
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
    attempt.completed_at = datetime.utcnow()
    
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
    current_time = datetime.utcnow()
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

@quiz_attempts.route('/attempts/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt_details(attempt_id):
    user_id = int(get_jwt_identity())
    
    # Get attempt and verify ownership
    attempt = Attempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(attempt.to_dict()) 