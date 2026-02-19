from fastapi.responses import HTMLResponse
import os

# main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# 1. Create the Database Tables
# This line is magic. It looks at your models.py file and
# automatically creates the tables in the database if they don't exist.
models.Base.metadata.create_all(bind=engine)

# 2. Initialize the App
app = FastAPI()

# Dependency: This helper function opens a connection to the database
# when a request comes in, and closes it when the request is done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. Our First "Hello World" Endpoint
# This is just to test if the server is working.
@app.get("/")
def read_root():
    return {"message": "Restaurant QR System is Online! 🚀"}

# 4. An Endpoint to Create a Restaurant (Test)
@app.post("/restaurants/")
def create_restaurant(name: str, email: str, db: Session = Depends(get_db)):
    # Create the object
    new_restaurant = models.Restaurant(name=name, email=email)
    # Add to the database session
    db.add(new_restaurant)
    # Commit (save) the changes
    db.commit()
    # Refresh to get the new ID (e.g., ID 1)
    db.refresh(new_restaurant)
    return new_restaurant
# ... (keep your existing imports and create_restaurant code) ...
from pydantic import BaseModel

# 1. We need a "Schema" so FastAPI knows what data to expect for food
class MenuItemCreate(BaseModel):
    name: str
    price: float
    description: str
    is_vegetarian: bool = True

# 2. Endpoint to ADD food to the menu
@app.post("/restaurants/{restaurant_id}/menu/")
def add_menu_item(restaurant_id: int, item: MenuItemCreate, db: Session = Depends(get_db)):
    # Create the food item
    new_item = models.MenuItem(
        name=item.name,
        price=item.price,
        description=item.description,
        is_vegetarian=item.is_vegetarian,
        restaurant_id=restaurant_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

# 3. Endpoint to VIEW the menu (The URL in the QR Code!)
# --- COPY AND PASTE THIS AT THE BOTTOM OF main.py ---

from fastapi.responses import HTMLResponse

# 1. THE DATA ENDPOINT (The "Robot" URL)
# We add "/api" to the front so it doesn't conflict with the website
@app.get("/api/menu/{restaurant_id}/{table_number}")
def get_menu_data(restaurant_id: int, table_number: int, db: Session = Depends(get_db)):
    # This logic stays the same: fetch from database
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    menu_items = db.query(models.MenuItem).filter(models.MenuItem.restaurant_id == restaurant_id).all()
    
    # Return raw JSON data
    return {
        "restaurant": restaurant.name,
        "table": table_number,
        "menu": menu_items
    }

# 2. THE WEBPAGE ENDPOINT (The "Human" URL)
# This matches the QR Code link exactly!
@app.get("/menu/{restaurant_id}/{table_number}", response_class=HTMLResponse)
def get_menu_html(restaurant_id: int, table_number: int):
    # This reads the HTML file and sends it to the browser
    # Make sure you created the "templates" folder and "menu.html" file!
    with open("templates/menu.html", "r") as f:
        return f.read()
    # --- PASTE AT THE BOTTOM OF main.py ---

from typing import List

# 1. Schema for incoming orders
class OrderCreate(BaseModel):
    table_id: int
    item_ids: List[int]  # The list of food IDs (e.g., [1, 2, 2])

@app.post("/orders/")
def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # A. Create a new Order Ticket
    new_order = models.Order(
        table_id=order_data.table_id,
        status="PENDING",
        total_amount=0.0 # We will calculate this later
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # B. Add the items to the ticket
    for item_id in order_data.item_ids:
        order_item = models.OrderItem(
            order_id=new_order.id,
            menu_item_id=item_id
        )
        db.add(order_item)
    
    db.commit()
    return {"status": "Order Sent!", "order_id": new_order.id}

# --- PASTE AT THE BOTTOM OF main.py ---

# 1. Endpoint to GET all orders for the Kitchen

# --- REPLACE your get_orders function in main.py with this ---

@app.get("/restaurants/{restaurant_id}/orders")
def get_orders(restaurant_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).join(models.Table).filter(models.Table.restaurant_id == restaurant_id).all()
    
    results = []
    for order in orders:
        # 1. Count the identical items for this specific table's order
        item_counts = {}
        for order_item in order.items:
            name = order_item.menu_item.name
            if name in item_counts:
                item_counts[name] += 1
            else:
                item_counts[name] = 1
                
        # 2. Format them nicely (e.g., "3x Classic French Fries")
        formatted_items = [f"{count}x {name}" for name, count in item_counts.items()]
            
        results.append({
            "id": order.id,
            "table": order.table.table_number,
            "status": order.status,
            "items": formatted_items,
            "total": order.total_amount
        })
    
    # Reverse the list so newest orders show first
    return results[::-1]

# --- REPLACE THE LAST FUNCTION IN main.py WITH THIS ---

@app.get("/admin", response_class=HTMLResponse)
def get_admin_panel():
    # We added encoding="utf-8" here to fix the emoji crash!
    with open("templates/admin.html", "r", encoding="utf-8") as f:
        return f.read()
    
    # --- PASTE AT THE BOTTOM OF main.py ---

from fastapi import status

@app.post("/orders/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(get_db)):
    # 1. Find the order
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    # 2. Update status
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = "COMPLETED"
    db.commit()
    
    return {"message": "Order completed!"}

# --- PASTE AT THE VERY BOTTOM OF main.py ---

@app.get("/setup")
def setup_database(db: Session = Depends(get_db)):
    # 1. Create the Restaurant
    rest = db.query(models.Restaurant).filter(models.Restaurant.id == 1).first()
    if not rest:
        rest = models.Restaurant(name="Shivam's Burger Joint", email="admin@test.com")
        db.add(rest)
        db.commit()
        
    # 2. Create Table 5
    table = db.query(models.Table).filter(models.Table.table_number == 5).first()
    if not table:
        table = models.Table(table_number=5, restaurant_id=1)
        db.add(table)
        db.commit()
        
    # 3. Cook up the Menu
    new_items = [
        {"name": "Paneer Tikka Wrap", "price": 180, "desc": "Grilled paneer wrapped in a whole wheat roti.", "veg": True},
        {"name": "Classic French Fries", "price": 120, "desc": "Crispy golden fries with sea salt.", "veg": True},
        {"name": "Veg Margherita Pizza", "price": 299, "desc": "Wood-fired crust with fresh basil and mozzarella.", "veg": True},
        {"name": "Cold Coffee", "price": 150, "desc": "Thick, creamy blended cold coffee.", "veg": True},
        {"name": "Spicy Veggie Burger", "price": 200, "desc": "Crispy vegetable patty with spicy mayo.", "veg": True}
    ]
    
    for item in new_items:
        exists = db.query(models.MenuItem).filter(models.MenuItem.name == item["name"]).first()
        if not exists:
            db_item = models.MenuItem(name=item["name"], price=item["price"], description=item["desc"], is_vegetarian=item["veg"], restaurant_id=1)
            db.add(db_item)
            
    db.commit()
    
    return {"message": "✅ Magic Setup Complete! Restaurant, Table 5, and Menu are ready."}