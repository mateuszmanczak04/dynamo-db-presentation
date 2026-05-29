# CLAUDE.md — DynamoDB Demo

## Project Purpose
Demo stack for DynamoDB presentations. Four Docker services: DynamoDB Local, FastAPI backend, Caddy frontend, Caddy gateway. All traffic via gateway on port 8080 — no CORS needed.

## Stack
- **DynamoDB**: `amazon/dynamodb-local` — sharedDb mode, data volume
- **Backend**: Python 3.12 + FastAPI + boto3, port 3000 (internal only)
- **Frontend**: Vanilla HTML/CSS/JS served by Caddy, port 80 (internal only)
- **Gateway**: Caddy, port 8080 (host-published) — routes `/api/*` → backend, `*` → frontend

## Key Files
```
docker-compose.yml          — service definitions
Makefile                    — up/down/seed/wipe/logs
gateway/Caddyfile           — reverse proxy rules
backend/app/main.py         — FastAPI app, table creation on startup
backend/app/dynamo.py       — boto3 client/resource singleton
backend/app/seed.py         — sample dataset (20 products, 15 orders)
backend/app/routes/products.py  — CRUD /api/products
backend/app/routes/orders.py    — CRUD /api/orders
backend/app/routes/demo.py      — /api/demo/scan|filter|query
frontend/index.html         — single-page UI
frontend/js/app.js          — all frontend logic
frontend/css/style.css      — dark theme
```

## DynamoDB Schema
- **Products**: PK=`productId` (S), GSI `CategoryIndex` on `category`
- **Orders**: PK=`orderId` (S), SK=`customerId` (S)

## API Conventions
- All routes prefixed `/api` (gateway strips nothing — FastAPI uses `root_path="/api"`)
- Decimal types used for DynamoDB price fields (boto3 requirement)
- `GET /api/orders/{id}` requires `?customerId=` query param (composite key)
- `DELETE /api/orders/{id}` requires `?customerId=` query param

## Development Workflow
```bash
make up    # build + start all 4 services
make seed  # load sample data
make logs  # tail all logs
make down  # teardown + remove volumes
```

## Adding New Features
- New route file in `backend/app/routes/`, import + include in `main.py`
- Frontend: add tab button + section in `index.html`, wire up in `app.js`
- New table: add creation logic in `main.py` `create_tables()`, add seed data in `seed.py`

## Constraints
- No CORS config — do not add it; the gateway handles same-origin routing
- Keep frontend vanilla (no bundlers, no frameworks) — this is a demo, simplicity matters
- DynamoDB Local does not enforce IAM; credentials in env are dummy values
- `amazon/dynamodb-local` exposes port 8000 internally only (not published to host)
