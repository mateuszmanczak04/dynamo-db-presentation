# Presentation Script — DynamoDB Demo (8 min)

---

## Overview

| #  | Topic                        | Time   | Cumulative |
|----|------------------------------|--------|------------|
| 1  | Intro + Docker start         | 1:00   | 1:00       |
| 2  | AWS SDK config               | 0:45   | 1:45       |
| 3  | Table creation               | 1:00   | 2:45       |
| 4  | Seed dataset                 | 0:30   | 3:15       |
| 5  | CRUD operations              | 1:30   | 4:45       |
| 6  | Query vs Scan                | 1:30   | 6:15       |
| 7  | FilterExpression             | 0:45   | 7:00       |
| 8  | NoSQL Workbench              | 0:45   | 7:45       |
| 9  | Wrap-up                      | 0:15   | 8:00       |

---

## 1. Intro + Docker Start — 1:00

**Screen:** terminal, `docker-compose.yml`

Open `docker-compose.yml`. Point out:
- `amazon/dynamodb-local` image — official AWS image, runs locally, no AWS account needed
- `-sharedDb` flag — single database file, all clients share the same state
- `dynamodb-data` volume — data persists across restarts
- Only `gateway:8080` is published; DynamoDB is internal only

```bash
make up
# docker compose up --build -d
```

Watch logs briefly:
```bash
make logs
# show backend health check passing
```

**Say:** "Four containers start: DynamoDB Local, FastAPI backend, a Caddy static server for the frontend, and a Caddy gateway that routes all traffic. The gateway is why we have no CORS config — everything arrives on the same origin."

---

## 2. AWS SDK Config — 0:45

**Screen:** `backend/app/dynamo.py`

```python
boto3.client(
    "dynamodb",
    endpoint_url=ENDPOINT,   # http://dynamodb:8000
    region_name=REGION,
)
```

**Say:** "This is the only change needed to point the AWS SDK at DynamoDB Local — override `endpoint_url`. Credentials are dummy values; DynamoDB Local doesn't enforce IAM."

Show env vars in `docker-compose.yml`:
```yaml
AWS_ACCESS_KEY_ID: local
AWS_SECRET_ACCESS_KEY: local
AWS_DEFAULT_REGION: us-east-1
DYNAMODB_ENDPOINT: http://dynamodb:8000
```

**Say:** "Same pattern for AWS CLI — just add `--endpoint-url http://localhost:8000`."

---

## 3. Table Creation — 1:00

**Screen:** `backend/app/main.py` — `create_tables()` function

Point out Products table definition:
```python
client.create_table(
    TableName="Products",
    KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
    ...
    GlobalSecondaryIndexes=[{
        "IndexName": "CategoryIndex",
        "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
        ...
    }],
)
```

**Say:** "DynamoDB only cares about key attributes at table creation time. Non-key attributes — name, price, stock — don't appear in the schema. You just write them."

Point out Orders table:
```python
KeySchema=[
    {"AttributeName": "orderId",    "KeyType": "HASH"},
    {"AttributeName": "customerId", "KeyType": "RANGE"},
]
```

**Say:** "Orders has a composite key — partition key `orderId` plus sort key `customerId`. This lets us do range queries within a partition. We'll come back to why this matters."

Point out `lifespan` handler:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_dynamodb()
    create_tables()
    yield
```

**Say:** "Tables are created on startup if they don't exist — idempotent. The backend waits for DynamoDB to be ready before starting."

---

## 4. Load Sample Dataset — 0:30

**Screen:** terminal, then browser

```bash
make seed
# curl -s -X POST http://localhost:8080/api/seed | jq
```

Show output: `{ "message": "Sample data loaded", "products": 20, "orders": 15 }`

Open **http://localhost:8080** — Products table fills in.

**Screen:** `backend/app/seed.py` — briefly scroll

**Say:** "20 products across 4 categories, 15 orders across 3 customers. Each product uses `Decimal` for the price — boto3 requires it for DynamoDB Number types."

---

## 5. CRUD Operations — 1:30

**Screen:** browser — Products tab

### GetItem
Click a product row, note the ID.

**Say:** "Under the hood this is `GetItem` — a direct key lookup. O(1) cost regardless of table size."

Open `backend/app/routes/products.py`, show:
```python
result = table.get_item(Key={"productId": product_id})
```

### PutItem
Click **+ Add Product**, fill in a new product (e.g. `P099`, "Test Laptop", Electronics, $999, 5).

**Say:** "PutItem writes the entire item. If an item with this key already exists it is replaced — no partial update."

Show in code:
```python
table.put_item(Item=_to_item(product))
```

### UpdateItem
Click **✏️** on any product, change the price, save.

**Say:** "UpdateItem modifies only the specified attributes — the item is not replaced."

Show in code:
```python
table.update_item(
    Key={"productId": product_id},
    UpdateExpression="SET #f_price = :price",
    ...
    ReturnValues="ALL_NEW",
)
```

### DeleteItem
Click **🗑️** on the product just created.

**Say:** "DeleteItem requires the full key. For Orders that means both `orderId` and `customerId`."

---

## 6. Query vs Scan — 1:30

**Screen:** browser — Demo tab

### Scan
Click **Run Scan**.

Point at the result:
- `operation: Scan`
- `scanned_count: 20`
- `returned_count: 20`

**Say:** "Scan reads every item in the table sequentially. Cost is proportional to table size, not result size. On a real table with millions of items this is expensive and slow."

### FilterExpression on Orders (Query demo)
Select customer **C001**, click **Run Query**.

Point at result:
- `scanned_count: 15`
- `returned_count: 5`

**Say:** "We wanted orders for C001 — got 5 back, but DynamoDB read all 15 first. `scanned_count` is what you pay for."

**Say:** "This is because `customerId` is our sort key, not the partition key. To do a real key-based Query on `customerId` alone we'd need a GSI — a Global Secondary Index. Without it, every query by customer is a full Scan."

**Show code** in `backend/app/routes/demo.py`:
```python
table.scan(
    FilterExpression=Attr("customerId").eq(customerId),
    ReturnConsumedCapacity="TOTAL",
)
```

**Say:** "The filter runs after DynamoDB has already read everything. Read units are consumed on the scan, not on the results."

---

## 7. FilterExpression — 0:45

**Screen:** browser — Demo tab, Scan + FilterExpression card

Select category **Electronics**, click **Run Filter**.

Point at result:
- `scanned_count: 20`
- `returned_count: 5`
- `filters: ["category = Electronics"]`

**Say:** "Same story — 20 items read, 5 returned. DynamoDB charged for 20."

Add max price **50**, click **Run Filter** again.

**Say:** "Multiple expressions are combined with `&`. Still a full scan — the filter does not reduce read cost."

Show code:
```python
filter_expr = Attr("category").eq(category)
price_filter = Attr("price").lte(Decimal(str(maxPrice)))
filter_expr = filter_expr & price_filter

result = table.scan(FilterExpression=filter_expr, ...)
```

**Say:** "Use FilterExpression to reduce data transferred over the network — but never as a substitute for proper key design."

---

## 8. NoSQL Workbench — 0:45

**Screen:** browser — NoSQL Workbench tab (show connection instructions), then switch to NoSQL Workbench app

Steps to show:
1. Open NoSQL Workbench → Amazon DynamoDB → Add connection → DynamoDB local → port **8000** → Connect
2. Click **Products** table → browse items
3. Show the `CategoryIndex` GSI in the table details

**Say:** "NoSQL Workbench gives you a visual query builder and lets you inspect the GSI projections. For access pattern design it's the recommended starting point before writing any code."

---

## 9. Wrap-Up — 0:15

**Say:** "DynamoDB Local is identical API surface to production — everything shown here works unchanged against a real table. The only difference is endpoint URL and credentials."

---

## Pre-Demo Checklist

- [ ] `make up` and wait for all containers healthy
- [ ] Open http://localhost:8080 in browser — status badge green
- [ ] `make seed` — tables populated
- [ ] NoSQL Workbench open and connected
- [ ] Terminal visible (split screen or second monitor)
- [ ] Bump terminal + browser font size for screen sharing
