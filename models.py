# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 1. The Restaurant (The Tenant)
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # We never store plain passwords!
    
    # Relationships
    tables = relationship("Table", back_populates="restaurant")
    menu_items = relationship("MenuItem", back_populates="restaurant")

# 2. The Physical Table (Where the QR Code lives)
class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    qr_code_url = Column(String)  # We will generate and save the link here later
    
    # Foreign Key: Which restaurant does this table belong to?
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    
    restaurant = relationship("Restaurant", back_populates="tables")
    orders = relationship("Order", back_populates="table")

# 3. The Menu (The Food)
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    is_vegetarian = Column(Boolean, default=True) # Important for India!
    is_available = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    
    restaurant = relationship("Restaurant", back_populates="menu_items")

# 4. The Order (The Cart)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PENDING") # PENDING, PAID, PREPARING, COMPLETED
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    table_id = Column(Integer, ForeignKey("tables.id"))
    
    table = relationship("Table", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

# 5. Order Items (The specific items in a cart)
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, default=1)
    notes = Column(String, nullable=True) # e.g. "Extra spicy", "No onions"

    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")