from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import pyramids, nodes, sources, contents, discovery, approvals

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pyramids.router, prefix=settings.API_V1_STR)
app.include_router(nodes.router, prefix=settings.API_V1_STR)
app.include_router(sources.router, prefix=settings.API_V1_STR)
app.include_router(contents.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Radar API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
