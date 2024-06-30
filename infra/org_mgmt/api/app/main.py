#! /usr/bin/env python3
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Union
from enum import Enum

app = FastAPI(
    title="Quiet Riot",
    version="2.0",
    description="A tool used for enumerating valid data about AWS, Azure, and GCP.",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Wesley Ladd",
        "email": "wsladd@icloud.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html",
    },
    docs_url="/documentation",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

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

@app.get("/live")
async def live():
    return {"status": "alive"}

@app.post("/query")
async def query(request: QueryRequest):
    # Placeholder for actual query logic
    if not request.principal_value:
        raise HTTPException(status_code=400, detail="Invalid principal value")
    return {"principal_type": request.principal_type, "principal_value": request.principal_value, "status": "queried"}

@app.post("/bulk-query")
async def bulk_query(request: BulkQueryRequest):
    # Placeholder for actual bulk query logic
    if not request.principal_values:
        raise HTTPException(status_code=400, detail="Invalid principal values")
    return {"principal_values": request.principal_values, "status": "bulk queried"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
