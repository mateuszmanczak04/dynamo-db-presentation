from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key

from ..dynamo import get_table

router = APIRouter()


class ProductIn(BaseModel):
    productId: str
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = ""


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None


def _to_item(p: ProductIn) -> dict:
    return {
        "productId": p.productId,
        "name": p.name,
        "category": p.category,
        "price": Decimal(str(p.price)),
        "stock": p.stock,
        "description": p.description,
    }


@router.get("")
def list_products():
    table = get_table("Products")
    result = table.scan()
    return result["Items"]


@router.get("/{product_id}")
def get_product(product_id: str):
    table = get_table("Products")
    result = table.get_item(Key={"productId": product_id})
    item = result.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item


@router.post("", status_code=201)
def create_product(product: ProductIn):
    table = get_table("Products")
    table.put_item(Item=_to_item(product))
    return {"productId": product.productId}


@router.put("/{product_id}")
def update_product(product_id: str, body: ProductUpdate):
    table = get_table("Products")
    existing = table.get_item(Key={"productId": product_id}).get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        return existing

    set_expr = "SET " + ", ".join(f"#f_{k} = :{k}" for k in updates)
    expr_names = {f"#f_{k}": k for k in updates}
    expr_values = {f":{k}": (Decimal(str(v)) if k == "price" else v) for k, v in updates.items()}

    result = table.update_item(
        Key={"productId": product_id},
        UpdateExpression=set_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW",
    )
    return result["Attributes"]


@router.delete("/{product_id}")
def delete_product(product_id: str):
    table = get_table("Products")
    table.delete_item(Key={"productId": product_id})
    return {"deleted": product_id}
