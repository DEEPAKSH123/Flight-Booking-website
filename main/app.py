import email
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL configuration
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="deepak123",
    database="data"
)
cursor = db_connection.cursor()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        password = request.form['password']
        
        # Insert data into the database
        query = "INSERT INTO Users (Username, Email, PhoneNumber, Password) VALUES (%s, %s, %s, %s)"
        values = (username, email, phonenumber, password)
        cursor.execute(query, values)
        db_connection.commit()
        
        return redirect(url_for('signin'))
    return render_template('signup.html')

# Signin route
from flask_mail import Mail,Message
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "deepakshkarkala@gmail.com"
app.config["MAIL_PASSWORD"] = "vjwckkarkxphwkpy"
mail=Mail(app)       
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None  # Initialize error message
    if request.method == 'POST':
        # Extract form data
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials in the database
        query = "SELECT * FROM Users WHERE Username = %s"
        values = (username,)
        cursor.execute(query, values)
        user = cursor.fetchone()
        
        if user and user[4] == password:
            # Set session data upon successful authentication
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password"
    return render_template('signin.html', error=error)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('home'))

from datetime import datetime

def query_flights(source_city, destination, date, economic_class):
    # Query flights based on source city, destination, date, and economic class
    query = """
    SELECT fb.*, f.seats_available, f.total_seats, f.unique_code
FROM flight_schedules fb
INNER JOIN flights f ON fb.flight_name = f.flight_name
WHERE fb.source_city = %s
AND fb.destination = %s
AND fb.date = %s
AND fb.economic_class = %s
    """
    
    values = (source_city, destination, date, economic_class)
    
    cursor.execute(query, values)
    matched_flights = cursor.fetchall()
    print(matched_flights)
    print(matched_flights)
    return matched_flights



@app.route('/flight_results',methods=['GET', 'POST'])
def flight_results():
    # Retrieve form data from URL parameters
    source_city = request.args.get('source_city')
    destination = request.args.get('destination')
    date = request.args.get('date')
    economic_class = request.args.get('economic_class')
    
    # Perform database query to fetch flights based on form data
    # Replace this with your actual database query
    matched_flights = query_flights(source_city, destination, date, economic_class)
    print(matched_flights)
    # Render the flight results template with matched flights
    return render_template('flight_results.html', matched_flights=matched_flights)

@app.route('/book_flights',methods=['GET', 'POST'])
def book_flights():
    if request.method == 'POST':
        # Retrieve data from the form
        source_city = request.form['source_city']
        destination = request.form['destination']
        date = request.form['date']
        economic_class = request.form['economic_class']
        
        # Redirect to the flight search results page with form data as URL parameters
        return redirect(url_for('flight_results', source_city=source_city, destination=destination, date=date, economic_class=economic_class))
    
    # If the method is GET, render the book_flights.html template
    return render_template('book_flights.html')
 
# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'username' in session:
        # Fetch user data based on session
        username = session['username']
        # You can fetch additional user data from the database if needed

        # Pass user data to the template
        user = {'username': username}  # You can add more user data here
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('signin'))



# Function to insert booking details into the userbookings table
def insert_booking(username, source_city, destination, date, departure_time, arrival_time, economic_class, flight_name, num_tickets,price):
    # Connect to MySQL database
    db_connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="deepak123",
        database="data"
    )

    # Create a MySQL cursor
    cursor = db_connection.cursor()

    # SQL query to insert booking details into the userbookings table
    sql = "INSERT INTO userbookings (username, source_city, destination, date, departure_time, arrival_time, economic_class, flight_name, num_tickets,price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    values = (username, source_city, destination, date, departure_time, arrival_time, economic_class, flight_name, num_tickets,price)

    # Execute the SQL query
    cursor.execute(sql, values)

    # Commit changes to the database
    db_connection.commit()

    # Close the cursor and database connection
    cursor.close()
    db_connection.close()


# Assuming you have a User model, you need to define a user loader function
#from your_application import User

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    if request.method == 'POST':
        # Retrieve form data
        source_city = request.form['sourceCity']
        destination = request.form['destination']
        date = request.form['date']
        departure_time = request.form['departureTime']
        arrival_time = request.form['arrivalTime']
        economic_class = request.form['economicClass']
        flight_name = request.form['flightName']
        num_tickets = request.form['numTickets']
        price=request.form['Price']
        
        # Retrieve username from session
        username = session.get('username')
        print(economic_class)
        # Fetch user details from the database based on the username
        query = "SELECT * FROM Users WHERE Username = %s"
        cursor.execute(query, (username,))
        user_details = cursor.fetchone()
        print(user_details)
        tp=int(num_tickets)*float(price)
        
        if user_details:
            # Insert booking details into the database
            insert_booking(username, source_city, destination, date, departure_time, arrival_time, economic_class, flight_name, num_tickets,tp)
            msg_body="Thank You for Booking in our website.You have booked "+num_tickets+" tickets\n Per ticket price "+price+"\ntotal price is "+ str(int(num_tickets)*float(price))+"\nyour booking details are:\nusername:"+username+"\nsource-city:"+source_city+"\ndestination city:"+destination+"\ndate:"+date+"\ndeparture time:"+departure_time+"\narrival time:"+arrival_time+"\nclass:"+economic_class+"\nflight name:"+flight_name+"\nnumber of tickets:"+num_tickets+"\nThank you please provide rating in our website"
            # Further processing or database operations can be performed here
            msg=Message(subject="Flight ticket booking details",sender=app.config["MAIL_USERNAME"],recipients=[user_details[2],],body=msg_body)    
            mail.send(msg)
            # Redirect to the confirmation page
            return redirect(url_for('confirmation_page'))
        else:
            # Handle case when user details are not found
            return "User details not found."

#from pymongo import MongoClient
@app.route('/view_booked_tickets')
def view_booked_tickets():
    # Logic to fetch and display previously booked tickets
    username = session.get('username')
        
        # Fetch user details from the database based on the username
    query = "SELECT * FROM userbookings WHERE Username = %s"
    cursor.execute(query, (username,))
    bookings = cursor.fetchall()
    #print(bookings)
    # Pass the bookings data to the template for rendering
    return render_template('view_booked_tickets.html', bookings=bookings)

@app.route('/provide_rating')
def provide_rating():
    # Logic to provide rating
    return render_template('provide_rating.html')

@app.route('/confirmation')
def confirmation_page():
    # Render the confirmation page

    return render_template('confirmation.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Fetch username and password from the form
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user data from the database
        cursor = db_connection.cursor()
        query = "SELECT * FROM admin WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        # Check if user exists and password is correct
        if user:
            # Redirect to the page where you can view users and bookings
            return redirect(url_for('admin_dashboard'))
        else:
            # Display an error message if authentication fails
            error_message = "Invalid username or password. Please try again."
            return render_template('admin_login.html', error=error_message)
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # Render the admin dashboard template
    return render_template('admin_dashboard.html')

@app.route('/view_users_and_bookings')
def view_users_and_bookings():
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM userbookings")
    userbookings_data = cursor.fetchall()
    # Logic to view users and bookings
    #print(userbookings_data)
    return render_template('view_users_and_bookings.html', userbookings=userbookings_data)

@app.route('/view_user_details')
def view_user_details():
    # Logic to fetch user details from the database
    # For demonstration purposes, let's assume some dummy data
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users")
    user_details= cursor.fetchall()
    return render_template('user_details.html', user_details=user_details)

@app.route('/update_flight_schedules', methods=['GET', 'POST'])
def update_flight_schedules():
    if request.method == 'POST':
        # Form data submitted for update
        schedule_id = request.form['schedule_id']  # Assuming 'schedule_id' is the name of the input field in your HTML form
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        class_name = request.form['class']
        flight_name = request.form['flight_name']


        # Update the schedule in the database
        cursor = db_connection.cursor()
        # Assume source, destination, date, departure_time, arrival_time, class_name, and flight_name are obtained from the form
        cursor.execute("UPDATE flight_schedules SET source_city = %s, destination = %s, date = %s, departure_time = %s, arrival_time = %s, economic_class = %s,flight_name=%s WHERE schedule_id = %s",
               (source, destination, date, departure_time, arrival_time, class_name, flight_name,schedule_id))

        db_connection.commit()
        cursor.close()

        return redirect(url_for('update_flight_schedules'))  # Redirect to the same route after update
    else:
        # Fetch existing flight schedules from the database
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM flight_schedules")
        flight_schedules = cursor.fetchall()
        cursor.close()

        return render_template('update_flight_schedules.html', flight_schedules=flight_schedules)

@app.route('/update_flight_details', methods=['GET', 'POST'])
def update_flight_details():
    if request.method == 'POST':
        # Form data submitted for update
        flight_id = request.form['flight_id'] 
        flight_name = request.form['flight_name'] # Assuming 'schedule_id' is the name of the input field in your HTML form
        unique_code = request.form['unique_code']
        seats_available = request.form['seats_available']
        total_seats = request.form['total_seats']
        
       


        # Update the schedule in the database
        cursor = db_connection.cursor()
        # Assume source, destination, date, departure_time, arrival_time, class_name, and flight_name are obtained from the form
        cursor.execute("UPDATE flights SET seats_available = %s, total_seats = %s, unique_code= %s,flight_name=%s WHERE flight_id = %s",
               (seats_available, total_seats, unique_code, flight_name,flight_id))

        db_connection.commit()
        cursor.close()

        return redirect(url_for('update_flight_details'))  # Redirect to the same route after update
    else:
        # Fetch existing flight schedules from the database
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM flights")
        flight_schedules = cursor.fetchall()
        cursor.close()

        return render_template('update_flight_details.html', flight_schedules=flight_schedules)
@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    # Retrieve flight details from the URL parameters
    sourceCity = request.args.get('sourceCity')
    destination = request.args.get('destination')
    date = request.args.get('date')
    departureTime = request.args.get('departureTime')
    arrivalTime = request.args.get('arrivalTime')
    economicClass = request.args.get('economicClass')
    flightName = request.args.get('flightName')
    seatsAvailable = request.args.get('seatsAvailable')
    totalSeats = request.args.get('totalSeats')
    uniqueCode = request.args.get('uniqueCode')
    Price=request.args.get('Price')
    #print(uniqueCode)
    # Render the ticket.html template with flight details
    return render_template('ticket.html', sourceCity=sourceCity, destination=destination, date=date,
                           departureTime=departureTime, arrivalTime=arrivalTime, economicClass=economicClass,
                           flightName=flightName, seatsAvailable=seatsAvailable, totalSeats=totalSeats,
                           uniqueCode=uniqueCode,Price=Price)



if __name__ == '__main__':
    app.run(debug=True)
