from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from models.api_responses import ErrorResponse
from models.status_code import sc
from utils.config import settings
from contextlib import asynccontextmanager
from utils.logger import logger
from dummy_routes import dummy_router
from business_exception import BusinessException
from utils.data_sources_manager import data_sources_manager
from datetime import datetime, timezone

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    """
    Lifespan event handler for application startup and shutdown
    """
    # Startup
    try:
        logger.info("Starting Template Project..")
        await data_sources_manager.connect_all()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Shutting down Template Project...")
        await data_sources_manager.disconnect_all()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during application shutdown: {str(e)}")


app = FastAPI(
        title="Template Project",
        description="Python template project that shows some best practices",
        version="1.0.0",
        lifespan=lifespan_handler

)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#handle pydantic model errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Pydantic model validation failed in {request.method} {request.url.path}: {exc!r}")
    error_response = ErrorResponse(
        error="Input validation failed",
        status_code=sc.UNPROCESSABLE_ENTITY,
        details=jsonable_encoder(exc.errors())
    )
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.model_dump(exclude_none=True),
    )

#handle business logic violation exception 
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    logger.error(f"Business violation exception in {request.method} {request.url.path}", exc_info=True)
    error_response = ErrorResponse(
        error=str(exc),
        status_code=exc.error_code
    )
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.model_dump(exclude_none=True),
    )

#handle unexpected exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception in {request.method} {request.url.path}", exc_info=True)
    error_response = ErrorResponse(
        error=str(exc),
        status_code=sc.INTERNAL_SERVER_ERROR
    )
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.model_dump(exclude_none=True),
    )

app.include_router(dummy_router)

# Favicon endpoint to prevent 404 logs
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon available"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "template-app", "version" : "1.0.0"}


# Database health check endpoint
@app.get("/health/database")
async def database_health_check():
    """
    Check the health of database connections
    """
    try:
        logger.debug("Doing Health check on database connections...")

        health_status = await data_sources_manager.health_check()
        return {
            "service": "ai-health-coach-be",
            "version": "1.0.0",
            "database_status": health_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "service": "ai-health-coach-be",
            "version": "1.0.0",
            "database_status": {
                "mongodb": {"status": "error", "connected": False},
                "postgresql": {"status": "error", "connected": False},
                "overall_status": "error"
            },
            "error": str(e)
        }

if __name__ == "__main__":
    logger.debug(f"Starting Server in port:{settings.APP_PORT}, reload={settings.DEV_MODE}")
    uvicorn.run("app:app", host="0.0.0.0", port=settings.APP_PORT, reload=settings.DEV_MODE)
