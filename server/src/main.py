# File: server/src/main.py  # Full file path comment as requested

from contextlib import asynccontextmanager  # Import async context manager utility for FastAPI lifespan handling
from typing import AsyncGenerator, Dict  # Import typing helpers for lifespan generator and response typing
from fastapi import FastAPI, status  # Import FastAPI app class and HTTP status codes
from src.api.routes.auth import router as auth_router  # Import authentication routes
from src.api.routes.profile import router as profile_router  # Import profile routes
from src.api.routes.assessment import router as assessment_router# Import Assessment routes
from src.db.mongodb import close_mongo_connection, connect_to_mongo  # Import async MongoDB lifecycle helpers


@asynccontextmanager  # Mark function as FastAPI lifespan context manager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:  # Define async startup/shutdown lifecycle function

    try:  # Start protected runtime block
        await connect_to_mongo()  # Connect to MongoDB at application startup
        print("MongoDB connected ✅")  # Log startup success for quick local visibility
        yield  # Hand control to FastAPI while app serves requests

    except Exception as e:
        print(e) # Prints for any kind of unwanted problems

    finally:  # Ensure cleanup always runs even if app crashes
        await close_mongo_connection()  # Close MongoDB client on shutdown
        print("MongoDB disconnected ✅")  # Log shutdown success for local observability


app = FastAPI(  # Create FastAPI application instance
    title="MindBridge API",  # Set API title shown in Swagger and ReDoc
    version="0.0.1",  # Set API semantic version for docs and clients
    description="MindBridge backend for authentication, profile management, and wellness workflow services.",  # Set high-level API description
    lifespan=lifespan,  # Register startup/shutdown lifecycle manager
)  # Finish FastAPI app initialization


app.include_router(auth_router)  # Mount authentication routes onto the application
app.include_router(profile_router)  # Mount profile routes onto the application
app.include_router(assessment_router) # Mount assessment routes onto the application


@app.get("/", status_code=status.HTTP_200_OK)  # Define root endpoint for quick service confirmation
async def root() -> Dict[str, str]:  # Return small JSON payload for root route
    return {"message": "MindBridge API is running"}  # Send simple readiness message
