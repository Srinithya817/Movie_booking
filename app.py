from flask import Flask, render_template, request, redirect, url_for, session, flash
import qrcode
import os
import uuid
import hashlib
from config import get_connection
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey123")

os.makedirs('static/images', exist_ok=True)

IMAGE_MAP = {
    'Leo': 'leo.jpg',
    'Pushpa 2': 'pushpa2.jpg',
    'Jawan': 'jawan.jpg',
    'Kalki 2898 AD': 'kalki.jpg',
    'Vikram': 'vikram.jpg'
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def format_time(time_str):
    try:
        time_str = str(time_str)
        if ':' in time_str:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            am_pm = "AM" if hours < 12 else "PM"
            hours_12 = hours if 1 <= hours <= 12 else abs(hours - 12)
            if hours_12 == 0:
                hours_12 = 12
            return f"{hours_12}:{minutes:02d} {am_pm}"
    except:
        pass
    return time_str

def get_booked_seats(show_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Seat_No FROM Seat_Lock WHERE Show_Id = %s", (show_id,))
    booked = [row[0] for row in cursor.fetchall()]
    conn.close()
    return booked

# ─── AUTH ───────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        password = hash_password(request.form['password'])
        mobile = request.form['mobile']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Customer (F_Name, L_Name, Email_id, Password, Mobile_no) VALUES (%s,%s,%s,%s,%s)",
                (fname, lname, email, password, mobile)
            )
            conn.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
            print("ERROR:", e)
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Customer WHERE Email_id=%s AND Password=%s", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['Cust_id']
            session['user_name'] = user['F_Name']
            session['user_email'] = user['Email_id']
            flash(f"Welcome back, {user['F_Name']}!", 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# ─── MOVIES ─────────────────────────────────────────────

@app.route('/')
def index():
    search = request.args.get('search', '').strip()
    language = request.args.get('language', '').strip()
    genre = request.args.get('genre', '').strip()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM Movie WHERE 1=1"
    params = []
    if search:
        query += " AND Movie_Title LIKE %s"
        params.append(f"%{search}%")
    if language:
        query += " AND Language = %s"
        params.append(language)
    if genre:
        query += " AND Genre = %s"
        params.append(genre)

    cursor.execute(query, params)
    movies = cursor.fetchall()

    cursor.execute("SELECT DISTINCT Language FROM Movie")
    languages = [r['Language'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT Genre FROM Movie")
    genres = [r['Genre'] for r in cursor.fetchall()]
    conn.close()

    return render_template('index.html', movies=movies, languages=languages,
                           genres=genres, search=search,
                           selected_language=language, selected_genre=genre)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Movie WHERE Movie_Id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.execute("SELECT * FROM Movie_Show1 WHERE Movie_Id = %s", (movie_id,))
    shows = cursor.fetchall()
    for show in shows:
        show['Formatted_Time'] = format_time(show['Show_Time'])
    conn.close()
    return render_template('movie_detail.html', movie=movie, shows=shows, image_map=IMAGE_MAP)

# ─── BOOKING ────────────────────────────────────────────

@app.route('/book', methods=['GET', 'POST'])
def book_show():
    if 'user_id' not in session:
        flash('Please log in to book tickets.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'GET':
        show_id = request.args.get('show_id')
        if not show_id:
            return redirect(url_for('index'))
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ms.*, m.Movie_Title, m.Movie_Id
            FROM Movie_Show1 ms
            JOIN Movie m ON ms.Movie_Id = m.Movie_Id
            WHERE ms.Show_Id = %s
        """, (show_id,))
        show = cursor.fetchone()
        conn.close()
        if not show:
            return redirect(url_for('index'))
        show['Formatted_Time'] = format_time(show['Show_Time'])
        booked_seats = get_booked_seats(show_id)
        session['current_show'] = {
            'show_id': show_id,
            'movie_title': show['Movie_Title'],
            'movie_id': show['Movie_Id'],
            'theatre_name': show['Theatre_Name'],
            'city': show['City'],
            'show_time': show['Formatted_Time']
        }
        return render_template('book_ticket.html', show=show,
                               movie={'Movie_Title': show['Movie_Title']},
                               booked_seats=booked_seats)

    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        seats = request.form['selected_seats']
        price = request.form['total_price']
        current_show = session.get('current_show', {})
        session['booking_data'] = {'name': name, 'email': email, 'seats': seats, 'price': price}
        return render_template('payment.html', name=name, email=email,
                               seats=seats, price=price, show=current_show,
                               movie_title=current_show.get('movie_title', 'Movie'))

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    booking_data = session.get('booking_data', {})
    current_show = session.get('current_show', {})
    show_id = current_show.get('show_id')
    seats_str = booking_data.get('seats', '')
    booking_ref = uuid.uuid4().hex[:8].upper()

    # Save booked seats
    if seats_str and show_id:
        conn = get_connection()
        cursor = conn.cursor()
        for seat in seats_str.split(','):
            seat = seat.strip()
            if seat:
                try:
                    cursor.execute("INSERT INTO Seat_Lock (Show_Id, Seat_No) VALUES (%s, %s)", (show_id, seat))
                except:
                    pass
        conn.commit()

        # Save booking record
        ticket_qr_filename = f"ticket_{uuid.uuid4().hex[:8]}.png"
        ticket_qr_path = os.path.join('static', 'images', ticket_qr_filename)
        qr_data = f"BookMyMovie\nRef: {booking_ref}\nMovie: {current_show.get('movie_title')}\nTheatre: {current_show.get('theatre_name')}\nTime: {current_show.get('show_time')}\nSeats: {seats_str}"
        qrcode.make(qr_data).save(ticket_qr_path)

        cursor.execute("""
            INSERT INTO Booking (Cust_id, Show_Id, Seats, Total_Price, Booking_Ref, QR_Path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], show_id, seats_str,
              booking_data.get('price', 0), booking_ref, ticket_qr_filename))
        conn.commit()
        conn.close()

    movie_image = IMAGE_MAP.get(current_show.get('movie_title', ''), 'leo.jpg')
    return render_template('success.html',
                           movie_title=current_show.get('movie_title', 'Movie'),
                           theatre_name=current_show.get('theatre_name', ''),
                           show_time=current_show.get('show_time', ''),
                           seats=seats_str,
                           price=booking_data.get('price', ''),
                           qr_path=ticket_qr_filename,
                           movie_image=movie_image,
                           booking_ref=booking_ref,
                           user_name=session.get('user_name', ''))

# ─── MY BOOKINGS ────────────────────────────────────────

@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        flash('Please log in to view your bookings.', 'warning')
        return redirect(url_for('login'))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, ms.Theatre_Name, ms.City, ms.Show_Date, ms.Show_Time,
               m.Movie_Title, m.Language
        FROM Booking b
        JOIN Movie_Show1 ms ON b.Show_Id = ms.Show_Id
        JOIN Movie m ON ms.Movie_Id = m.Movie_Id
        WHERE b.Cust_id = %s
        ORDER BY b.Booked_At DESC
    """, (session['user_id'],))
    bookings = cursor.fetchall()
    for b in bookings:
        b['Formatted_Time'] = format_time(b['Show_Time'])
    conn.close()
    return render_template('my_bookings.html', bookings=bookings, image_map=IMAGE_MAP)

# ─── ADMIN ──────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == os.getenv('ADMIN_PASSWORD', 'admin123'):
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Wrong password.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM Booking")
    total_bookings = cursor.fetchone()['total']
    cursor.execute("SELECT SUM(Total_Price) as revenue FROM Booking")
    revenue = cursor.fetchone()['revenue'] or 0
    cursor.execute("SELECT COUNT(*) as total FROM Customer")
    total_users = cursor.fetchone()['total']
    cursor.execute("""
        SELECT b.*, m.Movie_Title, ms.Theatre_Name, c.F_Name, c.Email_id
        FROM Booking b
        JOIN Movie_Show1 ms ON b.Show_Id = ms.Show_Id
        JOIN Movie m ON ms.Movie_Id = m.Movie_Id
        LEFT JOIN Customer c ON b.Cust_id = c.Cust_id
        ORDER BY b.Booked_At DESC LIMIT 20
    """)
    bookings = cursor.fetchall()
    cursor.execute("SELECT * FROM Movie")
    movies = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', total_bookings=total_bookings,
                           revenue=revenue, total_users=total_users,
                           bookings=bookings, movies=movies)

@app.route('/admin/add_movie', methods=['POST'])
def add_movie():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Movie (Movie_Title, Movie_Description, Movie_Stars, Language, Genre, Rating, Duration)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (request.form['title'], request.form['description'], request.form['stars'],
          request.form['language'], request.form['genre'],
          request.form['rating'], request.form['duration']))
    conn.commit()
    conn.close()
    flash('Movie added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
