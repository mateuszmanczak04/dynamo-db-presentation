from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Query
from boto3.dynamodb.conditions import Key, Attr

from ..dynamo import get_table

router = APIRouter()


@router.get("/query")
def query_orders_by_customer(customerId: str = Query(..., description="Customer ID, e.g. C001")):
    """
    Scan Orders with FilterExpression on customerId.
    Demonstrates how scanned_count != returned_count — DynamoDB reads all rows before filtering.
    For a true key-based Query, a GSI on customerId would be required.
    """
    table = get_table("Orders")
    result = table.scan(
        FilterExpression=Attr("customerId").eq(customerId),
        ReturnConsumedCapacity="TOTAL",
    )
    return {
        "operation": "Scan + FilterExpression",
        "explanation": (
            "Orders table PK=orderId SK=customerId. "
            "Querying by SK alone requires a GSI. "
            "This Scan reads ALL items then filters — scanned_count shows the true read cost."
        ),
        "customerId": customerId,
        "items": result["Items"],
        "returned_count": result["Count"],
        "scanned_count": result["ScannedCount"],
    }


@router.get("/scan")
def scan_products():
    """
    Full Scan of Products table — reads every item regardless of key.
    scanned_count == returned_count because no filter is applied.
    """
    table = get_table("Products")
    result = table.scan(ReturnConsumedCapacity="TOTAL")
    return {
        "operation": "Scan",
        "explanation": "Full table scan — reads every item. Cost scales with table size, not result size.",
        "items": result["Items"],
        "returned_count": result["Count"],
        "scanned_count": result["ScannedCount"],
    }


@router.get("/filter")
def scan_with_filter(
    category: Optional[str] = Query(None, description="Filter by category, e.g. Electronics"),
    maxPrice: Optional[float] = Query(None, description="Filter products with price <= maxPrice"),
):
    """
    Scan + FilterExpression on Products.
    scanned_count > returned_count illustrates that DynamoDB reads everything before filtering.
    """
    table = get_table("Products")

    filter_expr = None
    applied_filters = []

    if category:
        filter_expr = Attr("category").eq(category)
        applied_filters.append(f"category = {category}")

    if maxPrice is not None:
        price_filter = Attr("price").lte(Decimal(str(maxPrice)))
        filter_expr = price_filter if filter_expr is None else filter_expr & price_filter
        applied_filters.append(f"price <= {maxPrice}")

    kwargs: dict = {"ReturnConsumedCapacity": "TOTAL"}
    if filter_expr is not None:
        kwargs["FilterExpression"] = filter_expr

    result = table.scan(**kwargs)

    return {
        "operation": "Scan + FilterExpression",
        "explanation": (
            "DynamoDB scans the entire table, THEN applies the filter in memory. "
            "scanned_count reflects actual read units consumed — not the number of items returned."
        ),
        "filters": applied_filters,
        "items": result["Items"],
        "returned_count": result["Count"],
        "scanned_count": result["ScannedCount"],
    }
