from database import SessionLocal
import models

db = SessionLocal()

print("🛠️ Setting up your restaurant tables...")

# Check if Table 5 already exists
existing_table = db.query(models.Table).filter(models.Table.id == 5).first()

if not existing_table:
    # We force id=5 because your QR code points to Table 5
    # and your frontend uses the number in the URL as the ID.
    table_five = models.Table(
        id=5, 
        table_number=5, 
        restaurant_id=1, 
        qr_code_url="http://127.0.0.1:8000/menu/1/5"
    )
    db.add(table_five)
    db.commit()
    print("✅ Table 5 created successfully!")
else:
    print("ℹ️ Table 5 already exists.")

db.close()