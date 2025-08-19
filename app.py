import flask
from flask import Flask, request, redirect, url_for, session, render_template, jsonify
import mysql.connector
from mysql.connector import Error
import datetime
import random  # Needed for the init_parking_slots endpoint
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"

PLATE_RECOGNIZER_API_KEY = "4470e01b51a38c9425cbf1a8cc8d7f9768bca26b"
PLATE_RECOGNIZER_URL = "https://api.platerecognizer.com/v1/plate-reader/"

# 1) Create the database and tables if they don't exist
def create_db_and_table():
    try:
        # Connect to MySQL (without specifying a database)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Negligence@13"
        )
        cursor = conn.cursor()

        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS my_app_db")
        cursor.execute("USE my_app_db")

        # Create Users Table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS tbl_users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            licence VARCHAR(50),
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            phone VARCHAR(15),
            dob DATE
        );
        """
        cursor.execute(create_users_table)

        # Create Payments Table
        create_payments_table = """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100),
            amount DECIMAL(10,2),
            payment_method VARCHAR(50),
            promo_code VARCHAR(20),
            final_amount DECIMAL(10,2),
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (email) REFERENCES tbl_users(email) ON DELETE CASCADE
        );
        """
        cursor.execute(create_payments_table)

        # Create Vehicles Table using user's email as foreign key
        create_vehicles_table = """
        CREATE TABLE IF NOT EXISTS tbl_vehicles (
            vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100),
            vehicle_number VARCHAR(50),
            vehicle_model VARCHAR(100),
            vehicle_color VARCHAR(50),
            registration_year INT,
            FOREIGN KEY (user_email) REFERENCES tbl_users(email) ON DELETE CASCADE
        );
        """
        cursor.execute(create_vehicles_table)

        # Create Wallets Table with default balance of 1000
        create_wallets_table = """
        CREATE TABLE IF NOT EXISTS tbl_wallets (
            wallet_id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100),
            balance DECIMAL(10,2) DEFAULT 1000,
            FOREIGN KEY (user_email) REFERENCES tbl_users(email) ON DELETE CASCADE
        );
        """
        cursor.execute(create_wallets_table)

        # Create Admins Table
        create_admins_table = """
        CREATE TABLE IF NOT EXISTS tbl_admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        );
        """
        cursor.execute(create_admins_table)

        # Create Transactions Table
        create_transactions_table = """
        CREATE TABLE IF NOT EXISTS tbl_transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100),
            start_time DATETIME,
            end_time DATETIME,
            transaction_mode VARCHAR(50),
            amount DECIMAL(10,2),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES tbl_users(email) ON DELETE CASCADE
        );
        """
        cursor.execute(create_transactions_table)

        # Create UPI Transactions Table
        create_upi_transactions = """
        CREATE TABLE IF NOT EXISTS tbl_upi_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id INT,
            upi_id VARCHAR(100),
            promo_code VARCHAR(20),
            FOREIGN KEY (transaction_id) REFERENCES tbl_transactions(transaction_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_upi_transactions)

        # Create Wallet Transactions Table
        create_wallet_transactions = """
        CREATE TABLE IF NOT EXISTS tbl_wallet_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id INT,
            payment_method VARCHAR(50),
            promo_code VARCHAR(20),
            FOREIGN KEY (transaction_id) REFERENCES tbl_transactions(transaction_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_wallet_transactions)

        # Create Credit Transactions Table
        create_credit_transactions = """
        CREATE TABLE IF NOT EXISTS tbl_credit_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id INT,
            card_number VARCHAR(20),
            card_holder VARCHAR(100),
            expiry_date VARCHAR(10),
            promo_code VARCHAR(20),
            FOREIGN KEY (transaction_id) REFERENCES tbl_transactions(transaction_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_credit_transactions)

        # Create Debit Transactions Table
        create_debit_transactions = """
        CREATE TABLE IF NOT EXISTS tbl_debit_transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_id INT,
            card_number VARCHAR(20),
            card_holder VARCHAR(100),
            expiry_date VARCHAR(10),
            promo_code VARCHAR(20),
            FOREIGN KEY (transaction_id) REFERENCES tbl_transactions(transaction_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_debit_transactions)

        # Create Login History Table
        create_login_history_table = """
        CREATE TABLE IF NOT EXISTS tbl_login_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100),
            login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(50)
        );
        """
        cursor.execute(create_login_history_table)

        # Create Parking Slots Table
        create_parking_slots_table = """
        CREATE TABLE IF NOT EXISTS tbl_parking_slots (
            slot_id INT AUTO_INCREMENT PRIMARY KEY,
            slot_name VARCHAR(50) UNIQUE,
            lat DECIMAL(10,6),
            lng DECIMAL(10,6)
        );
        """
        cursor.execute(create_parking_slots_table)

        # Create Slot Reservations Table
        create_slot_res_table = """
        CREATE TABLE IF NOT EXISTS tbl_slot_reservations (
            reservation_id INT AUTO_INCREMENT PRIMARY KEY,
            slot_id INT,
            user_email VARCHAR(100),
            start_time DATETIME,
            end_time DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (slot_id) REFERENCES tbl_parking_slots(slot_id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_slot_res_table)

        def create_pricing_table(cursor):
            # This table stores pricing rates based on day and time window.
            create_pricing_table = """
            CREATE TABLE IF NOT EXISTS tbl_pricing (
                pricing_id INT AUTO_INCREMENT PRIMARY KEY,
                day_of_week VARCHAR(20), -- e.g., 'Weekday', 'Weekend'
                time_window VARCHAR(20), -- e.g., 'Peak', 'Off-Peak'
                rate_per_hour DECIMAL(10,2)
            );
            """
            cursor.execute(create_pricing_table)

        # Create Parking Lot Owners Table
        create_parkinglotowners_table = """
        CREATE TABLE IF NOT EXISTS tbl_parkinglotowners (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(255),
            name VARCHAR(100),
            contact VARCHAR(15),
            lot_name VARCHAR(100),
            location VARCHAR(255),
            capacity INT,
            pricing DECIMAL(10,2),
            amenities VARCHAR(255)
        );
        """
        cursor.execute(create_parkinglotowners_table)

        # Create Owner Registrations Table (to store details entered via register_owner.html)
        create_owner_registrations = """
        CREATE TABLE IF NOT EXISTS tbl_owner_registrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            owner_email VARCHAR(100),
            lot_name VARCHAR(100),
            location VARCHAR(255),
            capacity INT,
            contact VARCHAR(15),
            pricing DECIMAL(10,2),
            amenities VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_owner_registrations)

        # Create Owner Payments Table (to store 60% share per transaction type)
        create_owner_payments = """
        CREATE TABLE IF NOT EXISTS tbl_owner_payments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            owner_email VARCHAR(100),
            transaction_date DATE,
            transaction_type VARCHAR(50),
            total_amount DECIMAL(10,2),
            owner_share DECIMAL(10,2),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE(owner_email, transaction_date, transaction_type)
        );
        """
        cursor.execute(create_owner_payments)
        
        create_owner_complaints = """
        CREATE TABLE IF NOT EXISTS tbl_complaints (
            complaint_id INT AUTO_INCREMENT PRIMARY KEY,
            owner_email VARCHAR(100),
            licence_plate VARCHAR(50),
            complaint_type VARCHAR(50),
            additional_info TEXT,
            image_path VARCHAR(255),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Insert a default parking lot owner if one doesn't already exist
        default_owner_email = 'owner@example.com'
        default_owner_password = 'password'  # Consider hashing the password in production
        default_owner_name = 'Default Owner'
        default_owner_contact = '1234567890'
        default_lot_name = 'Default Lot'
        default_location = '123 Default Street'
        default_capacity = 50
        default_pricing = 10.00
        default_amenities = 'CCTV, Security'

        insert_default_owner = """
        INSERT IGNORE INTO tbl_parkinglotowners 
        (email, password, name, contact, lot_name, location, capacity, pricing, amenities)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_default_owner, (default_owner_email, default_owner_password, default_owner_name, default_owner_contact, default_lot_name, default_location, default_capacity, default_pricing, default_amenities))
        conn.commit()


        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables created (if they did not exist).")
    except Error as e:
        print("Error creating database or tables:", e)

# 2) Helper function to get a connection to the database
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Negligence@13",
            database="my_app_db"
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None

# 3) Flask Routes

@app.route("/")
def home():
    return redirect(url_for("register"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        licence = request.form.get("licence")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        phone = request.form.get("phone")
        dob = request.form.get("dob")

        if password != confirm_password:
            return "Passwords do not match. <a href='/register'>Try again</a>"

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!"
        try:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO tbl_users (licence, name, email, password, phone, dob)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (licence, name, email, password, phone, dob))
            conn.commit()

            # Automatically register a wallet with default balance 1000
            insert_wallet_query = "INSERT INTO tbl_wallets (user_email) VALUES (%s)"
            cursor.execute(insert_wallet_query, (email,))
            conn.commit()

            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        except Error as e:
            return f"Error inserting data: {e}"
    return render_template("register.html")

@app.route("/register_owner", methods=["GET", "POST"])
def register_owner():
    if request.method == "POST":
        lot_name = request.form.get("lot-name")
        location = request.form.get("location")
        capacity = request.form.get("capacity")
        owner_name = request.form.get("owner-name")
        owner_phone = request.form.get("owner-phone")
        email = request.form.get("owner-email")
        pricing = request.form.get("pricing")
        amenities = request.form.get("amenities")
        
        # Optionally, you might want to add a password field for the owner.
        # For now, we’ll use a default password.
        default_password = "ownerpassword"  # In production, hash this!
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!"
        try:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO tbl_parkinglotowners (email, password, name, contact, lot_name, location, capacity, pricing, amenities)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (email, default_password, owner_name, owner_phone, lot_name, location, capacity, pricing, amenities))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        except Error as e:
            return f"Error inserting owner data: {e}"
    return render_template("register_owner.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!"
        try:
            cursor = conn.cursor(dictionary=True)
            # Check if credentials match an admin record.
            select_admin_query = "SELECT * FROM tbl_admins WHERE email = %s AND password = %s"
            cursor.execute(select_admin_query, (email, password))
            admin = cursor.fetchone()
            if admin:
                session["admin_id"] = admin["id"]
                session["email"] = admin["email"]
                user_ip = request.remote_addr
                insert_login_history = "INSERT INTO tbl_login_history (user_email, ip_address) VALUES (%s, %s)"
                cursor.execute(insert_login_history, (email, user_ip))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("admin_home"))
            
            # Check if credentials match a parking lot owner record.
            select_owner_query = "SELECT * FROM tbl_parkinglotowners WHERE email = %s AND password = %s"
            cursor.execute(select_owner_query, (email, password))
            owner = cursor.fetchone()
            if owner:
                session["owner_id"] = owner["id"]
                session["email"] = owner["email"]
                user_ip = request.remote_addr
                insert_login_history = "INSERT INTO tbl_login_history (user_email, ip_address) VALUES (%s, %s)"
                cursor.execute(insert_login_history, (email, user_ip))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("index_owner"))
            
            # Check for regular user credentials.
            select_query = "SELECT * FROM tbl_users WHERE email = %s AND password = %s"
            cursor.execute(select_query, (email, password))
            user = cursor.fetchone()
            if user:
                session["user_id"] = user["id"]
                session["email"] = user["email"]
                # Ensure wallet record exists for the user.
                cursor2 = conn.cursor()
                select_wallet_query = "SELECT * FROM tbl_wallets WHERE user_email = %s"
                cursor2.execute(select_wallet_query, (email,))
                wallet = cursor2.fetchone()
                if wallet is None:
                    insert_wallet_query = "INSERT INTO tbl_wallets (user_email) VALUES (%s)"
                    cursor2.execute(insert_wallet_query, (email,))
                    conn.commit()
                cursor2.close()
                user_ip = request.remote_addr
                insert_login_history = "INSERT INTO tbl_login_history (user_email, ip_address) VALUES (%s, %s)"
                cursor.execute(insert_login_history, (email, user_ip))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("page1"))
            else:
                cursor.close()
                conn.close()
                return redirect(url_for("login"))
        except Exception as e:
            return f"Error during login: {e}"
    return render_template("login.html")


@app.route("/page1")
def page1():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("page1.html")

@app.route("/credit")
def credit():
    return render_template("credit.html")

@app.route("/debit")
def debit():
    return render_template("debit.html")

@app.route("/payment")
def payment():
    return render_template("payment.html")

@app.route("/upi")
def upi():
    return render_template("upi.html")

@app.route("/wallet")
def wallet():
    return render_template("wallet.html")

@app.route("/navigation")
def navigation():
    return render_template("navigation.html")

@app.route("/detection")
def detection():
    return render_template("detection.html")

@app.route("/detection2")
def detection2():
    return render_template("detection2.html")

@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/register_vehicle", methods=["GET", "POST"])
def register_vehicle():
    if request.method == "POST":
        user_email = session.get("email")
        vehicle_number = request.form.get("vehicle_number")
        vehicle_model = request.form.get("vehicle_model")
        vehicle_color = request.form.get("vehicle_color")
        registration_year = request.form.get("registration_year")
        if not user_email:
            return "User not logged in. Please login first."
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!"
        try:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO tbl_vehicles (user_email, vehicle_number, vehicle_model, vehicle_color, registration_year)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (user_email, vehicle_number, vehicle_model, vehicle_color, registration_year))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for("page1"))
        except Error as e:
            return f"Error inserting vehicle data: {e}"
    return render_template("register_vehicle.html")

# Endpoint: Get registered vehicles for the logged-in user
@app.route("/get_user_vehicles")
def get_user_vehicles():
    if "email" not in session:
        return jsonify({"vehicles": []})
    email = session["email"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"vehicles": []})
    cursor = conn.cursor()
    cursor.execute("SELECT vehicle_number FROM tbl_vehicles WHERE user_email = %s", (email,))
    vehicles = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify({"vehicles": vehicles})

# Endpoint: Get current wallet balance for the logged-in user
@app.route("/get_wallet_balance")
def get_wallet_balance():
    if "email" not in session:
        return jsonify({"balance": 0})
    email = session["email"]
    conn = get_db_connection()
    if conn is None:
        return jsonify({"balance": 0})
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM tbl_wallets WHERE user_email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({"balance": result[0] if result else 0})

# Endpoint: Process wallet payment – deduct the amount and record the transaction
@app.route("/process_wallet_payment", methods=["POST"])
def process_wallet_payment():
    if "email" not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    try:
        final_amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid amount provided"}), 400
    payment_method = data.get("payment_method")
    promo_code = data.get("promo_code")
    email = session["email"]

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM tbl_wallets WHERE user_email = %s", (email,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"success": False, "error": "Wallet record not found"}), 400
        current_balance = float(result[0])
        if current_balance < final_amount:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "Insufficient wallet balance"}), 400

        # Update wallet balance
        cursor.execute("UPDATE tbl_wallets SET balance = balance - %s WHERE user_email = %s", (final_amount, email))
        conn.commit()

        # Record payment in payments table
        cursor.execute(
            "INSERT INTO payments (email, amount, payment_method, promo_code, final_amount) VALUES (%s, %s, %s, %s, %s)",
            (email, final_amount, payment_method, promo_code, final_amount)
        )
        conn.commit()

        # Insert a record into the main transactions table
        start_time = data.get("start_time")  # Expect these to be passed from the client
        end_time = data.get("end_time")
        transaction_mode = "Wallet"
        status = "Successful"
        insert_transaction = """
            INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (email, start_time, end_time, transaction_mode, final_amount, status))
        conn.commit()
        transaction_id = cursor.lastrowid  # Get the ID of the newly inserted transaction

        # Insert record into wallet_transactions table
        insert_wallet_transaction = """
            INSERT INTO tbl_wallet_transactions (transaction_id, payment_method, promo_code)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_wallet_transaction, (transaction_id, payment_method, promo_code))
        conn.commit()

        # Return updated wallet balance
        cursor.execute("SELECT balance FROM tbl_wallets WHERE user_email = %s", (email,))
        updated_balance = float(cursor.fetchone()[0])
        cursor.close()
        conn.close()
        return jsonify({"success": True, "remaining_balance": updated_balance})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/process_debit_payment", methods=["POST"])
def process_debit_payment():
    if "email" not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    try:
        final_amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid amount provided"}), 400

    card_number = data.get("card_number")
    card_holder = data.get("card_holder")
    expiry_date = data.get("expiry_date")
    promo_code = data.get("promo_code")
    start_time = data.get("start_time")  # passed from the client
    end_time = data.get("end_time")      # passed from the client
    email = session["email"]

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        transaction_mode = "Debit Card"
        status = "Successful"
        insert_transaction = """
            INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (email, start_time, end_time, transaction_mode, final_amount, status))
        conn.commit()
        transaction_id = cursor.lastrowid

        insert_debit_transaction = """
            INSERT INTO tbl_debit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_debit_transaction, (transaction_id, card_number, card_holder, expiry_date, promo_code))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/process_credit_payment", methods=["POST"])
def process_credit_payment():
    if "email" not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    try:
        final_amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid amount provided"}), 400

    card_number = data.get("card_number")
    card_holder = data.get("card_holder")
    expiry_date = data.get("expiry_date")
    promo_code = data.get("promo_code")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    email = session["email"]

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        transaction_mode = "Credit Card"
        status = "Successful"
        insert_transaction = """
            INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (email, start_time, end_time, transaction_mode, final_amount, status))
        conn.commit()
        transaction_id = cursor.lastrowid

        insert_credit = """
            INSERT INTO tbl_credit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_credit, (transaction_id, card_number, card_holder, expiry_date, promo_code))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/process_upi_payment", methods=["POST"])
def process_upi_payment():
    if "email" not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    try:
        final_amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Invalid amount provided"}), 400

    upi_id = data.get("upi_id")
    promo_code = data.get("promo_code")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    email = session["email"]

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        transaction_mode = "UPI"
        status = "Successful"
        insert_transaction = """
            INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_transaction, (email, start_time, end_time, transaction_mode, final_amount, status))
        conn.commit()
        transaction_id = cursor.lastrowid

        insert_upi = """
            INSERT INTO tbl_upi_transactions (transaction_id, upi_id, promo_code)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_upi, (transaction_id, upi_id, promo_code))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/init_parking_slots")
def init_parking_slots():
    """Seed 10 random slots if none exist."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as cnt FROM tbl_parking_slots")
        row = cursor.fetchone()
        if row["cnt"] == 0:
            base_lat, base_lng = 11.0168, 76.9558
            for i in range(1, 11):
                lat = base_lat + random.uniform(-0.01, 0.01)
                lng = base_lng + random.uniform(-0.01, 0.01)
                slot_name = f"Slot {i}"
                insert_q = "INSERT INTO tbl_parking_slots (slot_name, lat, lng) VALUES (%s, %s, %s)"
                cursor.execute(insert_q, (slot_name, lat, lng))
            conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get_parking_slots", methods=["GET"])
def get_parking_slots():
    """Return all slots from tbl_parking_slots."""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT slot_id, slot_name, lat, lng
        FROM tbl_parking_slots
        ORDER BY slot_id
        """
        cursor.execute(query)
        slots = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(slots)
    except Error:
        return jsonify([])

@app.route("/get_slot_reservations", methods=["GET"])
def get_slot_reservations():
    """Return all reservations from tbl_slot_reservations."""
    conn = get_db_connection()
    if not conn:
        return jsonify([])
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT reservation_id, slot_id, user_email, start_time, end_time, created_at
        FROM tbl_slot_reservations
        ORDER BY start_time
        """
        cursor.execute(query)
        res = cursor.fetchall()
        for r in res:
            if isinstance(r["start_time"], datetime.datetime):
                r["start_time"] = r["start_time"].isoformat()
            if isinstance(r["end_time"], datetime.datetime):
                r["end_time"] = r["end_time"].isoformat()
            if isinstance(r["created_at"], datetime.datetime):
                r["created_at"] = r["created_at"].isoformat()
        cursor.close()
        conn.close()
        return jsonify(res)
    except Error as e:
        print("Error fetching slot reservations:", e)
        return jsonify([])

@app.route("/reserve_slot", methods=["POST"])
def reserve_slot():
    """Insert a new reservation if no overlap for that slot/time range."""
    if "email" not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.get_json()
    slot_id = data.get("slot_id")
    reserved_from = data.get("reserved_from")  # "YYYY-MM-DD HH:MM:SS"
    reserved_to = data.get("reserved_to")
    email = session["email"]

    if not slot_id or not reserved_from or not reserved_to:
        return jsonify({"success": False, "error": "Missing reservation details"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()

        # Overlap check for the same slot
        overlap_q = """
        SELECT reservation_id FROM tbl_slot_reservations
        WHERE slot_id = %s
          AND (start_time < %s AND end_time > %s)
        """
        cursor.execute(overlap_q, (slot_id, reserved_to, reserved_from))
        overlap = cursor.fetchone()
        if overlap:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "This slot is already reserved for that time range."}), 400

        # If you also want to prevent the user from double-booking themselves:
        user_overlap_q = """
        SELECT reservation_id FROM tbl_slot_reservations
        WHERE user_email = %s
          AND (start_time < %s AND end_time > %s)
        """
        cursor.execute(user_overlap_q, (email, reserved_to, reserved_from))
        user_overlap = cursor.fetchone()
        if user_overlap:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "You already have an overlapping reservation."}), 400

        # Insert new reservation
        insert_q = """
        INSERT INTO tbl_slot_reservations (slot_id, user_email, start_time, end_time)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_q, (slot_id, email, reserved_from, reserved_to))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

def get_pricing():
    """
    Returns the entire pricing table.
    Example JSON:
    {
      "success": true,
      "rates": [
        {
          "pricing_id": 1,
          "day_of_week": "Weekday",
          "time_window": "Off-Peak",
          "rate_per_hour": 50.00
        },
        ...
      ]
    }
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tbl_pricing")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "rates": rows})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/update_pricing", methods=["POST"])
def update_pricing():
    """
    Allows admin to update the rate_per_hour for a given pricing_id.
    Expects JSON: { "pricing_id": 1, "rate_per_hour": 65.00 }
    """
    data = request.get_json()
    pricing_id = data.get("pricing_id")
    rate = data.get("rate_per_hour")
    if pricing_id is None or rate is None:
        return jsonify({"success": False, "error": "Missing pricing_id or rate"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor()
        update_sql = "UPDATE tbl_pricing SET rate_per_hour = %s WHERE pricing_id = %s"
        cursor.execute(update_sql, (rate, pricing_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# Booking Analysis Endpoint
# -------------------------------
@app.route("/get_booking_analysis", methods=["GET"])
def get_booking_analysis():
    """
    Example: returns aggregated data by hour for total bookings and average price.
    In real usage, you'd replace the price logic with your actual pricing calculations or references to transactions.
    """
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        # Example logic: 
        # - we assume tbl_slot_reservations is used for bookings
        # - we do a rough guess for price by hour, day, etc.
        query = """
        SELECT 
          HOUR(start_time) AS booking_hour,
          COUNT(*) AS total_bookings,
          -- Example: approximate average cost for demonstration
          AVG(TIMESTAMPDIFF(MINUTE, start_time, end_time)/60 * 50) AS avg_price
        FROM tbl_slot_reservations
        GROUP BY booking_hour
        ORDER BY booking_hour;
        """
        cursor.execute(query)
        analysis = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "analysis": analysis})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------------------
# Download Report Endpoint
# -------------------------------
@app.route("/download_report", methods=["GET"])
def download_report():
    """
    For demonstration: returns a success message with timeframe.
    If you want to serve a real PDF file, you'd generate it and return the file content here.
    """
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if not start_date or not end_date:
        return jsonify({"success": False, "error": "Missing start_date or end_date"}), 400
    # In real usage, generate or query data in [start_date, end_date].
    return jsonify({"success": True, "message": f'Report from {start_date} to {end_date} generated successfully.'})


# -------------------------
# Admin Routes
# -------------------------

@app.route("/admin_home")
def admin_home():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_home-page.html")

@app.route("/admin_tracking")
def admin_tracking():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_tracking.html")

@app.route("/admin_datainsights")
def admin_datainsights():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_datainsights.html")

@app.route("/admin_dataexport")
def admin_dataexport():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_dataexport.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_dashboard.html")

@app.route("/admin_navigation")
def admin_navigation():
    if "admin_id" not in session:
        return redirect(url_for("login"))
    return render_template("admin_navigation.html")

@app.route("/get_transactions", methods=["GET"])
def get_transactions():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT transaction_id, user_email, 
                   COALESCE(start_time, created_at) AS start_time, 
                   end_time, transaction_mode, amount, status, created_at
            FROM tbl_transactions
            ORDER BY start_time DESC
        """
        cursor.execute(query)
        transactions = cursor.fetchall()
        
        for tx in transactions:
            if not tx.get('start_time'):
                tx['start_time'] = tx['created_at']
            if isinstance(tx.get('start_time'), datetime.datetime):
                tx['start_time'] = tx['start_time'].isoformat()
            if tx.get('end_time') and isinstance(tx.get('end_time'), datetime.datetime):
                tx['end_time'] = tx['end_time'].isoformat()
            if isinstance(tx.get('created_at'), datetime.datetime):
                tx['created_at'] = tx['created_at'].isoformat()
                
        print("Fetched transactions:", transactions)
        cursor.close()
        conn.close()
        return jsonify(transactions)
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin_get_users", methods=["GET"])
def admin_get_users():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, email, 'User' AS role FROM tbl_users"
        cursor.execute(query)
        users = cursor.fetchall()
        query_admin = "SELECT id, email, 'Admin' AS role FROM tbl_admins"
        cursor.execute(query_admin)
        admins = cursor.fetchall()
        cursor.close()
        conn.close()
        all_users = admins + users
        return jsonify(all_users)
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin_delete_user", methods=["POST"])
def admin_delete_user():
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "User ID not provided"}), 400
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = "DELETE FROM tbl_users WHERE id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route("/admin_get_logins", methods=["GET"])
def admin_get_logins():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, user_email, login_time, ip_address
            FROM tbl_login_history
            ORDER BY login_time DESC
        """
        cursor.execute(query)
        logins = cursor.fetchall()
        for login in logins:
            if isinstance(login.get('login_time'), datetime.datetime):
                login['login_time'] = login['login_time'].isoformat()
        cursor.close()
        conn.close()
        return jsonify(logins)
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route("/admin_toggle_2fa", methods=["POST"])
def admin_toggle_2fa():
    data = request.get_json()
    enabled = data.get("enabled")
    return jsonify({"success": True, "2fa_enabled": enabled})

# ------------------------------------------
# OWNER
# ------------------------------------------

@app.route("/index_owner")
def index_owner():
    if "owner_id" not in session:
        return redirect(url_for("login"))
    return render_template("index_owner.html")

@app.route("/payments_owner")
def payments_owner():
    if "owner_id" not in session:
        return redirect(url_for("login"))
    return render_template("payments_owner.html")

@app.route("/complaint_owner")
def complaint_owner():
    if "owner_id" not in session:
        return redirect(url_for("login"))
    return render_template("complaint_owner.html")

@app.route("/register_owner", methods=["GET", "POST"])
def render_register_owner():
    if request.method == "POST":
        lot_name = request.form.get("lot-name")
        location = request.form.get("location")
        capacity = request.form.get("capacity")
        owner_name = request.form.get("owner-name")
        contact = request.form.get("contact")
        email = request.form.get("email")
        pricing = request.form.get("pricing")
        amenities = request.form.get("amenities")
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed!"
        try:
            cursor = conn.cursor()
            # Insert into the owner registrations table
            insert_sql = """
            INSERT INTO tbl_owner_registrations 
            (owner_email, lot_name, location, capacity, contact, pricing, amenities)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (email, lot_name, location, capacity, contact, pricing, amenities))
            conn.commit()
            cursor.close()
            conn.close()
            # Optionally, redirect to the owner homepage after successful registration
            return redirect(url_for("index_owner"))
        except Exception as e:
            return f"Error inserting registration data: {e}"
    return render_template("register_owner.html")


@app.route("/contact_owner", methods=["GET", "POST"])
def render_contact_owner():
    # Here, add your processing logic for owner contact messages if needed.
    return render_template("contact_owner.html")

@app.route("/statistics_owner")
def render_statistics_owner():
    if "owner_id" not in session:
        return redirect(url_for("login"))
    return render_template("statistics_owner.html")

@app.route("/get_owner_payments", methods=["GET"])
def get_owner_payments():
    if "owner_id" not in session:
        return jsonify({"success": False, "error": "Owner not logged in"}), 401
    
    owner_email = session["email"]
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "error": "DB connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Build the query based on provided dates.
        if start_date and end_date:
            query = """
            SELECT transaction_mode, SUM(amount) AS total_amount
            FROM tbl_transactions
            WHERE owner_email = %s AND DATE(start_time) BETWEEN %s AND %s
            GROUP BY transaction_mode
            """
            cursor.execute(query, (owner_email, start_date, end_date))
        elif start_date:
            query = """
            SELECT transaction_mode, SUM(amount) AS total_amount
            FROM tbl_transactions
            WHERE owner_email = %s AND DATE(start_time) = %s
            GROUP BY transaction_mode
            """
            cursor.execute(query, (owner_email, start_date))
        else:
            query = """
            SELECT transaction_mode, SUM(amount) AS total_amount
            FROM tbl_transactions
            WHERE owner_email = %s
            GROUP BY transaction_mode
            """
            cursor.execute(query, (owner_email,))
            
        results = cursor.fetchall()
        owner_payments = []
        for row in results:
            total_amount = float(row["total_amount"] or 0)
            owner_share = total_amount * 0.6
            transaction_type = row["transaction_mode"]
            
            # Only update the backend table if a single date is provided.
            if start_date and not end_date:
                insert_sql = """
                INSERT INTO tbl_owner_payments (owner_email, transaction_date, transaction_type, total_amount, owner_share)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    total_amount = VALUES(total_amount), 
                    owner_share = VALUES(owner_share)
                """
                cursor.execute(insert_sql, (owner_email, start_date, transaction_type, total_amount, owner_share))
            
            owner_payments.append({
                "transaction_type": transaction_type,
                "total_amount": total_amount,
                "owner_share": owner_share
            })
            
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "payments": owner_payments})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ocr_plate", methods=["POST"])
def ocr_plate():
    """
    This route receives a file under 'plateImage' from the JS fetch call,
    sends it to Plate Recognizer, and returns JSON with the recognized plate.
    """
    if 'plateImage' not in request.files:
        return jsonify({"success": False, "error": "No file part in the request."})
    file = request.files['plateImage']
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file."})

    try:
        # We won't store the file permanently here; just pass it to Plate Recognizer.
        headers = {"Authorization": f"Token {PLATE_RECOGNIZER_API_KEY}"}
        files = {"upload": (file.filename, file.stream, file.mimetype)}
        response = requests.post(PLATE_RECOGNIZER_URL, files=files, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                plate = data["results"][0].get("plate", "").upper()
                return jsonify({"success": True, "plate": plate})
            else:
                return jsonify({"success": True, "plate": ""})  # No plate found
        else:
            return jsonify({"success": False, "error": f"Plate Recognizer API error: {response.status_code}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    """
    This route processes the final complaint submission, including
    re-uploading the file or storing the same file again if needed.
    """
    if "owner_id" not in session:
        return redirect(url_for("login"))
    
    # Extract form fields
    owner_email = session["email"]
    licence_plate = request.form.get("licencePlate")
    complaint_type = request.form.get("complaintType")
    additional_info = ""
    if complaint_type == "Other":
        additional_info = request.form.get("otherComplaint", "")

    # Handle the uploaded file (again) for storing in 'static/complaint_images'
    file = request.files.get("plateImage")
    image_path = None
    if file and file.filename:
        # Create the folder if not exists
        upload_folder = os.path.join(app.root_path, "static", "complaint_images")
        if not os.path.isdir(upload_folder):
            os.makedirs(upload_folder)
        
        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # We'll store the relative path in DB
        image_path = f"static/complaint_images/{filename}"

    # Insert into the tbl_complaints table
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed!"
    
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO tbl_complaints (owner_email, licence_plate, complaint_type, additional_info, image_path)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (owner_email, licence_plate, complaint_type, additional_info, image_path))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("index_owner"))
    except Error as e:
        return f"Error submitting complaint: {e}"

if __name__ == "__main__":
    create_db_and_table()
    app.run(debug=True)
