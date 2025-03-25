from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Contact
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# our database uri
if 'RDS_DB_NAME' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD'],
        host=os.environ['RDS_HOSTNAME'],
        port=os.environ['RDS_PORT'],
        database=os.environ['RDS_DB_NAME'],
    )
else:
    # our database uri
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost:5432/sample_users_db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Print template directory for debugging
print("Template directory:", os.path.join(os.path.dirname(__file__), 'templates'))

# Database migration settings
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/', methods=['GET', 'POST'])
def login():
    print("HERE??")
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("HERE??")
        
        user = User.query.filter_by(email=email).first()
        print(user)
        print("HERE??")
       
        if user and user.password == password:
            print("HERE in IF??")
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            return jsonify({'success': True, 'message': f'Welcome back, {user.full_name}!'})
        else:
            return jsonify({'success': False, 'message': 'Please check your email and password'})
    
    return render_template('login.html')

@app.route('/login-by-ajax', methods=['POST', 'GET']) 
def login_by_ajax():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            session['user_id'] = user.id  
            session['user_name'] = user.full_name
            return jsonify({'output_msg': f'Welcome back, {user.full_name}!', 'success': True})
        else:
            return jsonify({'output_msg': 'Invalid email or password. Please try again.', 'success': False})
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['name']
        age = int(request.form['age'])
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
       
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', error="Email already exists!")
       
        new_user = User(
            full_name=full_name,
            email=email,
            password=password,  
            age=age,
            address=address,
            phone=phone
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful!', 'success')
            return redirect(url_for('login'))  
        except Exception as e:
            db.session.rollback()
            return render_template('signup.html', error=f"Error: {str(e)}")

    return render_template('signup.html')

@app.route('/signup_by_ajax', methods=['GET', 'POST'])
def signup_user_by_ajax():
    if request.method == 'POST':
        full_name = request.form['username']
        age = int(request.form['age'])
        phone = request.form['phone']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already in use, please try another email address.'})

        new_user = User(
            full_name=full_name,
            email=email,
            password=password,
            age=age,
            address=address,
            phone=phone,
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Signup successful! Redirecting to login...'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})
    
    return render_template('signup.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please login.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    print(f"User ID: {session['user_id']}, User: {user}")
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))
    return render_template('home.html', user=user)

@app.route('/view_users_list')
def view_users_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    contacts = Contact.query.filter_by(user_id=session['user_id']).all()
    print(f"Contacts fetched: {[contact.name for contact in contacts]}")
    return render_template('view_users_list.html', users=contacts)

@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    if 'user_id' not in session:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Please login first'})
        return redirect(url_for('login'))
    
    contact = Contact.query.get(contact_id)
    if not contact or contact.user_id != session['user_id']:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Contact not found or unauthorized'})
        return redirect(url_for('view_users_list'))
    
    if request.method == 'GET':
        return render_template('edit_user.html', contact=contact)
    elif request.method == 'POST':
        try:
            contact.name = request.form['name']
            contact.age = int(request.form['age'])
            contact.phone = request.form['phone']
            contact.address = request.form['address']
            contact.email = request.form['email']
            db.session.commit()
            return jsonify({'success': True, 'message': 'Contact updated successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Please login first'})
        flash('Login please', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if request.method == 'GET':
        return render_template('change_password.html')
    elif request.method == 'POST':
        try:
            new_password = request.form['password']
            user.password = new_password  
            db.session.commit()
            return jsonify({'success': True, 'message': 'Password changed successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/delete_contact/<int:contact_id>', methods=['POST', 'GET'])
def delete_contact(contact_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login'})
    
    contact = Contact.query.get(contact_id)
    if not contact or contact.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Contact not found or unauthorized'})
    
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Contact deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/delete_confirm/<int:user_id>', methods=['GET'])
def delete_confirm(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    contact = Contact.query.get(user_id)
    if not contact or contact.user_id != session['user_id']:
        return redirect(url_for('view_users_list'))
    
    print(f"Rendering delete_confirm.html for contact ID: {user_id}")
    return render_template('delete_confirm.html', user=contact)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    print("Entering /add_contact")
    if 'user_id' not in session:
        print("No session user_id, redirecting to login")
        return jsonify({'success': False, 'redirect': url_for('login')})

    if request.method == 'POST':
        print("Received POST request to /add_contact")
        try:
            full_name = request.form['name']
            age = int(request.form['age'])
            phone = request.form['phone']
            address = request.form['address']
            email = request.form['email']
            print(f"Form data: name={full_name}, age={age}, phone={phone}, address={address}, email={email}")

            existing_contact = Contact.query.filter_by(email=email).first()
            if existing_contact:
                print(f"Email {email} already exists in contacts")
                return jsonify({'success': False, 'message': 'Email already exists in contacts!'})

            new_contact = Contact(
                name=full_name,
                age=age,
                phone=phone,
                address=address,
                email=email,
                user_id=session['user_id']
            )

            db.session.add(new_contact)
            db.session.commit()
            print(f"Added contact: {new_contact.name}, ID: {new_contact.id}")
            return jsonify({'success': True, 'redirect': url_for('view_users_list')})
        except Exception as e:
            db.session.rollback()
            print(f"Error adding contact: {str(e)}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    print("Rendering add_contact.html")
    return render_template('add_contact.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)