from flask import Blueprint, render_template, request, redirect, session, flash
from functools import wraps
from database.db import get_db_connection
conn, cursor = get_db_connection()
from auth.encryption import verify_password

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return wrapper
@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM admins WHERE username=%s",
            (username,)
        )
        admin = cursor.fetchone()

        if admin and verify_password(admin["password"], password):
            session["admin_id"] = admin["admin_id"]
            return redirect("/admin/dashboard")

        flash("Invalid credentials")

    return render_template("admin/login.html")
from auth.encryption import encrypt_password

@admin_bp.route("/register", methods=["GET","POST"])
def admin_register():

    cursor.execute("SELECT COUNT(*) AS total FROM admins")
    if cursor.fetchone()["total"] > 0:
        return "Admin already exists"

    if request.method == "POST":
        username = request.form["username"]
        password = encrypt_password(request.form["password"])

        cursor.execute(
            "INSERT INTO admins (username,password) VALUES (%s,%s)",
            (username,password)
        )
        conn.commit()

        return redirect("/admin/login")

    return render_template("admin/register.html")
@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin_id", None)
    flash("Admin logged out")
    return redirect("/admin/login")
@admin_bp.route("/users")
@admin_login_required
def users():

    cursor.execute("""
        SELECT id, name, email, phone
        FROM users
        ORDER BY id DESC
    """)
    users = cursor.fetchall()

    return render_template("admin/users.html", users=users)
@admin_bp.route("/delete-user/<int:user_id>")
@admin_login_required
def delete_user(user_id):

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()

    flash("User deleted successfully")
    return redirect("/admin/users")
@admin_bp.route("/update-user/<int:user_id>", methods=["POST"])
@admin_login_required
def update_user(user_id):

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")

    cursor.execute("""
        UPDATE users
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
    """, (name, email, phone, user_id))

    conn.commit()

    flash("User updated successfully")
    return redirect("/admin/users")
@admin_bp.route("/login-activity")
@admin_login_required
def login_activity():

    cursor.execute("""
        SELECT 
            l.id,
            u.name,
            l.ip_address,
            l.city,
            l.country,
            l.browser,
            l.os,
            l.device_type,
            l.login_time,
            l.logout_time,
            l.session_duration_seconds
        FROM login_activity l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.login_time DESC
    """)

    activities = cursor.fetchall()

    return render_template(
        "admin/login_activity.html",
        activities=activities
    )
@admin_bp.route("/delete-activity/<int:activity_id>")
@admin_login_required
def delete_activity(activity_id):

    cursor.execute(
        "DELETE FROM login_activity WHERE id=%s",
        (activity_id,)
    )
    conn.commit()

    flash("Activity deleted")
    return redirect("/admin/login-activity")
@admin_bp.route("/dashboard")
@admin_login_required
def dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    orders_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM products")
    products_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    users_count = cursor.fetchone()["total"]

    return render_template(
        "admin/dashboard.html",
        orders_count=orders_count,
        products_count=products_count,
        users_count=users_count
    )
@admin_bp.route("/products")
@admin_login_required
def manage_products():

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return render_template("admin/products.html", products=products)
@admin_bp.route("/product/delete/<int:p_id>")
@admin_login_required
def delete_product(p_id):

    cursor.execute("DELETE FROM products WHERE p_id=%s", (p_id,))
    conn.commit()

    return redirect("/admin/products")
@admin_bp.route("/orders")
@admin_login_required
def manage_orders():

    cursor.execute("""
        SELECT o.order_id, u.name, o.total_amount,
               o.payment_method, o.payment_status,
               o.created_at
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.order_id DESC
    """)

    orders = cursor.fetchall()

    return render_template("admin/orders.html", orders=orders)