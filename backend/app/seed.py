from decimal import Decimal
from .dynamo import get_table

# ── original 20 hand-crafted products ────────────────────────────────────────

_BASE_PRODUCTS = [
    {"productId": "P001", "name": "Wireless Headphones", "category": "Electronics", "price": Decimal("79.99"), "stock": 50, "description": "Over-ear noise-cancelling headphones"},
    {"productId": "P002", "name": "Mechanical Keyboard", "category": "Electronics", "price": Decimal("129.99"), "stock": 30, "description": "TKL layout, Cherry MX switches"},
    {"productId": "P003", "name": "USB-C Hub", "category": "Electronics", "price": Decimal("39.99"), "stock": 100, "description": "7-in-1 hub with HDMI, USB-A, SD card"},
    {"productId": "P004", "name": "Webcam 1080p", "category": "Electronics", "price": Decimal("59.99"), "stock": 45, "description": "Full HD webcam with built-in mic"},
    {"productId": "P005", "name": "Monitor Stand", "category": "Electronics", "price": Decimal("34.99"), "stock": 60, "description": "Adjustable aluminum monitor riser"},
    {"productId": "P006", "name": "Running Shoes", "category": "Clothing", "price": Decimal("89.99"), "stock": 80, "description": "Lightweight trail running shoes"},
    {"productId": "P007", "name": "Denim Jacket", "category": "Clothing", "price": Decimal("49.99"), "stock": 40, "description": "Classic blue denim jacket"},
    {"productId": "P008", "name": "Cotton T-Shirt", "category": "Clothing", "price": Decimal("19.99"), "stock": 200, "description": "Organic cotton, crew neck"},
    {"productId": "P009", "name": "Wool Sweater", "category": "Clothing", "price": Decimal("69.99"), "stock": 35, "description": "Merino wool, slim fit"},
    {"productId": "P010", "name": "Cargo Pants", "category": "Clothing", "price": Decimal("44.99"), "stock": 55, "description": "Multi-pocket utility pants"},
    {"productId": "P011", "name": "Clean Code", "category": "Books", "price": Decimal("34.99"), "stock": 25, "description": "Robert C. Martin — software craftsmanship"},
    {"productId": "P012", "name": "Designing Data-Intensive Applications", "category": "Books", "price": Decimal("44.99"), "stock": 20, "description": "Martin Kleppmann — distributed systems"},
    {"productId": "P013", "name": "The Pragmatic Programmer", "category": "Books", "price": Decimal("29.99"), "stock": 30, "description": "Hunt & Thomas — developer career guide"},
    {"productId": "P014", "name": "System Design Interview", "category": "Books", "price": Decimal("24.99"), "stock": 40, "description": "Alex Xu — Vol. 1 & 2"},
    {"productId": "P015", "name": "Deep Work", "category": "Books", "price": Decimal("14.99"), "stock": 50, "description": "Cal Newport — focused success"},
    {"productId": "P016", "name": "Desk Lamp", "category": "Home", "price": Decimal("29.99"), "stock": 70, "description": "LED desk lamp with USB charging port"},
    {"productId": "P017", "name": "Coffee Maker", "category": "Home", "price": Decimal("49.99"), "stock": 25, "description": "12-cup programmable coffee maker"},
    {"productId": "P018", "name": "Air Purifier", "category": "Home", "price": Decimal("89.99"), "stock": 20, "description": "HEPA filter, 500 sq ft coverage"},
    {"productId": "P019", "name": "Throw Blanket", "category": "Home", "price": Decimal("24.99"), "stock": 90, "description": "Soft fleece, 50x60 inches"},
    {"productId": "P020", "name": "Bamboo Cutting Board", "category": "Home", "price": Decimal("19.99"), "stock": 110, "description": "Extra-large with juice groove"},
]

# ── 80 generated products (20 per category, IDs P021–P100) ───────────────────

_ELECTRONICS_NAMES = [
    ("Bluetooth Speaker", "Portable, waterproof, 20h battery"),
    ("Smart Watch", "Health tracking, GPS, 5-day battery"),
    ("Laptop Stand", "Foldable aluminum, adjustable height"),
    ("LED Strip Lights", "RGB, WiFi, 5m roll"),
    ("Portable Charger", "20000mAh, dual USB-C"),
    ("Noise-Cancelling Earbuds", "ANC, 30h total battery"),
    ("4K Webcam", "Auto-focus, built-in ring light"),
    ("Gaming Mouse", "16000 DPI, 7 programmable buttons"),
    ("Wireless Charger Pad", "15W fast charge, Qi compatible"),
    ("HDMI Capture Card", "4K60 passthrough, USB-C"),
    ("USB Microphone", "Cardioid condenser, plug-and-play"),
    ("Smart Plug", "WiFi, energy monitoring, voice control"),
    ("E-Reader", "6-inch glare-free display, 6-week battery"),
    ("Keyboard Wrist Rest", "Memory foam, non-slip base"),
    ("Screen Cleaning Kit", "Microfiber cloth + spray, 100ml"),
    ("Cable Management Box", "Hides power strip and cables"),
    ("Mini PC", "Intel N100, 8GB RAM, 256GB SSD"),
    ("Portable SSD", "2TB, USB 3.2 Gen2, 1050 MB/s"),
    ("Drawing Tablet", "8x5 inch, 8192 pressure levels"),
    ("Smart Doorbell", "1080p, motion detection, cloud storage"),
]

_CLOTHING_NAMES = [
    ("Hoodie", "Heavyweight fleece, kangaroo pocket"),
    ("Chino Shorts", "Stretch cotton, 7-inch inseam"),
    ("Polo Shirt", "Pique cotton, slim fit"),
    ("Waterproof Jacket", "3-layer shell, packable"),
    ("Compression Leggings", "High-waist, 4-way stretch"),
    ("Casual Sneakers", "Canvas upper, rubber sole"),
    ("Beanie", "Ribbed knit, one size fits all"),
    ("Oxford Shirt", "Non-iron cotton, button-down collar"),
    ("Athletic Shorts", "Quick-dry, 5-inch inseam"),
    ("Puffer Vest", "Recycled fill, side pockets"),
    ("Swim Trunks", "Quick-dry, mesh liner, 7-inch"),
    ("Flannel Shirt", "100% cotton, relaxed fit"),
    ("Yoga Pants", "4-way stretch, high-rise"),
    ("Leather Belt", "Full-grain, reversible black/brown"),
    ("Crew Socks 6-Pack", "Cushioned sole, moisture-wicking"),
    ("Baseball Cap", "Structured, adjustable strap"),
    ("Slim Fit Chinos", "Stretch, wrinkle-resistant"),
    ("Tank Top 3-Pack", "Cotton-modal blend, ribbed"),
    ("Winter Gloves", "Touchscreen-compatible, fleece lining"),
    ("Dress Socks 5-Pack", "Mercerized cotton, reinforced heel"),
]

_BOOKS_NAMES = [
    ("The Art of Computer Programming", "Knuth — 4 vol. fundamental algorithms"),
    ("Introduction to Algorithms", "CLRS — 4th edition"),
    ("Refactoring", "Martin Fowler — 2nd edition"),
    ("Site Reliability Engineering", "Google SRE book"),
    ("The Phoenix Project", "DevOps novel by Gene Kim"),
    ("Accelerate", "Forsgren et al. — DevOps metrics"),
    ("Domain-Driven Design", "Eric Evans — the blue book"),
    ("Release It!", "Nygard — production-ready software"),
    ("The Staff Engineer's Path", "Tanya Reilly"),
    ("An Elegant Puzzle", "Will Larson — engineering management"),
    ("Software Architecture Patterns", "Mark Richards — O'Reilly"),
    ("Kubernetes in Action", "Marko Luksa — 2nd edition"),
    ("Database Internals", "Alex Petrov — storage engines"),
    ("Distributed Systems", "van Steen & Tanenbaum — 4th ed"),
    ("The Manager's Path", "Camille Fournier"),
    ("A Philosophy of Software Design", "John Ousterhout — 2nd ed"),
    ("Effective Java", "Joshua Bloch — 3rd edition"),
    ("Python Cookbook", "Beazley & Jones — recipes"),
    ("High Performance Python", "Micha Gorelick & Ian Ozsvald"),
    ("Fluent Python", "Luciano Ramalho — 2nd edition"),
]

_HOME_NAMES = [
    ("French Press", "Stainless steel, 34oz, double-walled"),
    ("Wooden Spice Rack", "Holds 20 jars, wall-mounted"),
    ("Blackout Curtains", "100% polyester, noise-reducing"),
    ("Humidifier", "Ultrasonic, 4L tank, whisper-quiet"),
    ("Under-Desk Drawer", "Clamp-on, holds keyboard and more"),
    ("Bedside Organizer", "Hanging caddy, 6 pockets"),
    ("Shower Caddy", "Rust-proof stainless, 3 shelves"),
    ("Laundry Hamper", "Collapsible, 55L, bamboo frame"),
    ("Smart Thermostat", "WiFi, learning schedule, energy report"),
    ("Electric Kettle", "1.7L, 60min keep-warm, variable temp"),
    ("Vegetable Chopper", "14-piece set, dishwasher safe"),
    ("Silicone Baking Mats 2-Pack", "Non-stick, fits half-sheet pan"),
    ("Bamboo Bath Mat", "Anti-slip, moisture-resistant"),
    ("Candle Set 3-Pack", "Soy wax, 50h burn each"),
    ("Door Draft Stopper", "Self-adhesive foam seal, 36-inch"),
    ("Magnetic Knife Strip", "Stainless steel, holds 8 knives"),
    ("Pot and Pan Organizer", "Adjustable rack, 9 dividers"),
    ("Shower Squeegee", "Stainless handle, rubber blade"),
    ("Over-Door Hooks 6-Pack", "No-drill, holds 22 lbs each"),
    ("Wax Melter", "Electric, ceramic dish, 25W"),
]

_GENERATED_ITEMS = [
    (_ELECTRONICS_NAMES, "Electronics", 21, 29.99, 199.99),
    (_CLOTHING_NAMES,    "Clothing",    41, 12.99, 109.99),
    (_BOOKS_NAMES,       "Books",       61,  9.99,  54.99),
    (_HOME_NAMES,        "Home",        81, 14.99,  99.99),
]

_generated: list[dict] = []
import random as _random
_random.seed(42)

for _names, _cat, _start_idx, _min_price, _max_price in _GENERATED_ITEMS:
    for i, (name, desc) in enumerate(_names):
        pid = f"P{_start_idx + i:03d}"
        price = Decimal(str(round(_random.uniform(_min_price, _max_price), 2)))
        stock = _random.randint(5, 150)
        _generated.append({
            "productId": pid,
            "name": name,
            "category": _cat,
            "price": price,
            "stock": stock,
            "description": desc,
        })

PRODUCTS = _BASE_PRODUCTS + _generated

ORDERS = [
    {"orderId": "O001", "customerId": "C001", "productId": "P001", "quantity": 1, "status": "delivered", "totalPrice": Decimal("79.99"), "createdAt": "2024-01-05T10:00:00Z"},
    {"orderId": "O002", "customerId": "C001", "productId": "P011", "quantity": 2, "status": "delivered", "totalPrice": Decimal("69.98"), "createdAt": "2024-01-12T14:30:00Z"},
    {"orderId": "O003", "customerId": "C001", "productId": "P006", "quantity": 1, "status": "shipped", "totalPrice": Decimal("89.99"), "createdAt": "2024-02-01T09:15:00Z"},
    {"orderId": "O004", "customerId": "C001", "productId": "P017", "quantity": 1, "status": "pending", "totalPrice": Decimal("49.99"), "createdAt": "2024-02-20T16:45:00Z"},
    {"orderId": "O005", "customerId": "C001", "productId": "P003", "quantity": 2, "status": "delivered", "totalPrice": Decimal("79.98"), "createdAt": "2024-03-08T11:00:00Z"},
    {"orderId": "O006", "customerId": "C002", "productId": "P002", "quantity": 1, "status": "delivered", "totalPrice": Decimal("129.99"), "createdAt": "2024-01-08T08:00:00Z"},
    {"orderId": "O007", "customerId": "C002", "productId": "P012", "quantity": 1, "status": "delivered", "totalPrice": Decimal("44.99"), "createdAt": "2024-01-25T13:00:00Z"},
    {"orderId": "O008", "customerId": "C002", "productId": "P018", "quantity": 1, "status": "shipped", "totalPrice": Decimal("89.99"), "createdAt": "2024-02-14T10:30:00Z"},
    {"orderId": "O009", "customerId": "C002", "productId": "P009", "quantity": 3, "status": "pending", "totalPrice": Decimal("209.97"), "createdAt": "2024-03-01T15:00:00Z"},
    {"orderId": "O010", "customerId": "C002", "productId": "P016", "quantity": 2, "status": "delivered", "totalPrice": Decimal("59.98"), "createdAt": "2024-03-10T09:00:00Z"},
    {"orderId": "O011", "customerId": "C003", "productId": "P008", "quantity": 5, "status": "delivered", "totalPrice": Decimal("99.95"), "createdAt": "2024-01-15T12:00:00Z"},
    {"orderId": "O012", "customerId": "C003", "productId": "P015", "quantity": 1, "status": "delivered", "totalPrice": Decimal("14.99"), "createdAt": "2024-02-03T14:00:00Z"},
    {"orderId": "O013", "customerId": "C003", "productId": "P004", "quantity": 1, "status": "shipped", "totalPrice": Decimal("59.99"), "createdAt": "2024-02-18T11:30:00Z"},
    {"orderId": "O014", "customerId": "C003", "productId": "P019", "quantity": 2, "status": "pending", "totalPrice": Decimal("49.98"), "createdAt": "2024-03-05T16:00:00Z"},
    {"orderId": "O015", "customerId": "C003", "productId": "P020", "quantity": 1, "status": "delivered", "totalPrice": Decimal("19.99"), "createdAt": "2024-03-12T10:00:00Z"},
]


def load_all():
    products_table = get_table("Products")
    orders_table = get_table("Orders")

    for product in PRODUCTS:
        products_table.put_item(Item=product)

    for order in ORDERS:
        orders_table.put_item(Item=order)

    return {"products": len(PRODUCTS), "orders": len(ORDERS)}


def wipe_all():
    products_table = get_table("Products")
    orders_table = get_table("Orders")

    products = products_table.scan(ProjectionExpression="productId")["Items"]
    for p in products:
        products_table.delete_item(Key={"productId": p["productId"]})

    orders = orders_table.scan(ProjectionExpression="orderId, customerId")["Items"]
    for o in orders:
        orders_table.delete_item(Key={"orderId": o["orderId"], "customerId": o["customerId"]})

    return {"deleted_products": len(products), "deleted_orders": len(orders)}
