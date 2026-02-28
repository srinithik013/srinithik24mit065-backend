from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Add CORS **immediately after creating app**
CORS(app, resources={r"/api/*": {"origins": "*"}})

# === Database Configuration ===
# Default to SQLite for easier local setup, switch to MySQL via .env if needed
USE_MYSQL = os.getenv('USE_MYSQL', 'false').lower() == 'true'

if USE_MYSQL:
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'with_bliss_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
else:
    # Use SQLite by default (file-based, no server needed)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'with_bliss.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === Database Models ===
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    def __init__(self, **kwargs):
        super(Package, self).__init__(**kwargs)

    def to_dict(self):
        return {"_id": str(self.id), "name": self.name, "price": self.price, "description": self.description, "image": self.image}

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=True) # Optional
    user_phone = db.Column(db.String(20), nullable=False)
    event_date = db.Column(db.String(50), nullable=True)
    package_name = db.Column(db.String(100), nullable=True)
    submitted_at = db.Column(db.String(50), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    def __init__(self, **kwargs):
        super(Booking, self).__init__(**kwargs)

    def to_dict(self):
        return {
            "_id": str(self.id), 
            "customer_name": self.user_name, 
            "user_email": self.user_email, 
            "contact": self.user_phone, 
            "date": self.event_date, 
            "package": self.package_name, 
            "submitted_at": self.submitted_at
        }

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.String(50), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    def __init__(self, **kwargs):
        super(ContactMessage, self).__init__(**kwargs)

    def to_dict(self):
        return {"_id": str(self.id), "name": self.name, "email": self.email, "message": self.message, "submitted_at": self.submitted_at}

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=True)

    def __init__(self, **kwargs):
        super(Gallery, self).__init__(**kwargs)

    def to_dict(self):
        return {"_id": str(self.id), "title": self.title, "image_url": self.image_url, "category": self.category}


# Create tables on startup (works with both gunicorn and direct run)
with app.app_context():
    try:
        db.create_all()
        print("Database tables initialized.")
    except Exception as e:
        print(f"DB init warning: {e}")

# ===========================
# HOME / HEALTH CHECK
# ===========================
@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "With Bliss Backend API is running successfully",
        "endpoints": ["/api/packages", "/api/bookings", "/api/contact", "/api/gallery"]
    })

# ===========================
# PACKAGES
# ===========================
@app.route('/api/packages', methods=['GET', 'POST'])
def manage_packages():
    if request.method == 'GET':
        packages = Package.query.all()
        return jsonify([p.to_dict() for p in packages])

    if request.method == 'POST':
        data = request.json
        new_pkg = Package(
            name=data.get('name'),
            price=data.get('price'),
            description=data.get('description'),
            image=data.get('image')
        )
        db.session.add(new_pkg)
        db.session.commit()
        return jsonify({"message": "Package added", "id": str(new_pkg.id)}), 201

@app.route('/api/packages/<int:id>', methods=['PUT', 'DELETE'])
def update_package(id):
    pkg = db.session.get(Package, id)
    if not pkg:
        return jsonify({"message": "Package not found"}), 404

    if request.method == 'PUT':
        data = request.json
        pkg.name = data.get('name', pkg.name)
        pkg.price = data.get('price', pkg.price)
        pkg.description = data.get('description', pkg.description)
        pkg.image = data.get('image', pkg.image)
        db.session.commit()
        return jsonify({"message": "Package updated"})

    if request.method == 'DELETE':
        db.session.delete(pkg)
        db.session.commit()
        return jsonify({"message": "Package deleted"})

# ===========================
# BOOKINGS
# ===========================
@app.route('/api/bookings', methods=['GET', 'POST'])
def manage_bookings():
    if request.method == 'GET':
        bookings = Booking.query.all()
        return jsonify([b.to_dict() for b in bookings])

    if request.method == 'POST':
        data = request.json
        # Handle both frontend naming conventions
        new_booking = Booking(
            user_name=data.get('customer_name') or data.get('user_name'),
            user_phone=data.get('contact') or data.get('user_phone'),
            event_date=data.get('date') or data.get('event_date'),
            package_name=data.get('package')
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"message": "Booking successful", "id": str(new_booking.id)}), 201

# ===========================
# CONTACT MESSAGES
# ===========================
@app.route('/api/contact', methods=['GET', 'POST'])
def contact_message():
    if request.method == 'GET':
        messages = ContactMessage.query.all()
        return jsonify([m.to_dict() for m in messages])

    if request.method == 'POST':
        data = request.json
        new_msg = ContactMessage(
            name=data.get('name'),
            email=data.get('email'),
            message=data.get('message')
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"message": "Message received"})

# ===========================
# GALLERY
# ===========================
@app.route('/api/gallery', methods=['GET', 'POST'])
def manage_gallery():
    if request.method == 'GET':
        images = Gallery.query.all()
        return jsonify([img.to_dict() for img in images])

    if request.method == 'POST':
        data = request.json
        new_img = Gallery(
            title=data.get('title'),
            image_url=data.get('image_url'),
            category=data.get('category')
        )
        db.session.add(new_img)
        db.session.commit()
        return jsonify({"message": "Image added to gallery"})

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables initialized.")
        except Exception as e:
            print(f"Database initialization failed: {e}")

    print("With Bliss Backend is running at http://localhost:5000")
    app.run(debug=True, port=5000)
