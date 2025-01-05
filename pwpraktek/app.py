from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = config.DATABASE_CONFIG['host']
app.config['MYSQL_USER'] = config.DATABASE_CONFIG['user']
app.config['MYSQL_PASSWORD'] = config.DATABASE_CONFIG['password']
app.config['MYSQL_DB'] = config.DATABASE_CONFIG['database']

mysql = MySQL(app)

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_by_username = cursor.fetchone()
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_by_email = cursor.fetchone()

        if user_by_username:
            flash('Username sudah terdaftar, silakan pilih yang lain.', 'danger')
        elif user_by_email:
            flash('Email sudah terdaftar, silakan pilih yang lain.', 'danger')
        else:
            cursor.execute("INSERT INTO users (username, email, role, password_hash) VALUES (%s, %s, %s, %s)", 
               (username, email, role, password_hash))
            mysql.connection.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))

        cursor.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email dan password tidak boleh kosong.', 'danger')
            return redirect(url_for('login'))

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, role, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[4], password): 
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            flash('Login berhasil!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email atau password salah.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: 
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, role, email FROM users")
    users = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, role, password_hash) VALUES (%s, %s, %s, %s)",
                       (username, email, role, password_hash))
        mysql.connection.commit()
        cursor.close()
        flash('Pengguna berhasil ditambahkan.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_user.html')

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']

        cursor.execute("UPDATE users SET username = %s, email = %s, role = %s WHERE id = %s",
                       (username, email, role, id))
        mysql.connection.commit()
        cursor.close()
        flash('Pengguna berhasil diperbarui.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Pengguna berhasil dihapus.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
