from fastapi import FastAPI,Depends
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.core.permissions import require_admin
from app.models.user import User
from app.api.stations import router as stations_router
from app.api.trains import router as trains_router
from app.api.train_routes import router as train_routes_router
from app.api.search import router as search_router
from app.api.coaches import router as coaches_router
from app.api.seats import router as seats_router
from app.api.bookings import router as bookings_router
from app.api.inventory import router as inventory_router
from app.api.fares import router as fares_router
from app.api.payments import router as payments_router
from app.api.refunds import router as refunds_router
from app.api import trains


app=FastAPI(
    title="RailConnect API",
    description="Railway Booking Backend",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(stations_router)
app.include_router(trains_router)
app.include_router(train_routes_router)
app.include_router(search_router)
app.include_router(coaches_router)
app.include_router(seats_router)
app.include_router(bookings_router)
app.include_router(inventory_router)
app.include_router(fares_router)
app.include_router(payments_router)
app.include_router(refunds_router)
app.include_router(trains.router)

@app.get("/")
def home():
    return {
        "message":"welcome",
        "status":"running",
    }


@app.get("/health")
def health_check():
    return {
        "status":"healthy"
    }


@app.get("/admin/test")
def admin_test(
    current_user:User=Depends(require_admin)
):
    return{
        "message":"Admin access granted",
        "user": current_user.email,
    }
