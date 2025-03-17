from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User 
from werkzeug.utils import secure_filename 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/sample_users_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

 
#Database migration settings
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
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('home'))
        else:
            print("HERE in else??")
            flash('Please check your email and password if they are correct', 'error')
            return render_template('login.html')
    
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
        flash('Please login .', 'error')
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
        flash('Please login .', 'error')
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('view_users_list.html', users=users)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Please login first'})
        flash('Login first', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'User not found'})
        flash('User not found', 'error')
        return redirect(url_for('view_users_list'))
    
    if request.method == 'GET':
        return render_template('edit_user.html', user=user)
    elif request.method == 'POST':
        try:
            user.full_name = request.form['name']
            user.age = int(request.form['age'])
            user.phone = request.form['phone']
            user.address = request.form['address']
            user.email = request.form['email']
            db.session.commit()
            return jsonify({'success': True, 'message': 'User updated successfully'})
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

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Please login.', 'error')
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('view_users_list'))
    db.session.delete(user)
    db.session.commit()
    flash('Deleted successfully', 'success')
    return redirect(url_for('view_users_list'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)