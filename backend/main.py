import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.api.routes import router
from backend.services.run_manager import RunManager
from backend.api.intelligence import router as intelligence_router
from backend.services.survey import survey_data

logging.basicConfig(level=logging.INFO,format='%(levelname)s %(message)s')


@asynccontextmanager
async def lifespan(app):
    app.state.manager=RunManager()
    app.state.manager.initialize()
    survey_data()
    yield


app=FastAPI(title='BhoomiSync',version='0.1.0',lifespan=lifespan)
app.include_router(router)
app.include_router(intelligence_router)
