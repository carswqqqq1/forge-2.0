from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import os

from app.core.config import get_settings
from app.infrastructure.storage.mongodb import get_mongodb
from app.infrastructure.storage.redis import get_redis
from app.interfaces.dependencies import get_agent_service
from app.interfaces.api.routes import router
from app.interfaces.api.openai_routes import router as openai_router
from app.infrastructure.logging import setup_logging
from app.interfaces.errors.exception_handlers import register_exception_handlers
from app.infrastructure.models.documents import (
    AgentDocument,
    SessionDocument,
    UserDocument,
    ClawDocument,
    UsageLedgerDocument,
    BillingActivityDocument,
    ScheduleDocument,
    ConnectorDocument,
    ReferralDocument,
)
from beanie import init_beanie

# Initialize logging system
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration
settings = get_settings()


# Create lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code executed on startup
    logger.info("Application startup - Forge backend initializing")
    
    # Initialize MongoDB and Beanie
    await get_mongodb().initialize()

    # Initialize Beanie
    await init_beanie(
        database=get_mongodb().client[settings.mongodb_database],
        document_models=[
            AgentDocument,
            SessionDocument,
            UserDocument,
            ClawDocument,
            UsageLedgerDocument,
            BillingActivityDocument,
            ScheduleDocument,
            ConnectorDocument,
            ReferralDocument,
        ]
    )
    logger.info("Successfully initialized Beanie")
    
    # Initialize Redis
    await get_redis().initialize()
    
    try:
        yield
    finally:
        # Code executed on shutdown
        logger.info("Application shutdown - Forge backend terminating")
        # Disconnect from MongoDB
        await get_mongodb().shutdown()
        # Disconnect from Redis
        await get_redis().shutdown()


        logger.info("Cleaning up AgentService instance")
        try:
            await asyncio.wait_for(get_agent_service().shutdown(), timeout=30.0)
            logger.info("AgentService shutdown completed successfully")
        except asyncio.TimeoutError:
            logger.warning("AgentService shutdown timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Error during AgentService cleanup: {str(e)}")

app = FastAPI(title="Forge", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=list({
        "http://localhost:5173",
        "http://localhost:3000",
        os.environ.get("FRONTEND_URL", "http://localhost:5173"),
    }),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_chat_request_size(request: Request, call_next):
    chat_path = request.url.path.startswith("/api/v1/sessions/") and request.url.path.endswith("/chat")
    if not chat_path:
        return await call_next(request)

    max_size = settings.max_request_body_size_bytes
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > max_size:
                return JSONResponse(
                    status_code=413,
                    content={"code": 413, "msg": "Request body too large", "data": None},
                )
        except ValueError:
            pass

    body = await request.body()
    if len(body) > max_size:
        return JSONResponse(
            status_code=413,
            content={"code": 413, "msg": "Request body too large", "data": None},
        )

    return await call_next(request)

# Register exception handlers
register_exception_handlers(app)

# Register routes
app.include_router(router, prefix="/api/v1")
# OpenAI-compatible proxy (used by OpenClaw containers for LLM requests)
app.include_router(openai_router)
