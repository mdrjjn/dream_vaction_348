import mysql.connector
import pdb
import sys
from app import connection_info
import random

from flask import render_template, request, url_for, make_response
from app import app


@app.route("/")
def home():
    return render_template('index.html')

@app.route("/avail_flights", methods=["GET", "POST"])
def show_flights():
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                              host=connection_info.MyHost,
                              database=connection_info.MyDatabase)
    cursor = cnx.cursor()
    query = "select * from flight;"
    cursor.execute(query)
    flights = []
    for row in cursor:
        flight = {
            'flight_id':row[0],
            'airline_id':row[1],
            'aircraft_id':row[2],
            'depart_airport_id':row[3],
            'arrival_airport_id':row[4],
            'remaining_seats':row[5]
        }
        flights.append(flight)
    # pdb.set_trace()
    cursor.close()
    cnx.close() 
    return render_template('avail_flights.html', flights=flights)

@app.route("/current_reservations", methods=["GET", "POST"])
def current_reservations():
    uid = request.cookies.get('userID')
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                                  host=connection_info.MyHost,
                                  database=connection_info.MyDatabase)
    cursor = cnx.cursor()

    #TODO FIX THE INJECTION
    cursor.execute("select * from ticket where passenger_id = " + uid)
    tickets = []
    for row in cursor:
        ticket = {
            'ticket_id':row[0],
            'flight_id' : row[2]
        }
        tickets.append(ticket)
    cursor.close()
    cnx.close()
    return render_template('reservations.html', tickets=tickets)

@app.route("/book_flight", methods=["GET", "POST"])
def book_flight():
    uid = request.cookies.get('userID')
    fid = request.form["f_id"]
    
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                                  host=connection_info.MyHost,
                                  database=connection_info.MyDatabase)
    cursor = cnx.cursor()

    add_ticket = "INSERT INTO ticket "\
            "(passenger_id, flight_id)"\
            "VALUES (%s, %s)"
    ticket_data = (int(uid), int(fid))
    cursor.execute(add_ticket, ticket_data)
    cnx.commit()
    cursor.close()
    cnx.close()
    
    return render_template('ticket_confirm.html')

@app.route("/cancel_flight", methods=["GET", "POST"])
def cancel_flight():
    tid = request.form["t_id"]
    
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                                  host=connection_info.MyHost,
                                  database=connection_info.MyDatabase)
    cursor = cnx.cursor()
    
    get_ticket = "SELECT * FROM ticket "\
                    "WHERE ticket_id = %s"
    cursor.execute(get_ticket, (int(tid),))
    fid = cursor.fetchone()[2]
    
    remove_ticket = "DELETE FROM ticket "\
                    "WHERE ticket_id = %s"
    cursor.execute(remove_ticket, (int(tid),))
    cnx.commit()
    cursor.close()
    cnx.close()
    
    return render_template('cancel_flight.html', fid = fid)

@app.route("/login", methods=["GET", "POST"])
def login():
    uid = request.form["user_id"]
    resp = make_response(render_template('menu.html'))
    resp.set_cookie('userID', uid)
    return resp

@app.route("/logout", methods=["GET", "POST"])
def logout():
    uid = request.cookies.get('userID')
    resp = make_response(render_template('index.html'))
    resp.set_cookie('userID', uid, max_age=0)
    return resp


@app.route("/menu", methods=["GET", "POST"])
def menu():
    return render_template('menu.html')

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template('signup.html')
    else:
        uid = random.randrange(0, 10000, 1)
        fname = request.form["first_name"]
        lname = request.form["last_name"]

        # pdb.set_trace()
        cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                                  host=connection_info.MyHost,
                                  database=connection_info.MyDatabase)
        cursor = cnx.cursor()

        add_user = "INSERT INTO passenger "\
               "(uid, first_name, last_name)"\
               "VALUES (%s, %s, %s)"
        user_data = (uid, fname, lname)
        cursor.execute(add_user, user_data)
        cnx.commit()
        cursor.close()
        cnx.close()
        
        return render_template('su_confirm.html', uid=uid)

