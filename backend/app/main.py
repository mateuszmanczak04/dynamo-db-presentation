import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .dynamo import get_client
from .routes import products, orders, demo
from . import seed as seed_module


def create_tables():
    client = get_client()
    existing = set(client.list_tables()["TableNames"])

    if "Products" not in existing:
        client.create_table(
            TableName="Products",
            KeySchema=[{"AttributeName": "productId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "productId", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "CategoryIndex",
                    "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                }
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    if "Orders" not in existing:
        client.create_table(
            TableName="Orders",
            KeySchema=[
                {"AttributeName": "orderId", "KeyType": "HASH"},
                {"AttributeName": "customerId", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "orderId", "AttributeType": "S"},
                {"AttributeName": "customerId", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )


def wait_for_dynamodb(retries: int = 10, delay: float = 2.0):
    client = get_client()
    for attempt in range(retries):
        try:
            client.list_tables()
            return
        except Exception:
            if attempt < retries - 1:
                time.sleep(delay)
    raise RuntimeError("DynamoDB Local did not become available")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_dynamodb()
    create_tables()
    yield


app = FastAPI(
    title="DynamoDB Demo API",
    description="CRUD + demo endpoints for DynamoDB Local presentation",
    version="1.0.0",
    root_path="/api",
    lifespan=lifespan,
)

app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(demo.router, prefix="/demo", tags=["demo"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


@app.post("/seed", tags=["seed"])
def load_seed():
    result = seed_module.load_all()
    return {"message": "Sample data loaded", **result}


@app.delete("/seed", tags=["seed"])
def wipe_seed():
    result = seed_module.wipe_all()
    return {"message": "All data wiped", **result}
