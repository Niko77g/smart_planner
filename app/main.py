from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.router.status import router as status_router
from app.router.events import router as events_router
from app.router.home import router as home_router
from app.router.auth import router as auth_router

def create_app() -> FastAPI:
    my_app = FastAPI(title="Smart Study Planner")
    my_app.mount("/static", StaticFiles(directory="app/static"), name="static")
    my_app.include_router(status_router)
    my_app.include_router(events_router)
    my_app.include_router(home_router)
    my_app.include_router(auth_router)
    return my_app

app = create_app()
