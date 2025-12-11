import sqlite3
import json
import random
from database import get_db_connection, init_db

# Base data for generation
# Base data for generation
CATEGORIES = {
    "Clothing": [
        ("Dress", ["Floral Summer Dress", "Silk Wrap Dress", "Velvet Cocktail Dress", "Linen Summer Dress", "Sequined Evening Dress", "Knitted Midi Dress", "Pleated Midi Skirt"]),
        ("Top", ["Ribbed Knit Top", "Silk Blouse", "Cotton T-Shirt", "Linen Casual Shirt", "Oversized Blazer", "Streetwear Hoodie", "Classic Oxford Shirt"]),
        ("Pants", ["Straight-Fit High-Waisted Jeans", "Slim-Fit Jeans", "Chino Pants", "Tailored Trousers", "Wide Leg Jeans", "Cargo Pants"]),
        ("Jacket", ["Bomber Jacket", "Leather Biker Jacket", "Wool Blazer", "Trench Coat", "Puffer Jacket", "Denim Jacket"]),
        ("Suit", ["Navy Wool Suit", "Charcoal Slim Suit", "Tuxedo", "Linen Summer Suit"])
    ],
    "Accessories": [
        ("Bag", ["Leather Tote Bag", "Sleek Backpack", "Small Crossbody Bag", "Velvet Clutch", "Woven Straw Bag"]),
        ("Jewelry", ["Gold Hoops", "Pearl Drop Earrings", "Silver Chain Necklace", "Diamond Studs", "Chunky Bracelet"]),
        ("Eyewear", ["Aviator Sunglasses", "Cat Eye Sunglasses", "Wayfarer", "Round Metal"]),
        ("Scarves", ["Silk Scarf", "Cashmere Wrap", "Wool Scarf", "Patterned Bandana"])
    ],
    "Shoes": [
        ("Heels", ["Block Heels", "Strappy Gold Heels", "Classic Black Pumps", "Nude Kittens"]),
        ("Boots", ["Leather Chelsea Boots", "Suede Ankle Boots", "Knee High Boots", "Combat Boots"]),
        ("Flats", ["Leather Loafers", "Minimal White Sneakers", "Chunky Sneakers", "Ballet Flats", "Espadrilles"])
    ]
}

COLORS = ["Red", "Blue", "Green", "Black", "White", "Beige", "Navy", "Gold", "Silver", "Pink", "Burgundy", "Camel", "Pastel", "Floral"]
ADJECTIVES = ["Elegant", "Casual", "Vintage", "Modern", "Classic", "Bohemian", "Chic", "Minimalist", "Oversized", "Fitted", "Winter", "Summer", "Autumn", "Spring"]

IMAGES = {
    "Dress": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?q=80&w=1000&auto=format&fit=crop",
    "Top": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=1000&auto=format&fit=crop",
    "Pants": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=1000&auto=format&fit=crop",
    "Jacket": "https://images.unsplash.com/photo-1551028919-6016b7af5549?q=80&w=1000&auto=format&fit=crop",
    "Suit": "https://images.unsplash.com/photo-1594938298603-c8148c47e356?q=80&w=1000&auto=format&fit=crop",
    "Bag": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?q=80&w=1000&auto=format&fit=crop",
    "Jewelry": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?q=80&w=1000&auto=format&fit=crop",
    "Eyewear": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=1000&auto=format&fit=crop",
    "Scarves": "https://images.unsplash.com/photo-1520975661595-dc22dd83ca91?q=80&w=1000&auto=format&fit=crop",
    "Shoes": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=1000&auto=format&fit=crop",
    "Heels": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=1000&auto=format&fit=crop",
    "Boots": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?q=80&w=1000&auto=format&fit=crop",
    "Flats": "https://images.unsplash.com/photo-1560343090-f0409e92791a?q=80&w=1000&auto=format&fit=crop",
    "Clothing": "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?q=80&w=1000&auto=format&fit=crop",
    "Accessory": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?q=80&w=1000&auto=format&fit=crop"
}

def generate_products(count=300):
    products = []
    
    # Demographics
    DEMOGRAPHICS = ["Women", "Men", "Girl", "Boy"]
    
    for i in range(count):
        cat = random.choice(list(CATEGORIES.keys()))
        sub_type, item_names = random.choice(CATEGORIES[cat])
        base_name = random.choice(item_names)
        color = random.choice(COLORS)
        adj = random.choice(ADJECTIVES)
        
        # Gender assignment logic
        # Specific items usually map to specific genders, but purely random for generic items
        # Heuristics:
        if any(x in base_name for x in ["Dress", "Skirt", "Blouse", "Heels", "Clutch"]):
            target_demo = random.choice(["Women", "Girl"])
        elif any(x in base_name for x in ["Suit", "Tuxedo", "Oxford"]):
            target_demo = random.choice(["Men", "Boy"])
        else:
            target_demo = random.choice(DEMOGRAPHICS)

        # Refine name based on demo (e.g. "Little Girl's Dress" or "Men's Suit")
        if target_demo in ["Girl", "Boy"]:
            prefix = f"{target_demo}'s"
        else:
            prefix = f"{target_demo}'s" if random.random() > 0.7 else "" # Optional prefix for adults
            
        full_name = f"{adj} {color} {base_name}"
        if prefix:
             full_name = f"{prefix} {full_name}"

        price = round(random.uniform(25.0, 450.0), 2)
        if target_demo in ["Girl", "Boy"]:
            price = round(price * 0.6, 2) # Kids clothes cheaper
        
        # Tags creation
        tags = [cat.lower(), sub_type.lower(), color.lower(), adj.lower(), target_demo.lower(), "fashion"]
        
        if cat == "Clothing":
            tags.append("fashion")
            tags.append("clothes")
            tags.append("women" if random.random() > 0.4 else "men") # Mix of men/women
        if "Wedding" in base_name or "Formal" in tags or "Suit" in base_name or "Evening" in base_name:
            tags.append("formal")
            tags.append("wedding")
        elif "Casual" in base_name or "Hoodie" in base_name or "Sneakers" in base_name:
            tags.append("casual")
            tags.append("streetwear")

        # Fallback image logic
        img_key = sub_type if sub_type in IMAGES else cat
        if img_key not in IMAGES: img_key = "Clothing"
        image = IMAGES.get(img_key)

        product = {
            "id": f"gen_{i+1}",
            "name": full_name,
            "category": cat,
            "price": price,
            "description": f"A stylish {base_name.lower()} for {target_demo}s. Perfect for {tags[-1]} occasions.",
            "tags": json.dumps(tags),
            "stock": random.randint(1, 50),
            "image": image
        }
        products.append(product)
        
    return products

def seed():
    print("Seeding database...")
    init_db()
    conn = get_db_connection()
    
    # Clear existing
    conn.execute("DELETE FROM products")
    
    products = generate_products(250) # Generating 250 items to be safe
    
    for p in products:
        conn.execute('''
            INSERT INTO products (id, name, category, price, description, tags, stock, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p["id"], p["name"], p["category"], p["price"], p["description"], p["tags"], p["stock"], p["image"]))
        
    conn.commit()
    print(f"Seeded {len(products)} products.")
    conn.close()

if __name__ == "__main__":
    seed()
