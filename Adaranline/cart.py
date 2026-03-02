from flask import Blueprint, redirect, flash, session,render_template,jsonify
from auth.mandatelogin import login_required,ajax_login_required
from database.db import conn, cursor
cart_bp = Blueprint("cart", __name__)
@cart_bp.route("/add-to-cart/<int:product_id>", methods=["POST"])
@ajax_login_required
def add_to_cart(product_id):
    if "user_id" not in session:
        flash("Please login to add items to cart")
        return redirect("/LoginRegister")
    cursor.execute("""
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE
        quantity = quantity + 1
    """, (session["user_id"], product_id))
    conn.commit()
    flash("Item added to cart")
    return jsonify({"status": "success"})

@cart_bp.route("/buy-now/<int:product_id>", methods=["POST"])
@login_required
def buy_now(product_id):

    if "user_id" not in session:
        flash("Login required")
        return redirect("/LoginRegister")

    cursor.execute("""
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE
        quantity = 1
    """, (session["user_id"], product_id))

    conn.commit()

    return redirect("/checkout")
@cart_bp.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect("/LoginRegister")

    cursor.execute("""
        SELECT c.cart_id, p.part_name, p.price, c.quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.p_id
        WHERE c.user_id = %s
    """, (session["user_id"],))

    items = cursor.fetchall()
    total = sum(i["price"] * i["quantity"] for i in items)

    return render_template("cart.html", items=items, total=total)
@cart_bp.route("/cart/update/<int:cart_id>/<action>")
def update_cart(cart_id, action):

    if action == "plus":
        cursor.execute(
            "UPDATE cart_items SET quantity = quantity + 1 WHERE cart_id=%s",
            (cart_id,)
        )
    else:
        cursor.execute(
            "UPDATE cart_items SET quantity = quantity - 1 WHERE cart_id=%s AND quantity > 1",
            (cart_id,)
        )

    conn.commit()
    return redirect("/cart")

