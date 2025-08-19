from fastapi import FastAPI
from src.api import global_router
from src.core.conf import settings
from src.core.exceptions import set_errror
from src.services.lots import scheduler
from contextlib import asynccontextmanager
from .log import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting scheduler")
    scheduler.start()
    yield
    logger.info("Shutdown scheduler")
    scheduler.shutdown()


def create_app():
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.TITLE,
        version=settings.VERSION,
        lifespan=lifespan,
    )
    # Include all Routers
    app.include_router(global_router)

    # Set error handler
    set_errror(app)

    return app
