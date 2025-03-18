from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app import db
from app.utils.helpers import admin_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    return jsonify(user.to_dict()), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = int(get_jwt_identity())
    user = User.query.get_or_404(current_user_id)
    
    data = request.get_json()
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'dob' in data:
        user.dob = data['dob']
    if 'qualification' in data:
        user.qualification = data['qualification']
    
    db.session.commit()
    return jsonify(user.to_dict()), 200

@user_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200 