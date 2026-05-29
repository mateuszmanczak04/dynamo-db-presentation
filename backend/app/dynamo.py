import os
import boto3

ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

_client = None
_resource = None


def get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "dynamodb",
            endpoint_url=ENDPOINT,
            region_name=REGION,
        )
    return _client


def get_resource():
    global _resource
    if _resource is None:
        _resource = boto3.resource(
            "dynamodb",
            endpoint_url=ENDPOINT,
            region_name=REGION,
        )
    return _resource


def get_table(name: str):
    return get_resource().Table(name)
