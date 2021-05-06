import os
import io
from google.cloud import datastore,vision
from google.cloud.vision_v1 import types
from flask import Flask, render_template, redirect, url_for, request,make_response
from flask_login import login_user
# from .forms import LoginForm
from typing import Union
# from models import User
from google.auth.transport import requests
import google.oauth2.id_token
import datetime


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# @app.route("/login", methods=['GET','POST'])

def create_client(project_id):
    return datastore.Client(project_id)


def add_rooms(room_id:str,room_number:int, room_type: str, room_price:int ):
    client = datastore.Client()
    task = datastore.Entity(client.key("Rooms"))

    # Apply new field values and save the Task entity to Datastore
    task.update(
        {
            # "created": datetime.datetime.utcnow(),
            "room_id":room_id,
            "room_number": room_number,
            "room_type": room_type,
            "room_price":room_price,
            "status": False,
        }
    )
    client.put(task)
    return task.key

def add_bookings(customer_id:str,room_id :str,room_number:int,checkIn_time:str,checkOut_time:str):
    client = datastore.Client()
    task = datastore.Entity(client.key("Bookings"))

    # Apply new field values and save the Task entity to Datastore
    task.update(
        {

            "book_time": datetime.datetime.utcnow(),
            "room_id": room_id,
            "room_number": room_number,
            "checkIn_time": checkIn_time,
            "checkOut_time": checkOut_time,
            "customer_id": customer_id,

        }
    )
    client.put(task)
    return task.key


def add_customer(customer_id: str,customer_name:str):
    client = datastore.Client()
    task = datastore.Entity(client.key("Customers"))

    # Apply new field values and save the Task entity to Datastore
    task.update(
        {
            "book_time": datetime.datetime.utcnow(),
            "customer_id": customer_id,
            "customer_name": customer_name,
            
        }
    )
    client.put(task)
    return task.key

def mark_done(client: datastore.Client, task_id: Union[str, int]):
    with client.transaction():
        # Create a key for an entity of kind "Task", and with the supplied
        # `task_id` as its Id
        key = client.key("Task", task_id)
        # Use that key to load the entity
        task = client.get(key)

        if not task:
            raise ValueError(f"Task {task_id} does not exist.")

        # Update a field indicating that the associated
        # work has been completed
        task["done"] = True

        # Persist the change back to Datastore
        client.put(task)

# @app.route('/book_room', methods=['POST','GET'])
# def bookings():
#     room_id = "ZXZX4747"
#     customer_id = "ZASD20HT5"
    
#     if id_token:
#         try:
#             claims = google.oauth2.id_token.verify_firebase_token(id_token,
#             firebase_request_adapter)
#             room_number = request.form.get('room_number')
#             room_type = request.form.get('room_type')
#             room_price = request.form.get('room_price')
#             checkIn_time = request.form.get('checkIn_time')
#             checkOut_time = request.form.get('checkOut_time')

#             add_bookings(customer_id,room_id,room_number,checkIn_time,checkOut_time)

#         except ValueError as exc:
#             print(str(exc))

#     return  render_template('page/book_room.html',user_data=claims,error_message=error_message)


@app.route('/new_room', methods=['POST','GET'])
def new_room():
    id_token = request.cookies.get("token")
    print(f"Token: {id_token}")
    client = None
    error_message = None
    claims = None

    room_id = "ZXZX4747"
    customer_id = "ZASD20HT5"
    room_number = request.form.get('room_number')
    room_type = request.form.get('room_type')
    room_price = request.form.get('room_price')
    print(room_number)

    add_rooms(room_id,room_number, room_type, room_price)
    
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
            firebase_request_adapter)

            

        except ValueError as exc:
            print(str(exc))

    return  render_template('page/new_room.html',user_data=claims,error_message=error_message)
 
def fetch_rooms():
    client = datastore.Client()
    # Create a query against all of your objects of kind "Task"
    query = client.query(kind="Rooms")
    allRooms = query.fetch()
    return allRooms

def viewBookings():
    client = datastore.Client()
    # Create a query against all of your objects of kind "Task"
    query = client.query(kind="Bookings")
    all_bookings = query.fetch()
    return all_bookings

def fetch_times(limit):
     query = datastore_client.query(kind='visit')
     query.order = ['-timestamp']
     times = query.fetch(limit=limit)
     return times


def store_time(dt):
     entity = datastore.Entity(key = datastore_client.key('visit'))
     entity.update({'timestamp' : dt})
     datastore_client.put(entity)

@app.route('/')
def home():

    return render_template('page/index.html')


@app.route('/delete')
def delete_booking():

    from google.cloud import datastore

    # For help authenticating your client, visit
    # https://cloud.google.com/docs/authentication/getting-started
    client = datastore.Client()
    query = client.query(kind="Bookings")
    all_bookings = query.fetch(id )
    print(id)

    key = client.key("Bookings","5667525748588544")
    print(key)
    delete = client.delete(key)
    return "Item deleted"
        
   
    # # Create a key for an entity of kind "Task", and with the supplied
    # # `task_id` as its Id
    # key = client.key("Bookings", task_id)
    # # Use that key to delete its associated document, if it exists
    # client.delete(key)


@app.route('/bookings')
def view_bookings():

    booked = None
    id_token = request.cookies.get("token")
    client = None
    error_message = None
    claims = None
    booked = viewBookings()
    

    if id_token:

        try:
            print("hello")
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            
        except ValueError as exe:
            error_message = str(exe)  
    print (booked)    
    return  render_template('page/bookings_view.html',user_data=claims,booked = booked, error_message=error_message)

@app.route('/rooms')
def root():

    id_token = request.cookies.get("token")
    client = None
    error_message = None
    claims = None
    allRooms = None
    allRooms = fetch_rooms()
    if id_token:

        try:
            print("hello")
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
            
        except ValueError as exe:
            error_message = str(exe)  
    return  render_template('page/index.html',user_data=claims,allRooms = allRooms, error_message=error_message)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)