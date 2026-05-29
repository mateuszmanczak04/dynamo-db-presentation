# Presentation Slides — DynamoDB Demo

Each `---` is a slide boundary.

---

## Slide 1 — Title

**DynamoDB in Practice**
*Local development, CRUD, and access pattern design*

> Subtitle / your name / date

---

## Slide 2 — What is DynamoDB?

**DynamoDB** is AWS's fully managed NoSQL database.

- Key-value + document store (not relational, no SQL)
- Designed for **single-digit millisecond** latency at any scale
- Scales horizontally by distributing data across partitions
- **Serverless pricing** — pay per read/write, not per instance
- No schema for non-key fields — items in the same table can look completely different

> "It forces you to think about access patterns upfront, not after."

---

## Slide 3 — Demo Stack Architecture

```
Browser  ──→  :8080  Caddy Gateway
                         ├── /api/*  ──→  :3000  FastAPI + boto3
                         │                          └── boto3 ──→  :8000  DynamoDB Local
                         └──  *      ──→  :80    Caddy (static HTML/JS)
```

Four Docker containers. Single origin — no CORS.

**DynamoDB Local** = official AWS Docker image. Identical API to production. No AWS account, no billing. Only difference: `endpoint_url`.

```python
boto3.client("dynamodb", endpoint_url="http://dynamodb:8000")
```

---

## Slide 4 — Data Model: Partial Schema

DynamoDB enforces schema **only on key attributes**. Everything else is free-form.

```python
# Table creation — only keys declared
client.create_table(
    TableName="Products",
    KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
    AttributeDefinitions=[
        {"AttributeName": "productId", "AttributeType": "S"},
    ],
)

# At write time — any attributes accepted
table.put_item(Item={
    "productId": "P001",
    "name": "Wireless Headphones",   # ← not in schema
    "price": Decimal("79.99"),        # ← not in schema
    "inStock": True,                  # ← not in schema
})
```

**Available types:** `S` (String), `N` (Number), `B` (Binary), `BOOL`, `NULL`, `L` (List), `M` (Map), `SS/NS/BS` (Sets)

---

## Slide 5 — Keys: Partition Key and Sort Key

**Partition key (HASH)** — mandatory. Hashed → determines physical shard. Like a hash map key. Lookup is O(1).

**Sort key (RANGE)** — optional. Items with same PK sorted by SK within shard. Enables range queries.

| Table    | PK         | SK           | Use case |
|----------|------------|--------------|----------|
| Products | `productId`| —            | Direct lookup by product ID |
| Orders   | `orderId`  | `customerId` | Order + customer composite |

**Key design is your most important decision.** Wrong keys = expensive scans at runtime. You can't change them after creation.

---

## Slide 6 — Global Secondary Index (GSI)

A GSI is a **copy of your table, re-keyed** on different attributes. Maintained automatically.

```
Main index:     productId  →  item
CategoryIndex:  category   →  item   ← GSI
```

Without GSI on `category`:
- "Get all Electronics" = full Scan (read all 100 items, filter)

With `CategoryIndex`:
- "Get all Electronics" = Query (read only the Electronics partition)

```python
client.create_table(
    ...
    GlobalSecondaryIndexes=[{
        "IndexName": "CategoryIndex",
        "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
        "Projection": {"ProjectionType": "ALL"},
    }],
)
```

---

## Slide 7 — CRUD Operations

| Operation | DynamoDB | Behaviour |
|-----------|----------|-----------|
| Read      | `GetItem` | Exact key → O(1). Cheapest. |
| Create    | `PutItem` | Write entire item. **Replaces** if key exists (UPSERT). |
| Update    | `UpdateItem` | Modify specific attributes. Item not replaced. |
| Delete    | `DeleteItem` | Requires full key (PK + SK if composite). |

**Conditional writes** — make PutItem behave like INSERT:
```python
table.put_item(
    Item={...},
    ConditionExpression="attribute_not_exists(productId)"
    # raises ConditionalCheckFailedException if item exists
)
```

**UpdateExpression example:**
```python
table.update_item(
    Key={"productId": "P001"},
    UpdateExpression="SET #price = :price",
    ExpressionAttributeNames={"#price": "price"},  # 'price' is reserved
    ExpressionAttributeValues={":price": Decimal("99.99")},
    ReturnValues="ALL_NEW",
)
```

---

## Slide 8 — Scan vs Query (the core lesson)

|                   | **Scan**                        | **Query**                    |
|-------------------|---------------------------------|------------------------------|
| What it reads     | Every item in the table         | All items in one partition   |
| Filter applied    | After reading everything        | Key condition reduces reads  |
| Cost              | Proportional to **table size**  | Proportional to **result**   |
| Use when          | Migrations, analytics, one-offs | All production access paths  |

**You pay for what DynamoDB reads, not what it returns.**

```
Products: 100 items

Scan (no filter):          scanned=100  returned=100  ✓ fair
Scan + filter Electronics: scanned=100  returned=25   ✗ paid for 75 items you didn't need
Query on CategoryIndex:    scanned=25   returned=25   ✓ paid only for what you got
```

---

## Slide 9 — The Cost of a Bad Access Pattern

DynamoDB on-demand: **$0.25 per million Read Capacity Units**
Eventually consistent read: **0.5 RCU per item** (≤4KB)

**Scenario:** find 25 Electronics products out of 100 total. 100,000 requests/day.

|                    | RCUs/op | $/op        | $/month       |
|--------------------|---------|-------------|---------------|
| Scan (no GSI)      | 50 RCU  | $0.0000125  | **$37.50**    |
| Query (CategoryIndex)| 12.5 RCU | $0.000003125 | **$9.38**   |
| **Savings**        |         |             | **$28.12/mo** |

Scale to 10M items → Scan costs $1,250/month for the same query. Query still costs $9.38.

**Design access patterns before writing code.**

---

## Slide 10 — FilterExpression

A filter applied **in-memory after DynamoDB reads**, before sending to client.

```python
table.scan(
    FilterExpression=Attr("category").eq("Electronics") & Attr("price").lte(Decimal("50"))
)
```

- Reduces **data over the wire** ✓
- Does **NOT** reduce read cost ✗ — you pay for everything scanned

Use `FilterExpression` to cut network payload.  
Use **GSI + Query** to cut read cost.

> "FilterExpression is not a substitute for proper key design."

---

## Slide 11 — Live Demo

**What we'll show:**
1. `make up` → four containers start
2. AWS SDK config — one line to point at DynamoDB Local
3. Table creation — schema for keys only
4. `make seed` → 100 products, 15 orders
5. CRUD: GetItem, PutItem, UpdateItem, DeleteItem
6. Scan vs FilterExpression — watch `scanned_count` vs `returned_count`
7. Cost estimates live in the UI
8. NoSQL Workbench — visual GSI inspection

---

## Slide 12 — Key Takeaways

1. **DynamoDB Local** = production API, zero AWS setup
2. **Schema = keys only** — non-key attributes are free-form documents
3. **GetItem is O(1)** — hash on partition key, direct shard lookup
4. **You pay for scanned_count**, not returned_count
5. **Scan = full table read** every time — avoid in production hot paths
6. **GSI solves non-key access patterns** — maintain alternate indexes at write time
7. **Access patterns first** — design keys around how you query, not how data is structured
8. To go to production: remove `endpoint_url`, add real credentials. That's it.

---

## Slide 13 — Resources (optional / backup)

- [DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)
- [NoSQL Workbench (free download)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/workbench.html)
- [DynamoDB Local Docker image](https://hub.docker.com/r/amazon/dynamodb-local)
- [Alex DeBrie — The DynamoDB Book](https://www.dynamodbbook.com/) — best deep-dive resource
- [DynamoDB pricing calculator](https://aws.amazon.com/dynamodb/pricing/on-demand/)
- boto3 docs: `Table.get_item`, `Table.put_item`, `Table.update_item`, `Table.scan`, `Table.query`
