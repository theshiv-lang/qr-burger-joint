from database import SessionLocal
import models

db = SessionLocal()

print("🍔 Cooking up the new menu...")

# A full vegetarian menu 
new_items = [
    {"name": "Paneer Tikka Wrap", "price": 180, "desc": "Grilled paneer wrapped in a whole wheat roti.", "veg": True},
    {"name": "Classic French Fries", "price": 120, "desc": "Crispy golden fries with sea salt.", "veg": True},
    {"name": "Veg Margherita Pizza", "price": 299, "desc": "Wood-fired crust with fresh basil and mozzarella.", "veg": True},
    {"name": "Cold Coffee", "price": 150, "desc": "Thick, creamy blended cold coffee.", "veg": True},
    {"name": "Spicy Veggie Burger", "price": 200, "desc": "Crispy vegetable patty with spicy mayo.", "veg": True}
]

for item in new_items:
    # Check if it already exists so we don't make duplicates
    exists = db.query(models.MenuItem).filter(models.MenuItem.name == item["name"]).first()
    if not exists:
        db_item = models.MenuItem(
            name=item["name"], 
            price=item["price"], 
            description=item["desc"], 
            is_vegetarian=item["veg"],
            restaurant_id=1
        )
        db.add(db_item)

db.commit()
db.close()
print("✅ Full menu added to the database!")