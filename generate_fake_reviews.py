import pandas as pd
import random
from faker import Faker

fake = Faker()

# ================== PRODUCT CATALOG ==================
product_catalog = {
    "Clothing": [
        "Cotton T-Shirt", "Denim Jeans", "Leather Jacket", "Sports Shorts", "Wool Sweater",
        "Formal Shirt", "Hoodie", "Chinos", "Maxi Dress", "Polo Shirt", "Cargo Pants", "Bomber Jacket"
    ],
    "Electronics": [
        "Wireless Earbuds", "Smartphone Case", "Bluetooth Speaker", "Laptop Bag", "Smartwatch",
        "Gaming Mouse", "Mechanical Keyboard", "Noise Cancelling Headphones", "Tablet Cover", "Portable Charger"
    ],
    "Accessories": [
        "Leather Belt", "Sunglasses", "Backpack", "Wallet", "Silk Scarf",
        "Wrist Watch", "Beanie Hat", "Travel Duffel Bag", "Keychain", "Umbrella"
    ],
    "Shoes": [
        "Running Shoes", "Leather Boots", "Sneakers", "Sandals", "Formal Shoes",
        "Slip-On Loafers", "High Heels", "Flip Flops", "Climbing Boots", "Canvas Shoes"
    ],
    "Home": [
        "Coffee Maker", "Vacuum Cleaner", "Air Purifier", "Microwave Oven", "Blender",
        "Rice Cooker", "Toaster", "Dish Rack", "Electric Kettle", "Ceiling Fan"
    ],
    "Beauty": [
        "Moisturizing Cream", "Lipstick", "Shampoo", "Perfume", "Hair Dryer",
        "Nail Polish", "Face Mask", "Foundation", "Beard Trimmer", "Sunscreen"
    ],
    "Sports": [
        "Yoga Mat", "Dumbbells", "Tennis Racket", "Football", "Basketball",
        "Cycling Helmet", "Running Shorts", "Swimming Goggles", "Cricket Bat", "Hiking Backpack"
    ],
    "Kitchen": [
        "Non-Stick Frying Pan", "Chef Knife", "Cutting Board", "Blender Jar", "Electric Mixer",
        "Water Bottle", "Stainless Steel Cookware Set", "Measuring Cup Set", "Oven Gloves", "Coffee Grinder"
    ]
}

fulfillment_status = ["Fulfilled", "Pending", "Canceled"]
countries = ["Canada", "USA", "Australia", "UK"]

# ================== REVIEW TEMPLATES ==================
positive_templates = [
    "Absolutely love the {product}, excellent quality and fast delivery.",
    "The {product} exceeded my expectations, will definitely buy again!",
    "Very happy with the {product}, fits perfectly and great value for money.",
    "The {product} arrived on time and works perfectly, highly recommend.",
    "Amazing {product}, customer support was also top-notch.",
    "Great {product}! Exactly as described and worth every penny.",
    "The {product} is perfect for my needs, amazing craftsmanship.",
    "Excellent purchase, the {product} feels premium and durable.",
    "Fast shipping and great quality {product}, could not be happier.",
    "The {product} is stylish and comfortable, I wear it every day.",
    "Superb quality on the {product}, packaging was also great.",
    "Best purchase ever! The {product} is worth every cent.",
    "The {product} came earlier than expected, amazing service.",
    "Highly satisfied, the {product} works even better than advertised.",
    "The {product} looks amazing and is really sturdy.",
    "Perfect fit and great fabric quality on the {product}.",
    "Loved the color and style of the {product}, perfect buy.",
    "A premium {product} with impressive performance.",
    "Everything about this {product} screams quality!",
    "The {product} has become my favorite item."
]

neutral_templates = [
    "The {product} is decent, not too bad but nothing extraordinary.",
    "Average experience with the {product}, works okay but has room for improvement.",
    "The {product} is just fine, delivery took longer than expected.",
    "It's okay, the {product} does the job but quality could be better.",
    "The {product} is acceptable, but I expected slightly better packaging.",
    "Average build quality on the {product}, neither bad nor great.",
    "Neutral experience, the {product} performs as advertised but lacks premium feel.",
    "The {product} is fine but not worth the price in my opinion.",
    "It's usable, but the {product} could have been more comfortable.",
    "Mediocre experience overall, the {product} is serviceable.",
    "The {product} is nothing special, just average.",
    "Got what I ordered, the {product} is okay.",
    "Fairly standard experience, nothing too exciting about the {product}.",
    "Not bad, but the {product} is also not great.",
    "The {product} is fine for casual use, not premium quality.",
    "The {product} works as expected but nothing to brag about.",
    "The {product} does the job but lacks a premium feel.",
    "Neither good nor bad, just okay {product}.",
    "Meh experience with the {product}, nothing memorable.",
    "I feel neutral about this {product}, nothing stands out."
]

negative_templates = [
    "Very poor quality {product}, broke within a week.",
    "The {product} arrived late and was not as described.",
    "Size issue with the {product}, totally unusable.",
    "Disappointed with the {product}, customer support unhelpful.",
    "The {product} is overpriced for such cheap material.",
    "Terrible quality {product}, felt like a waste of money.",
    "The {product} stopped working after just one use, very frustrating.",
    "Extremely dissatisfied with the {product}, will not recommend.",
    "Bad experience, the {product} came with missing parts.",
    "The {product} is flimsy and uncomfortable, regret buying it.",
    "The {product} broke within days, horrible quality.",
    "Worst experience ever, the {product} is a scam.",
    "Customer service ignored my complaint about the {product}.",
    "The {product} feels cheap and unreliable.",
    "Totally not worth it, the {product} is a disaster.",
    "Received the wrong {product}, very disappointed.",
    "The {product} came damaged, packaging was horrible.",
    "Awful experience, will never buy this {product} again.",
    "The {product} is uncomfortable and poorly made.",
    "Waste of money, don't buy this {product}."
]

# ================== GENERATE DATA ==================
data = []
for _ in range(2000):  # Generate 2000 rows
    category = random.choice(list(product_catalog.keys()))
    product_name = random.choice(product_catalog[category])
    rating = random.randint(1, 5)
    
    if rating <= 2:
        template = random.choice(negative_templates)
    elif rating == 3:
        template = random.choice(neutral_templates)
    else:
        template = random.choice(positive_templates)

    review_content = template.format(product=product_name)
    
    data.append({
        "Timestamp": fake.date_between(start_date='-1y', end_date='today'),
        "Shipping Country": random.choice(countries),
        "Product Category": category,
        "Product Name": product_name,
        "Rating": rating,
        "Review Content": review_content,
        "Fulfillment Status": random.choice(fulfillment_status),
        "Order Value": round(random.uniform(10, 500), 2)
    })

# ================== SAVE CSV ==================
df = pd.DataFrame(data)
df.to_csv("raw_reviews.csv", index=False)
print("Generated raw_reviews.csv with 2000 realistic reviews.")
