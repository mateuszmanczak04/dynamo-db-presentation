from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..dynamo import get_table

router = APIRouter()


class OrderIn(BaseModel):
    orderId: str
    customerId: str
    productId: str
    quantity: int
    status: str
    totalPrice: float
    createdAt: str


def _to_item(o: OrderIn) -> dict:
    return {
        "orderId": o.orderId,
        "customerId": o.customerId,
        "productId": o.productId,
        "quantity": o.quantity,
        "status": o.status,
        "totalPrice": Decimal(str(o.totalPrice)),
        "createdAt": o.createdAt,
    }


@router.get("")
def list_orders():
    table = get_table("Orders")
    result = table.scan()
    return result["Items"]


@router.get("/{order_id}")
def get_order(order_id: str, customerId: str):
    table = get_table("Orders")
    result = table.get_item(Key={"orderId": order_id, "customerId": customerId})
    item = result.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Order not found")
    return item


@router.post("", status_code=201)
def create_order(order: OrderIn):
    table = get_table("Orders")
    table.put_item(Item=_to_item(order))
    return {"orderId": order.orderId}


@router.delete("/{order_id}")
def delete_order(order_id: str, customerId: str):
    table = get_table("Orders")
    table.delete_item(Key={"orderId": order_id, "customerId": customerId})
    return {"deleted": order_id}
