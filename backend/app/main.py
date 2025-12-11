from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.endpoints import jobs  # Import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API untuk analisis lowongan pekerjaan menggunakan NLP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    jobs.router, 
    prefix=f"{settings.API_V1_PREFIX}/jobs",
    tags=["Jobs"]
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Job Market Intelligence Platform API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

# ... rest of your endpoints