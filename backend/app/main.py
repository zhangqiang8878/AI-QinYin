from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.api import auth, users, voices

app = FastAPI(title="AI亲音 Backend API")

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(voices.router, prefix="/api/voices", tags=["voices"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()