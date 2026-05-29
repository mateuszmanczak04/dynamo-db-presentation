# DynamoDB Demo

Self-contained demo stack for a DynamoDB presentation. Runs entirely locally via Docker Compose — no AWS account required.

## Quick Start

```bash
make up      # build and start all services
make seed    # load 20 products + 15 orders
```

Open **http://localhost:8080**

```bash
make down    # stop and remove containers + volumes
```

## Architecture

```
Browser → http://localhost:8080
             │
             ▼
         ┌─────────┐
         │ gateway │  Caddy :8080
         └────┬────┘
              │ /api/*          everything else
              ▼                       ▼
        ┌──────────┐          ┌──────────────┐
        │ backend  │          │   frontend   │
        │ FastAPI  │          │  Caddy :80   │
        │  :3000   │          │ static files │
        └────┬─────┘          └──────────────┘
             │
             ▼
     ┌───────────────┐
     │ dynamodb-local│
     │   :8000       │
     └───────────────┘
```

### Services

| Service  | Image               | Internal port | Description                              |
|----------|---------------------|---------------|------------------------------------------|
| dynamodb | amazon/dynamodb-local | 8000        | DynamoDB Local with `-sharedDb`           |
| backend  | python:3.12-slim    | 3000          | FastAPI REST API + boto3                 |
| frontend | caddy:alpine        | 80            | Static HTML/CSS/JS                       |
| gateway  | caddy:alpine        | **8080**→host | Reverse proxy — same-origin routing      |

Only the gateway port (8080) is published. All inter-service traffic stays on a Docker bridge network.

## DynamoDB Tables

### Products

| Attribute   | Type | Role                  |
|-------------|------|-----------------------|
| productId   | S    | PK (Partition Key)    |
| name        | S    |                       |
| category    | S    | GSI: CategoryIndex PK |
| price       | N    |                       |
| stock       | N    |                       |
| description | S    |                       |

### Orders

| Attribute  | Type | Role                    |
|------------|------|-------------------------|
| orderId    | S    | PK (Partition Key)      |
| customerId | S    | SK (Sort Key)           |
| productId  | S    |                         |
| quantity   | N    |                         |
| status     | S    | pending / shipped / delivered |
| totalPrice | N    |                         |
| createdAt  | S    | ISO 8601                |

## REST API

Base URL: `http://localhost:8080/api`

OpenAPI docs: **http://localhost:8080/api/docs**

### Products

| Method | Path                | Operation   | DynamoDB call |
|--------|---------------------|-------------|---------------|
| GET    | /products           | List all    | Scan          |
| GET    | /products/{id}      | Get one     | GetItem       |
| POST   | /products           | Create      | PutItem       |
| PUT    | /products/{id}      | Update      | UpdateItem    |
| DELETE | /products/{id}      | Delete      | DeleteItem    |

### Orders

| Method | Path                          | Operation | DynamoDB call |
|--------|-------------------------------|-----------|---------------|
| GET    | /orders                       | List all  | Scan          |
| GET    | /orders/{id}?customerId=C001  | Get one   | GetItem       |
| POST   | /orders                       | Create    | PutItem       |
| DELETE | /orders/{id}?customerId=C001  | Delete    | DeleteItem    |

### Seed

| Method | Path   | Effect                                    |
|--------|--------|-------------------------------------------|
| POST   | /seed  | Load 20 products + 15 orders (idempotent) |
| DELETE | /seed  | Wipe all data from both tables            |

### Demo Endpoints

| Method | Path                                    | Demonstrates                          |
|--------|-----------------------------------------|---------------------------------------|
| GET    | /demo/scan                              | Full Scan — reads every item          |
| GET    | /demo/filter?category=Electronics       | Scan + FilterExpression               |
| GET    | /demo/filter?maxPrice=50                | Scan + FilterExpression on price      |
| GET    | /demo/query?customerId=C001             | Scan + Filter (shows GSI need)        |

All demo endpoints return `scanned_count` and `returned_count` to illustrate read cost.

## Sample Dataset

**20 products** across 4 categories: Electronics, Clothing, Books, Home

**15 orders** across 3 customers: C001, C002, C003 — statuses: pending, shipped, delivered

## Makefile Targets

```bash
make up     # docker compose up --build -d
make down   # docker compose down -v
make seed   # POST /api/seed
make wipe   # DELETE /api/seed
make logs   # docker compose logs -f
```

## Presentation Topics Covered

| Topic                          | Where                                            |
|--------------------------------|--------------------------------------------------|
| DynamoDB Local via Docker      | `docker-compose.yml` — `amazon/dynamodb-local`   |
| AWS CLI / SDK config           | Backend env vars + Workbench tab in UI           |
| Creating tables                | `backend/app/main.py` — `lifespan` handler       |
| Loading a sample dataset       | `backend/app/seed.py` + `make seed`              |
| PutItem / GetItem / DeleteItem | Products and Orders CRUD panels                  |
| Query vs Scan                  | Demo tab — scan + filter comparison              |
| FilterExpression               | Demo tab — category and price filters            |
| NoSQL Workbench                | Workbench tab — connection instructions          |

## NoSQL Workbench

1. Open NoSQL Workbench → *Amazon DynamoDB* → *Add connection*
2. Select **DynamoDB local**, port **8000**
3. Click **Connect**

AWS CLI example:
```bash
aws dynamodb list-tables \
  --endpoint-url http://localhost:8000 \
  --region us-east-1
```

Environment: `AWS_ACCESS_KEY_ID=local`, `AWS_SECRET_ACCESS_KEY=local`, `AWS_DEFAULT_REGION=us-east-1`
