from functools import wraps
from flask import flash, redirect, session,request,jsonify
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first")
            return redirect('/LoginRegister')
        return f(*args, **kwargs)
    return decorated_function
def ajax_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "status": "login_required"
            }), 401
        return f(*args, **kwargs)
    return wrapper