import functools
from flask import session, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)

def login_required(view):
    """Decorator to protect candidate-only routes"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Authentication required. Please log in.'}), 401
            flash('Please log in as a candidate to access this page.', 'warning')
            return redirect(url_for('candidate_login', next=request.path))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """Decorator to protect admin-only routes"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'admin_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Administrator access required.'}), 403
            flash('Please log in with Administrator credentials to continue.', 'danger')
            return redirect(url_for('admin_login', next=request.path))
        return view(**kwargs)
    return wrapped_view
