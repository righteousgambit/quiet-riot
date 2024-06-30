#! /usr/bin/env python3
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.logging import configure_logging
from config.connections import AWSConnections, aws_connections
from routers import query, live

# Using the AWSConnections class to create SQS and DynamoDB clients
sqs_client = aws_connections.get_sqs_client()
dynamodb_client = aws_connections.get_dynamodb_client()

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

# Include the routers
app.include_router(query.router)
app.include_router(live.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
