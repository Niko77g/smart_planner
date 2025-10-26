from fastapi import FastAPI
from app.router.status import router as status_router
from app.router.events import router as events_router
from app.router.home import router as home_router

def create_app() -> FastAPI:
    app = FastAPI(title="Smart Study Planner")
    app.include_router(status_router)
    app.include_router(events_router)
    app.include_router(home_router)
    return app

app = create_app()
