from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from app.api.v1.admin_routes import router as admin_router
from app.api.v1.org_routes import router as org_router
from app.db.client import init_db, close_db

# Load environment variables from .env file
load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")

app = FastAPI(
    title="Organization Management API",
    description="API for managing organizations and admin authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin_router)
app.include_router(org_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_db()


@app.get("/")
async def root():
    return {"message": "Multi-Tenant Organization Management API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
