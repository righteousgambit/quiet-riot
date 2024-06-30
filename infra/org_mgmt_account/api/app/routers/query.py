from fastapi import APIRouter
from enum import Enum
from pydantic import BaseModel
from typing import List, Union

router = APIRouter()

class PrincipalType(str, Enum):
    AWS_ACCOUNT_IDS = "AWS Account IDs"
    MICROSOFT_365_DOMAINS = "Microsoft 365 Domains"
    AWS_SERVICES_FOOTPRINTING = "AWS Services Footprinting"
    AWS_ROOT_USER_EMAIL_ADDRESS = "AWS Root User E-mail Address"
    AWS_IAM_PRINCIPALS = "AWS IAM Principals"
    IAM_ROLES = "IAM Roles"
    IAM_USERS = "IAM Users"
    MICROSOFT_365_USERS = "Microsoft 365 Users (e-mails)"
    GOOGLE_WORKSPACE_USERS = "Google Workspace Users (e-mails)"


class QueryRequest(BaseModel):
    principal_type: PrincipalType
    principal_value: str


class BulkQueryRequest(BaseModel):
    principal_values: List[str]

@router.post("/query")
async def query(request: QueryRequest):
    # Placeholder for actual query logic
    if not request.principal_value:
        raise HTTPException(status_code=400, detail="Invalid principal value")
    return {
        "principal_type": request.principal_type,
        "principal_value": request.principal_value,
        "status": "queried",
    }


@router.post("/bulk-query")
async def bulk_query(request: BulkQueryRequest):
    # Placeholder for actual bulk query logic
    if not request.principal_values:
        raise HTTPException(status_code=400, detail="Invalid principal values")
    return {"principal_values": request.principal_values, "status": "bulk queried"}
