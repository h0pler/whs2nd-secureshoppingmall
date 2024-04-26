from fastapi import FastAPI, HTTPException
from typing import List, Optional
import sqlite3
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn=create_connection()
    create_tables(conn)
    if not get_user_by_username(conn,"admin"):
        register_admin(conn,"admin","admin","Admin User")
    yield
    conn.close()

app = FastAPI(lifespan=lifespan)

def create_connection(): #create connection to sqlite db
    conn = sqlite3.connect('shopping_mall.db') #db name is shopping_mall.db
    return conn

def create_tables(conn): #create two tables
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT,
            address TEXT,
            payment_info TEXT
        )
    ''') #create 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            thumbnail_url TEXT
        )
    ''') #create 'products' table
    conn.commit()

def add_user(conn, username, password, role, full_name, address, payment_info): #add normal user to db
    cursor = conn.cursor()
    #username, password, role, full_name, address, payment_info -> 'users' table
    cursor.execute(f'INSERT INTO users (username, password, role, full_name, address, payment_info) VALUES (?, ?, ?, ?, ?, ?)',
                   (username, password, role, full_name, address, payment_info))
    conn.commit() #apply to database
    user = {"username": username, "password": password, "role": role, "full_name": full_name, "address": address, "payment_info": payment_info}
    return {"message": "User created successfully!", "user": user} #return success message and user info

def register_admin(conn, username, password, full_name): #register admin 
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)',
                   (username, password, 'admin', full_name))
    conn.commit() #apply to database
    user = {"username": username, "password": password, "role": 'admin', "full_name": full_name}
    return {"message": "Admin registered successfully!", "user": user} #return success message and admin info

def authenticate_user(conn, username, password): #authenticate user
    cursor = conn.cursor()
    #search user using 'username' and 'password'
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone() #get data from db
    if user:
        #database -> array
        user_info = {"username": user[1], "password": user[2], "role": user[3], "full_name": user[4], "address": user[5], "payment_info": user[6]}
        return {"message": f"Welcome back, {username}!", "user": user_info} #welcome message when auth success
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password") #401 error when user auth fail

def get_all_products(conn): #get information about all products
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products') #select everything
    products = cursor.fetchall() #get data from db
    #return product array
    return [{"name": product[1], "category": product[2], "price": product[3], "thumbnail_url": product[4]} for product in products] #return everything in 'products' table

def add_product(conn, name, category, price, thumbnail_url): #add product 
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (name, category, price, thumbnail_url) VALUES (?, ?, ?, ?)', (name, category, price, thumbnail_url))
    conn.commit() #apply to database
    return {"message": "Product added successfully!"} #success message

def update_user_info(conn, username, full_name, address, payment_info): #update user
    cursor = conn.cursor()
    #update user info in database
    cursor.execute('UPDATE users SET full_name = ?, address = ?, payment_info = ? WHERE username = ?', (full_name, address, payment_info, username))
    conn.commit() #apply to database
    return {"message": "User information updated successfully!"} #success message

def get_user_by_username(conn, username): #search user
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,)) #search database by username
    return cursor.fetchone() #get data from db and return it

@app.post("/register") #POST -> register
#data -> username, password, role, full_name, address(optional), payment info(optional)
async def register_user(username: str, password: str, role: str, full_name: str, address: Optional[str] = None, payment_info: Optional[str] = None):
    conn = create_connection()
    result = add_user(conn, username, password, role, full_name, address, payment_info) #add user info to database
    conn.close()
    return result

@app.post("/login") #POST -> login
async def login(username: str, password: str): #data -> username, password
    conn = create_connection()
    result = authenticate_user(conn, username, password) #search database and authenticate
    conn.close()
    return result

@app.get("/products", response_model=List[dict]) #GET -> products
async def get_products():
    conn = create_connection()
    products = get_all_products(conn) #all products
    conn.close()
    return products

@app.post("/add_product") #POST -> add_product
#data -> name, category, price, thumbnail_url
async def add_new_product(name: str, category: str, price: float, thumbnail_url: str):
    conn = create_connection()
    result = add_product(conn, name, category, price, thumbnail_url) #add product info to database
    conn.close()
    return result

@app.put("/update_user_info") #PUT -> update_user_info
#data -> username, full_name, address, payment_info
async def update_user_info_endpoint(username: str, full_name: str, address: str, payment_info: str):
    conn = create_connection()
    result = update_user_info(conn, username, full_name, address, payment_info) #update user info in database
    conn.close()
    return result
