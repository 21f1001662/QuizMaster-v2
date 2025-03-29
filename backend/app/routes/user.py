from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from app.utils.helpers import admin_required
from datetime import datetime
from sqlalchemy import or_
from app.utils.cache import cache_get, cache_set, clear_profile_cache, get_profile_cache_key

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = int(get_jwt_identity())
    
    # Try to get from cache
    cache_key = get_profile_cache_key(current_user_id)
    cached_data = cache_get(cache_key)
    if cached_data:
        return jsonify(cached_data), 200
    
    # If not in cache, get from database
    user = User.query.get_or_404(current_user_id)
    user_data = user.to_dict()
    
    # Store in cache
    cache_set(cache_key, user_data)
    
    return jsonify(user_data), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'dob' in data:
        try:
            user.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    if 'qualification' in data:
        user.qualification = data['qualification']
    
    db.session.commit()
    
    # Clear user's profile cache
    clear_profile_cache(current_user_id)
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    # Get query parameters
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'created_at')  # Default sort by creation date
    sort = request.args.get('sort', 'desc').lower()  # Default descending order
    
    # Validate sort_by parameter
    valid_sort_fields = ['username', 'full_name', 'dob', 'qualification', 'is_admin', 'created_at']
    if sort_by not in valid_sort_fields:
        return jsonify({'message': f'Invalid sort_by. Must be one of: {", ".join(valid_sort_fields)}'}), 400
    
    # Validate sort direction
    if sort not in ['asc', 'desc']:
        return jsonify({'message': 'Invalid sort. Must be either "asc" or "desc"'}), 400
    
    # Base query
    query = User.query
    
    # Apply search filter if search parameter is provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.full_name.ilike(search_term)
            )
        )
    
    # Apply sorting
    sort_column = getattr(User, sort_by)
    if sort == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'sort_by': sort_by,
        'sort': sort
    }), 200 