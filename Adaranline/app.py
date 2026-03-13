from flask import Flask, render_template, redirect, request, flash, send_from_directory, session ,jsonify
from cart import cart_bp
import re
from admin import admin_bp
from flask_mail import Mail, Message
import random
import uuid
from auth.encryption import encrypt_password, verify_password
from auth.mandatelogin import login_required
from mysql.connector import Error
from database.db import get_db_connection
conn, cursor = get_db_connection()
import requests ,jwt          
import datetime
from user_agents import parse
from functools import wraps
import razorpay
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(cart_bp)
app.register_blueprint(admin_bp)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)
def generate_otp():
    return str(random.randint(100000, 999999))
YEARS = list(range(2026, 1999, -1))
ENGINE_TYPES = ["Petrol", "Diesel", "Hybrid", "Electric"]
PART_CATEGORIES = {
    "METAL / ALLOY": [
        "Engine Block",
        "Cylinder Head",
        "Pistons",
        "Crankshaft",
        "Connecting Rods",
        "Transmission Housing",
        "Gear Sets",
        "Chassis / Frame",
        "Brake Discs",
        "Exhaust Manifold",
        "Alloy Wheels",
        "Suspension Arms"
    ],
    "RUBBER / ELASTOMER PARTS": [
        "Tyres",
        "Inner Tubes",
        "Engine Mounts",
        "Suspension Bushings",
        "CV Joint Boots",
        "Brake Hoses",
        "Radiator Hoses",
        "Fuel Hoses",
        "Door Weather Strips",
        "Wiper Blades",
        "Pedal Pads",
        "Anti-Vibration Mounts"
    ],
    "PLASTIC / POLYMER PARTS": [
        "Dashboard",
        "Front / Rear Bumpers",
        "Headlamp Housing",
        "Tail Lamp Housing",
        "Interior Trim Panels",
        "Door Handles",
        "Air Intake Manifold",
        "Fuse Box Cover",
        "Mirror Housing",
        "Front Grille",
        "Washer Fluid Reservoir"
    ],
    "GLASS PARTS": [
        "Windshield",
        "Rear Glass",
        "Door Glass (Front / Rear)",
        "Quarter Glass",
        "Sunroof Glass",
        "Headlamp Lens",
        "Tail Lamp Lens",
        "Fog Lamp Glass",
        "Instrument Cluster Glass"
    ],
    "ELECTRICAL / ELECTRONIC PARTS": [
        "Battery",
        "Alternator",
        "Starter Motor",
        "ECU",
        "Wiring Harness",
        "Spark Plugs",
        "Sensors (O₂, Speed, Temp)",
        "Relays",
        "Fuses",
        "Power Window Motor",
        "Horn",
        "Ignition Coil"
    ],
    "INTERIOR / FABRIC / FOAM": [
        "Seat Upholstery",
        "Seat Foam",
        "Roof Lining",
        "Door Fabric Panels",
        "Floor Carpets",
        "Seat Belts",
        "Armrest Padding",
        "Sun Visors",
        "Boot Lining",
        "Steering Wheel Cover"
    ],
    "OTHERS": ["Please Specify"]
}

VEHICLE_DATA = {
    "SUV": {
        "Toyota": ["LC 300","Fortuner","Hilux","Innova"],
        "Mercedes":["GLA","GLB","GLC","GLS","G-63"],
       "Jeep":["Compass","Wrangler","Grand Cherokee","Meridian"],
       "Ford":["Everest","Rapter","EcoSport"],
        "Land Rover": ["Defender", "Range Rover Sport","Range Rover Discovery","Range Rover Autobiograpgy","Range Rover Evoque"]
    },
    "Sedan": {
             "Toyota": [
        "Corolla",
        "Corolla Hybrid",
        "Camry (Hybrid)",
        "Crown (Hybrid)",
        "Mirai (Hydrogen Fuel Cell)",
        "Yaris (Global markets)",
        "Belta (Global markets)"
    ],
    "BMW": [
        "2 Series Gran Coupé",
        "3 Series Sedan (New 'G50' generation)",
        "i3 (All-electric sedan, Neue Klasse)",
        "4 Series Gran Coupé / i4",
        "5 Series Sedan / i5",
        "7 Series Sedan / i7 (Facelift 'LCI' models)",
        "ALPINA B7 / B8 Gran Coupe",
        "M3",
        "M5"
    ],
    "Honda": [
        "Civic Sedan",
        "Civic Sedan Hybrid",
        "Civic Si",
        "Accord",
        "Accord Hybrid",
        "City (Global markets, facelifted 2026)",
        "Amaze (Global markets)",
        "0 Series Saloon (New all-electric sedan)"
    ],
    "Mercedes-Benz": [
        "CLA / CLA Electric (New 2026 model)",
        "C-Class Sedan (Facelifted 2026)",
        "E-Class Sedan (Facelifted 2026)",
        "S-Class Sedan",
        "EQE Sedan",
        "EQS Sedan",
        "Mercedes-AMG performance variants"
    ],
    "Audi": [
        "A3 Sedan",
        "A4 Sedan",
        "A6 Sedan / A6 e-tron (Electric)",
        "A8 Sedan",
        "e-tron GT / RS e-tron GT",
        "S and RS performance variants"
    ],
    "Dodge": [
        "Charger Daytona (All-electric sedan)",
        "Charger Sixpack (Twin-turbo Hurricane engine sedan)"
    ]

    },
    "Hatchback": {
           "Volkswagen": [
        "Polo (Global)",
        "Golf (GTI and R variants)",
        "ID.3 (All-electric)",
        "ID.2all (New entry-level EV)",
        "Tera (New for 2026)"
    ],
    "MINI": [
        "Cooper 2-Door (Petrol & SE Electric)",
        "Cooper 4-Door",
        "Cooper S / JCW (High performance)",
        "Aceman (All-electric crossover/hatch)"
    ],
    "Mercedes-Benz": [
        "A-Class Hatchback",
        "Mercedes-AMG A 35 / A 45 S 4MATIC+",
        "CLA Shooting Brake (Coupé-style hatch)",
        "B-Class (Sports Tourer/MPV style)"
    ],
    "Audi": [
        "A1 Sportback",
        "A3 Sportback",
        "S3 / RS 3 Sportback (High performance)",
        "A6 e-tron Sportback (Electric executive hatch)"
    ],
    "BMW": [
        "1 Series Sedan (Hatchback in global markets)",
        "i1 (All-electric compact hatch expected)",
        "2 Series Active Tourer (Small MPV/Hatch style)"
    ],
    "Suzuki": [
        "Swift / Swift Sport",
        "Baleno",
        "Wagon R / Wagon R Electric (Launching early 2026)",
        "Alto / Celerio",
        "Ignis (Compact urban hatch)"
    ],
    "Skoda": [
        "Fabia",
        "Scala",
        "Elroq (New electric model, compact hatch/SUV style)",
        "Octavia Hatch (Fastback style)"
    ],
    "Toyota": [
        "Yaris / GR Yaris",
        "Corolla Hatchback",
        "Aygo X (Urban crossover hatch)",
        "Glanza (India-specific model)",
        "Prius (Hybrid hatch)"
    ]
    },
    "Aggressive": {
        "Ferrari": [
        "12Cilindri (Naturally aspirated 6.5L V12)",
        "F80 (V6 Hybrid hypercar, successor to LaFerrari)",
        "849 Testarossa (Upcoming 2026 V8 Hybrid flagship)",
        "296 GTB / GTS (V6 Hybrid)",
        "SF90 Stradale / XX (V8 Hybrid)",
        "Purosangue (V12-powered high-performance utility)",
        "Roma / Roma Spider (Twin-turbo V8 GT)"
    ],
    "Lamborghini": [
        "Revuelto / Revuelto Roadster (V12 Plug-in Hybrid)",
        "Temerario (New-for-2026 Twin-turbo V8 Hybrid)",
        "Urus SE (V8 Hybrid performance SUV)",
        "Huracán STO / Tecnica (Final NA V10 units)"
    ],
    "Bugatti": [
        "Tourbillon (All-new 8.3L V16 Naturally Aspirated Hybrid)",
        "Bolide (Quad-turbo W16, track-only)",
        "Mistral (Quad-turbo W16, final open-top model)"
    ],
    "McLaren": [
        "W1 (1,275hp V8 Hybrid hypercar)",
        "750S / 750S Spider (Twin-turbo V8)",
        "Artura / Artura Spider (V6 Hybrid)",
        "GTS (Twin-turbo V8 grand tourer)"
    ],
    "Porsche": [
        "911 GT2 RS (992-gen flagship, high-performance ICE)",
        "911 GT3 / GT3 RS (Facelifted 992.2 naturally aspirated flat-six)",
        "911 Turbo S (Facelifted 3.7L twin-turbo flat-six)",
        "718 Cayman GT4 RS (Final petrol-powered mid-engine models)"
    ],
    "Aston Martin": [
        "Valkyrie / Valkyrie Spider (6.5L NA V12 Hybrid)",
        "Vanquish (New 2026 5.2L V12 flagship)",
        "Valhalla (V8 Mid-engine PHEV supercar)",
        "Valiant (Limited V12 track-focused special)",
        "Vantage / Vantage S (Twin-turbo V8)"
    ],
    "Pagani": [
        "Utopia / Utopia Roadster (6.0L AMG-sourced twin-turbo V12)",
        "Huayra Imola Roadster (V12 special series)",
        "Huayra Codalunga (Bespoke long-tail V12)"
    ],
    "Koenigsegg": [
        "Jesko / Jesko Absolut (Twin-turbo V8, 1,600+ hp)",
        "Gemera (HV8 version with twin-turbo V8 Hybrid)",
        "CC850 (Reimagined manual V8 hypercar)"
    ],
    "Gordon Murray Automotive": [
        "T.50 / T.50s (Naturally aspirated 3.9L V12)",
        "T.33 / T.33 Spider (Naturally aspirated V12 with manual option)"
    ],
    "Hennessey": [
        "Venom F5 / F5 Roadster (6.6L twin-turbo V8 'Fury')",
        "Venom F5 Revolution (Track-focused variant)"
    ],
    "Chevrolet": [
        "Corvette ZR1 (New 2026 1,000hp+ twin-turbo V8 flagship)",
        "Corvette Z06 (Naturally aspirated flat-plane crank V8)",
        "Corvette E-Ray (V8 Hybrid AWD)"
    ]
    },
    "Others":{
        "XYZ":["Please Specify"]
        }
}
def get_client_ip():
     
    if "X-Forwarded-For" in request.headers:
        ip = request.headers["X-Forwarded-For"].split(",")[0].strip()
    else:
        ip = request.remote_addr
    return ip or "0.0.0.0"
def get_ip_location(ip):
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=2)
        data = resp.json()
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
        }
    except Exception:
        return {"city": None, "region": None, "country": None}
def parse_user_agent(ua_string):
    ua = parse(ua_string)
    browser = ua.browser.family       
    browser_version = ua.browser.version_string
    os = ua.os.family                  
    os_version = ua.os.version_string
    device_type = "Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC"
    return browser, browser_version, os, os_version, device_type
@app.route("/")
def home():
    
    if not session.get("alert_shown"):
        flash("Drop a Gear and Disappear")
        session["alert_shown"] = True
    return render_template("homep.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/content")
def content():
    return render_template("content.html")
@app.route("/service")
def service():
    return render_template("servicepart.html")
def get_greeting():
    hour = datetime.datetime.utcnow().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"
@app.route("/LoginRegister", methods=['GET', 'POST'])
def LoginRegister():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user and verify_password(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            ip = get_client_ip()
            loc = get_ip_location(ip)
            user_agent = request.headers.get("User-Agent", "")
            login_time = datetime.datetime.utcnow()   
            user_agent = request.headers.get("User-Agent", "")
            browser, browser_version, os_name, os_version, device_type = parse_user_agent(user_agent)
            cursor.execute(
                """
                INSERT INTO login_activity
                (user_id, ip_address, city, region, country, user_agent,
                browser, browser_version, os, os_version, device_type, login_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user["id"],
                    ip,
                    loc["city"], loc["region"], loc["country"],
                    user_agent,
                    browser, browser_version, os_name, os_version, device_type,
                    login_time
                )
                )
            conn.commit()
            session["login_activity_id"] = cursor.lastrowid
            session["login_time_iso"] = login_time.isoformat()
            flash("Login Successful")
            return redirect('/')
        else:
            flash("Invalid credentials")
            return redirect('/LoginRegister')
    return render_template("login.html")
@app.route("/logout")
def logout():
    activity_id = session.get("login_activity_id")
    login_time_iso = session.get("login_time_iso")

    if activity_id and login_time_iso:
        logout_time = datetime.datetime.utcnow()
        try:
            login_time = datetime.fromisoformat(login_time_iso)
            duration_seconds = int((logout_time - login_time).total_seconds())
        except Exception:
            duration_seconds = None

        cursor.execute(
            """
            UPDATE login_activity
            SET logout_time = %s,
                session_duration_seconds = %s
            WHERE id = %s
            """,
            (logout_time, duration_seconds, activity_id)
        )
        conn.commit()
     

    session.clear()
    flash("Logged out successfully")
    return redirect("/")
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            if len(password) < 8:
                flash("Password must be at least 8 characters")
                return redirect('/register')
            password = encrypt_password(request.form.get('password'))
            if not re.match(r"^\d{10}$", phone):
                flash("Phone number must be 10 digits")
                return redirect('/register')
            phone = request.form.get('phone')
            
            print(phone)
            cursor.execute(
                "INSERT INTO users (name, email, password, phone) VALUES (%s, %s, %s, %s)",
                (name, email, password, phone)
            )
            conn.commit()
            flash("Registration successful, please login")
            return redirect('/LoginRegister')
        except Error as e:
            print("MYSQL ERROR:", e)
            flash("Phone number already registered")
            return redirect('/register')
    return render_template('register.html')
@app.route("/check-email", methods=["POST"])
def check_email():
    email = request.json.get("email")

    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    return {"exists": bool(user)}
@app.route("/forgot-password", methods=["GET","POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()

        if not user:
            flash("Email not registered")
            return redirect("/forgot-password")

        otp = generate_otp()
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

        cursor.execute("""
            INSERT INTO email_otp (email, otp, purpose, expires_at)
            VALUES (%s,%s,'reset_password',%s)
        """,(email, otp, expiry))
        conn.commit()

        msg = Message(
        f"ADRANALINE GARAGES OTP #{uuid.uuid4().hex[:6]}",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email])
        msg.body = f"Your OTP is {otp}. Valid for 5 minutes."
        mail.send(msg)
        session["reset_email"] = email
        flash("OTP sent to your email")
        return redirect("/verify-otp")

    return render_template("forgot_password.html")
@app.route("/verify-otp", methods=["GET","POST"])
def verify_otp():
    if request.method == "POST":
        user_otp = request.form["otp"]
        email = session.get("reset_email")

        cursor.execute("""
            SELECT * FROM email_otp
            WHERE email=%s AND otp=%s AND purpose='reset_password'
            AND is_used=FALSE
            AND expires_at > %s
        """,(email,user_otp,datetime.datetime.utcnow()))

        record = cursor.fetchone()

        if not record:
            flash("Invalid or Expired OTP")
            return redirect("/verify-otp")

        cursor.execute(
            "UPDATE email_otp SET is_used=TRUE WHERE id=%s",
            (record["id"],)
        )
        conn.commit()

        session["otp_verified"] = True
        return redirect("/reset-password")

    return render_template("verify_otp.html")
@app.route("/reset-password", methods=["GET","POST"])
def reset_password():
    if not session.get("otp_verified"):
        return redirect("/forgot-password")

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("Passwords do not match")
            return redirect("/reset-password")

        encrypted = encrypt_password(new_password)
        email = session["reset_email"]

        cursor.execute(
            "UPDATE users SET password=%s WHERE email=%s",
            (encrypted,email)
        )
        conn.commit()

        session.clear()
        flash("Password updated successfully")
        return redirect("/LoginRegister")

    return render_template("reset_password.html")
@app.route("/addresses", methods=["GET", "POST"])
@login_required
def addresses():
    if request.method == "POST":
        cursor.execute("""
            INSERT INTO user_addresses
            (user_id, full_name, phone,
             address_line1, address_line2,
             city, state, pincode)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session["user_id"],
            request.form["full_name"],
            request.form["phone"],
            request.form["line1"],
            request.form["line2"],
            request.form["city"],
            request.form["state"],
            request.form["pincode"],
        ))
        conn.commit()
        flash("Address added")
        return redirect("/addresses")

    cursor.execute(
        "SELECT * FROM user_addresses WHERE user_id=%s",
        (session["user_id"],)
    )
    addresses = cursor.fetchall()

    return render_template("addresses.html", addresses=addresses)

@app.context_processor
def cart_count():
    if "user_id" not in session:
        return dict(cart_count=0)

    cursor.execute(
        "SELECT SUM(quantity) AS total FROM cart_items WHERE user_id=%s",
        (session["user_id"],)
    )
    row = cursor.fetchone()
    return dict(cart_count=row["total"] or 0)

@app.route("/cart")
@login_required
def cart():

    cursor.execute("""
        SELECT
            c.cart_id,
            p.part_name,
            p.price,
            c.quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.p_id
        WHERE c.user_id = %s
    """, (session["user_id"],))

    items = cursor.fetchall()

    total = sum(i["price"] * i["quantity"] for i in items)

    return render_template("cart.html", items=items, total=total)
@app.route("/suv")
def suv():
    return render_template("suv.html")
@app.route("/sedan")
def sedan():
    return render_template("sedan.html")
@app.route("/hatchback")
def hatchback():
    return render_template("hatchback.html")
@app.route("/hatchbackparts")
def hatchbackparts():
    return render_template("hatchbackparts.html")
@app.route("/aggressive")
def aggressive():
    return render_template("aggresive.html")
@app.route("/MANYMORE")
def MANYMORE():
    return render_template("MANYMORE.html")
@app.route("/suv/Gwagon")
def GWagon():
    return render_template("GWagon.html")
@app.route("/defender")
def defender():
    return render_template("defender.html")
@app.route("/landcrusier")
def land_c():
    return render_template("landcruiser.html")
@app.route("/jeep")
def jeep():
    return render_template("jeep.html")
@app.route("/ford")
def ford():
    return render_template("ford.html")
@app.route("/range")
def range():
    return render_template("range.html")
def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "iat": datetime.datetime.utcnow(),
         
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, app.secret_key, algorithm="HS256") 

@app.route("/game")
@login_required
def game():
    token=generate_jwt(session['user_id'])
    return render_template("game.html",token=token)
@app.route("/api/score", methods=["POST"])
def save_score():
    score = request.json["score"]
    return {"status": "saved"}
@app.route("/checkout")
@login_required
def checkout():
    cursor.execute("""
        SELECT c.cart_id, p.part_name, p.price, c.quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.p_id
        WHERE c.user_id = %s
    """, (session["user_id"],))
    items = cursor.fetchall()
    if not items:
        flash("Your cart is empty")
        return redirect("/cart")
    cursor.execute(
        "SELECT * FROM user_addresses WHERE user_id=%s",
        (session["user_id"],)
    )
    addresses = cursor.fetchall()
    if not addresses:
        flash("Address not Found Please Add")
        return redirect("/addresses")
    total = sum(i["price"] * i["quantity"] for i in items)
    return render_template(
        "checkout.html",
        items=items,
        addresses=addresses,
        total=total
    )
def send_order_email(order_id):

    cursor.execute("""
        SELECT u.email, u.name, o.total_amount
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.order_id=%s
    """,(order_id,))

    data = cursor.fetchone()

    msg = Message(
        f"Order #{order_id} Confirmed",
        sender=app.config['MAIL_USERNAME'],
        recipients=[data["email"]]
    )

    msg.body = f"""
Hello {data['name']},

Your car part order #{order_id} is confirmed 🚗

Amount: ₹{data['total_amount']}

Thank you for shopping with us!
"""

    mail.send(msg)
@app.route("/place-order", methods=["POST"])
@login_required
def place_order():

    address_id = request.form.get("address_id")
    payment_method = request.form.get("payment_method")

    cursor.execute("""
        SELECT c.product_id, p.price, c.quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.p_id
        WHERE c.user_id=%s
    """, (session["user_id"],))

    cart_items = cursor.fetchall()

    if not cart_items:
        flash("Cart empty")
        return redirect("/cart")

    total = sum(i["price"] * i["quantity"] for i in cart_items)

    # SINGLE ORDER INSERT ONLY
    cursor.execute("""
        INSERT INTO orders
        (user_id, address_id, total_amount, payment_method, payment_status)
        VALUES (%s,%s,%s,%s,'pending')
    """, (session["user_id"], address_id, total, payment_method))

    conn.commit()
    order_id = cursor.lastrowid

    # order items + stock update
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items
            (order_id, product_id, price, quantity)
            VALUES (%s,%s,%s,%s)
        """, (
            order_id,
            item["product_id"],
            item["price"],
            item["quantity"]
        ))

        cursor.execute("""
            UPDATE products
            SET stock = stock - %s
            WHERE p_id = %s
        """, (item["quantity"], item["product_id"]))

    cursor.execute(
        "DELETE FROM cart_items WHERE user_id=%s",
        (session["user_id"],)
    )

    conn.commit()

    
    if payment_method == "COD":
        cursor.execute(
            "UPDATE orders SET payment_status='COD' WHERE order_id=%s",
            (order_id,)
        )
        conn.commit()
        send_order_email(order_id)

        # send_whatsapp_confirmation(order_id)  
        return redirect(f"/order-success/{order_id}")
    else:
        return redirect(f"/payment/{order_id}")
@app.route("/order-success/<int:order_id>")
@login_required
def order_success(order_id):
    cursor.execute("""
        SELECT * FROM orders
        WHERE order_id=%s AND user_id=%s
    """, (order_id, session["user_id"]))
    order = cursor.fetchone()
    return render_template("order_success.html", order=order)
@app.route("/buy-parts", methods=["GET", "POST"])
def buy_parts():
    vehicle_type = session.get("vehicle_type")
    brand = session.get("brand")
    model = session.get("model")
    part_category = session.get("part_category")
    brands = VEHICLE_DATA.get(vehicle_type, {}) if vehicle_type else {}
    models = brands.get(brand, []) if brand else []
    part_names = PART_CATEGORIES.get(part_category, []) if part_category else []
    return render_template(
        "buy.html",
        vehicle_types=VEHICLE_DATA.keys(),
        selected_vehicle=vehicle_type,
        brands=brands.keys(),
        selected_brand=brand,
        models=models,
        selected_model=model,
        years=YEARS,
        engines=ENGINE_TYPES,
        selected_year=session.get("year"),
        selected_engine=session.get("engine"),
        part_categories=PART_CATEGORIES.keys(),
        selected_part_category=part_category,
        part_names=part_names,
        selected_part_name=session.get("part_name"),
    )
@app.route("/api/clear", methods=["POST"])
def api_clear():
    for k in [
        "vehicle_type","brand","model","year",
        "engine","part_category","part_name","custom_part"
    ]:
        session.pop(k, None)
    return jsonify({"cleared": True})
@app.route("/api/selection", methods=["POST"])
def api_selection():
    data = request.get_json()
    allowed = {
        "vehicle_type",
        "brand",
        "model",
        "year",
        "engine",
        "part_category",
        "part_name",
        "custom_part"
    }
    key = data.get("key")
    value = data.get("value")
    if key in allowed:
        session[key] = value
    return jsonify({"status": "ok"})
@app.route("/products")
def products():
    required = [
        "vehicle_type", "brand", "model",
        "year", "engine", "part_category", "part_name"
    ]
    if not all(session.get(k) for k in required):
        flash("Incomplete selection")
        return redirect("/buy-parts")
    query = """
        SELECT p_id, part_name, price, stock, thumbnail
        FROM products
        WHERE vehicle_type=%s
          AND brand=%s
          AND model=%s
          AND year=%s
          AND engine=%s
          AND part_category=%s
          AND part_name=%s
    """
    cursor.execute(query, (
        session["vehicle_type"],
        session["brand"],
        session["model"],
        session["year"],
        session["engine"],
        session["part_category"],
        session["part_name"],
    ))
    items = cursor.fetchall()
    return render_template("products.html", products=items)
import json
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    cursor.execute("""
        SELECT p.p_id,p.price, p.stock,
               m.title, m.description, m.features,
               m.image_1, m.image_2, m.image_3,
               m.rating, m.review_count
        FROM products p
        JOIN master_pg_info m ON p.p_id = m.product_id
        WHERE p.p_id = %s
    """, (product_id,))
    product = cursor.fetchone()
    if not product:
        flash("Product not found")
        return redirect("/products")
    if product.get("features"):
        product["features"]=json.loads(product["features"])
    return render_template("product_detail.html", product=product)
@app.route("/clear-selection", methods=["POST"])
def clear_selection():
    keys_to_clear = [
        "vehicle_type",
        "brand",
        "model",
        "year",
        "engine",
        "part_category",
        "part_name",
        "custom_part"
    ]
    for key in keys_to_clear:
        session.pop(key, None)
    flash("Selection cleared")
    return redirect("/buy-parts")
import razorpay
client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))
@app.route("/payment/<int:order_id>")
@login_required
def payment(order_id):
    cursor.execute(
        "SELECT total_amount FROM orders WHERE order_id=%s",
        (order_id,)
    )
    order = cursor.fetchone()
    razorpay_order = client.order.create({
        "amount": int(order["total_amount"] * 100),
        "currency": "INR",
        "payment_capture": 1
    })
    return render_template(
    "payment.html",
    razorpay_key_id=os.environ.get("RAZORPAY_KEY_ID"),
    razorpay_order_id=razorpay_order["id"],
    amount=int(order["total_amount"] * 100),  
    order_id=order_id
)
@app.route("/payment-success", methods=["POST"])
@login_required
def payment_success():
    data = request.json
    order_id = data["order_id"]
    cursor.execute(
        "UPDATE orders SET payment_status='PAID' WHERE order_id=%s",
        (order_id,)
    )
    conn.commit()
    send_whatsapp_confirmation(order_id)
    return {"status": "ok"}
def send_whatsapp_confirmation(order_id):
    cursor.execute("""
        SELECT u.name, u.phone, o.total_amount
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.order_id=%s
    """, (order_id,))
    data = cursor.fetchone()
    message = f"""
Hello {data['name']} 👋
Your order #{order_id} is confirmed.
Amount: ₹{data['total_amount']}
Thank you for shopping with us 🚗
"""
    url = "https://graph.facebook.com/v18.0/PHONE_NUMBER_ID/messages"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": data["phone"],
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, json=payload, headers=headers)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
