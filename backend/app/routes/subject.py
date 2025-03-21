from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.subject import Subject, Chapter
from app import db
from app.utils.helpers import admin_required
from sqlalchemy import or_

subject_bp = Blueprint('subject', __name__)

# Subject Routes
@subject_bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required
def create_subject():
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Subject name is required'}), 400
        
    subject = Subject(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify(subject.to_dict()), 201

@subject_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    subject_id = request.args.get('subject_id', type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query
    query = Subject.query
    
    # If subject_id is provided, filter for specific subject
    if subject_id:
        query = query.filter_by(id=subject_id)
    
    # Apply search filter if search parameter is provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Subject.name.ilike(search_term),
                Subject.description.ilike(search_term)
            )
        )
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Return consistent response format
    return jsonify({
        'subjects': [subject.to_dict() for subject in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@subject_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    
    if 'name' in data:
        subject.name = data['name']
    if 'description' in data:
        subject.description = data['description']
    
    db.session.commit()
    return jsonify(subject.to_dict()), 200

@subject_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'message': 'Subject deleted successfully'}), 200

# Chapter Routes
@subject_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
@admin_required
def create_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'message': 'Chapter name is required'}), 400
        
    chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        subject_id=subject_id
    )
    
    db.session.add(chapter)
    db.session.commit()
    
    return jsonify(chapter.to_dict()), 201

@subject_bp.route('/chapters', methods=['GET'])
@jwt_required()
def get_chapters():
    chapter_id = request.args.get('chapter_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Base query
    query = Chapter.query
    
    # Apply filters if provided
    if chapter_id:
        query = query.filter_by(id=chapter_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Return consistent response format
    return jsonify({
        'chapters': [chapter.to_dict() for chapter in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@subject_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    
    if 'name' in data:
        chapter.name = data['name']
    if 'description' in data:
        chapter.description = data['description']
    
    db.session.commit()
    return jsonify(chapter.to_dict()), 200

@subject_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({'message': 'Chapter deleted successfully'}), 200 