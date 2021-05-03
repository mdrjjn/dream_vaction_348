import mysql.connector
import pdb
import sys
from app import connection_info
import random

from flask import render_template, request, url_for, make_response, redirect
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
    # query = "select flight_id, airline_name, model, capacity, depart_airport_name, airport_name as arrival_airport_name, remaining_seats from ("\
    #             "select flight_id, airline_name, model, capacity, airport_name as depart_airport_name, arrival_airport_id, remaining_seats from ("\
    #                 "select flight_id, airline_name, model, capacity, depart_airport_id, arrival_airport_id, remaining_seats from ("\
    #                     "select flight_id, airline_name, aircraft_id, depart_airport_id, arrival_airport_id, remaining_seats from flight as F1 join airline as A on F1.airline_id = A.airline_id"\
    #                 ") as F2 join aircraft as C on F2.aircraft_id = C.aircraft_id"\
    #             ") as F3 join airport as P1 on F3.depart_airport_id = P1.airport_id"\
    #         ") as F4 join airport as P2 on F4.arrival_airport_id = P2.airport_id"
    # cursor.execute(query)
    cursor.callproc("getFlight", (-1,))
    flights = []
    for result in cursor.stored_results():
        for row in result.fetchall():
            flight = {
                'flight_id':row[0],
                'airline_name':row[1],
                'aircraft_model':row[2],
                'aircraft_capacity':row[3],
                'depart_airport_name':row[4],
                'arrival_airport_name':row[5],
                'remaining_seats':row[6]
            }
            flights.append(flight)
    cursor.close()
    cnx.close() 
    return render_template('avail_flights.html', flights=flights)

@app.route("/current_reservations", methods=["GET", "POST"])
def current_reservations():
    uid = request.cookies.get('userID')
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                                  host=connection_info.MyHost,
                                  database=connection_info.MyDatabase)
    
    cursor = cnx.cursor(buffered=True)
    cursor.execute("select * from ticket where passenger_id = %s", (uid,))
    tickets = []
    for row in cursor:
        flight_cursor = cnx.cursor()
        flight_cursor.callproc("getFlight", (row[2],))
        for result in flight_cursor.stored_results():
            for flight in result.fetchall():
                ticket = {
                    'ticket_id':row[0],
                    'flight_id':row[2],
                    'airline_name':flight[1],
                    'aircraft_model':flight[2],
                    'aircraft_capacity':flight[3],
                    'depart_airport_name':flight[4],
                    'arrival_airport_name':flight[5],
                    'remaining_seats':flight[6]
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
    cursor = cnx.cursor(prepared=True)

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
    cursor.close()

    cursor = cnx.cursor()
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
    resp = make_response(redirect(url_for("menu")))
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
        cursor = cnx.cursor(prepared=True)

        add_user = "INSERT INTO passenger "\
               "(uid, first_name, last_name)"\
               "VALUES (%s, %s, %s)"
        user_data = (uid, fname, lname)
        cursor.execute(add_user, user_data)
        cnx.commit()
        cursor.close()
        cnx.close()
        
        return render_template('su_confirm.html', uid=uid)

@app.route("/capacity_filter", methods=["GET", "POST"])
def capacity_filter():
    min_cap = request.form["min_capacity"]
    cnx = mysql.connector.connect(user=connection_info.MyUser, password=connection_info.MyPassword,
                              host=connection_info.MyHost,
                              database=connection_info.MyDatabase)
    print(min_cap)
    cursor = cnx.cursor()
    query = "select flight_id, airline_name, model, capacity, depart_airport_name, airport_name as arrival_airport_name, remaining_seats from ( "\
                "select flight_id, airline_name, model, capacity, airport_name as depart_airport_name, arrival_airport_id, remaining_seats from ( "\
                    "select flight_id, airline_name, model, capacity, depart_airport_id, arrival_airport_id, remaining_seats from ( "\
                        "select flight_id, airline_name, aircraft_id, depart_airport_id, arrival_airport_id, remaining_seats "\
                        "from flight as F1 join airline as A on F1.airline_id = A.airline_id "\
                        "where F1.remaining_seats >= %s "\
                    ") as F2 join aircraft as C on F2.aircraft_id = C.aircraft_id "\
                ") as F3 join airport as P1 on F3.depart_airport_id = P1.airport_id "\
            ") as F4 join airport as P2 on F4.arrival_airport_id = P2.airport_id "
    cursor.execute(query, (int(min_cap),))
    flights = []
    for row in cursor:
        flight = {
            'flight_id':row[0],
            'airline_name':row[1],
            'aircraft_model':row[2],
            'aircraft_capacity':row[3],
            'depart_airport_name':row[4],
            'arrival_airport_name':row[5],
            'remaining_seats':row[6]
        }
        flights.append(flight)
    
    cursor.close()
    cnx.close() 
    return render_template('capacity_filter.html', flights=flights)
