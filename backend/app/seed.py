from decimal import Decimal
from .dynamo import get_table

PRODUCTS = [
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
