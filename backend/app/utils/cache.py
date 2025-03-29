import redis
import json
from functools import wraps
from flask import current_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Redis client
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=int(os.getenv('REDIS_DB', 0)),
    decode_responses=True  # Automatically decode responses to strings
)

def cache_key_prefix(prefix):
    """Decorator to add a prefix to the cache key"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return f"{prefix}:{func(*args, **kwargs)}"
        return wrapper
    return decorator

@cache_key_prefix('profile')
def get_profile_cache_key(user_id):
    """Generate cache key for user profile"""
    return f"user:{user_id}"

@cache_key_prefix('question')
def get_question_cache_key(question_id):
    """Generate cache key for student question"""
    return f"question:{question_id}"

@cache_key_prefix('quizzes')
def get_quizzes_cache_key(page, per_page, sort_by, sort, date_lb, date_ub, chapter_id, subject_id, name):
    """Generate cache key for student quizzes list"""
    return f"page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort:{sort}:date_lb:{date_lb}:date_ub:{date_ub}:chapter:{chapter_id}:subject:{subject_id}:name:{name}"

def cache_get(key):
    """Get value from cache"""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        current_app.logger.error(f"Redis GET Error: {str(e)}")
        return None

def cache_set(key, value, timeout=300):  # Default timeout: 5 minutes
    """Set value in cache with timeout"""
    try:
        redis_client.setex(key, timeout, json.dumps(value))
        return True
    except Exception as e:
        current_app.logger.error(f"Redis SET Error: {str(e)}")
        return False

def cache_delete(key):
    """Delete value from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        current_app.logger.error(f"Redis DELETE Error: {str(e)}")
        return False

def cache_delete_pattern(pattern):
    """Delete all keys matching pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        current_app.logger.error(f"Redis DELETE Pattern Error: {str(e)}")
        return False

def clear_profile_cache(user_id):
    """Clear user profile cache"""
    key = get_profile_cache_key(user_id)
    return cache_delete(key)

def clear_question_cache(question_id):
    """Clear student question cache"""
    key = get_question_cache_key(question_id)
    return cache_delete(key)

def clear_quizzes_cache():
    """Clear all student quizzes cache"""
    return cache_delete_pattern("quizzes:*") 