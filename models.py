from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model for storing user data."""
    __tablename__ = 'users'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(200), nullable=True)
    # profile_picture = db.Column(db.String(200), nullable=True)
    
    contacts = db.relationship('Contact', backref='owner', lazy=True)

    def __init__(self, full_name, email, password, age, address=None, phone=None):
        """Initialize a new User instance."""
        self.full_name = full_name
        self.email = email
        self.password = password
        self.age = age
        self.address = address
        self.phone = phone

    def __repr__(self):
        return f"<User {self.full_name} (ID: {self.id})>"

class Contact(db.Model):
    """Contact model for storing user contacts."""
    __tablename__ = 'contacts'  

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, age, phone, address, email, user_id):
        """Initialize a new Contact instance."""
        self.name = name
        self.age = age
        self.phone = phone
        self.address = address
        self.email = email
        self.user_id = user_id

    def __repr__(self):
        return f"<Contact {self.name} (ID: {self.id}) owned by User ID: {self.user_id}>"