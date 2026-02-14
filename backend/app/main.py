from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.routers import (
    pyramids, nodes, sources, contents, discovery, approvals, 
    input, whitelist, dashboard, health,
    hotspots, drift, strategy, scheduler, config, evolution,
    contributions, synonyms, classification, notifications,
    content_management
)

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

from app.services.scheduler.scheduler_service import scheduler_service
from app.services.scheduler.crawl_manager import crawl_manager
from app.services.scheduler import tasks
from app.services.scheduler.task_registry import TaskRegistry
from app.services.prompt_loader import prompt_loader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register Task Handlers
    TaskRegistry.register("content_crawl", tasks.run_content_crawl)
    TaskRegistry.register("source_health", tasks.run_source_health_check)
    TaskRegistry.register("system_health", tasks.run_system_health_detection)
    TaskRegistry.register("hotspot_lifecycle", tasks.run_hotspot_lifecycle)
    TaskRegistry.register("drift_detection", tasks.run_drift_detection)
    TaskRegistry.register("strategy_optimization", tasks.run_strategy_optimization)
    TaskRegistry.register("cluster_discovery", tasks.run_cluster_discovery)
    TaskRegistry.register("content_metabolism", tasks.run_content_metabolism)

    # Startup
    await scheduler_service.start()
    await crawl_manager.start()
    
    # Load AI Prompts
    await prompt_loader.load_initial_prompts()
    
    # Register Scheduled Tasks (Create in DB if not exist)
    # 1. Content Crawl (Every 30 mins)
    await scheduler_service.register_task(
        "content_crawl", "content_crawl", "*/30 * * * *"
    )
    # 2. Source Health (Every hour)
    await scheduler_service.register_task(
        "source_health", "source_health", "0 * * * *"
    )
    # 3. System Health (Daily at 02:00)
    await scheduler_service.register_task(
        "system_health", "system_health", "0 2 * * *"
    )
    # 4. Hotspot Lifecycle (Daily at 03:00)
    await scheduler_service.register_task(
        "hotspot_lifecycle", "hotspot_lifecycle", "0 3 * * *"
    )
    # 5. Drift Detection (Weekly, Monday at 04:00)
    await scheduler_service.register_task(
        "drift_detection", "drift_detection", "0 4 * * 1"
    )
    # 6. Strategy Optimization (Daily at 01:00)
    await scheduler_service.register_task(
        "strategy_optimization", "strategy_optimization", "0 1 * * *"
    )
    # 7. Cluster Discovery (Daily at 05:00)
    await scheduler_service.register_task(
        "cluster_discovery", "cluster_discovery", "0 5 * * *"
    )
    # 8. Content Metabolism (Daily at 02:30)
    await scheduler_service.register_task(
        "content_metabolism", "content_metabolism", "30 2 * * *"
    )
    # 9. Evolution Cycle (Daily at 00:00)
    await scheduler_service.register_task(
        "evolution_cycle", "evolution_cycle", "0 0 * * *"
    )
    
    yield
    # Shutdown
    await scheduler_service.stop()
    await crawl_manager.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",  # Next.js default fallback port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://localhost(:\d+)?",  # Allow all localhost ports in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(pyramids.router, prefix=settings.API_V1_STR)
app.include_router(nodes.router, prefix=settings.API_V1_STR)
app.include_router(sources.router, prefix=settings.API_V1_STR)
app.include_router(contents.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(input.router, prefix=settings.API_V1_STR)
app.include_router(whitelist.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(hotspots.router, prefix=settings.API_V1_STR)
app.include_router(drift.router, prefix=settings.API_V1_STR)
app.include_router(strategy.router, prefix=settings.API_V1_STR)
app.include_router(scheduler.router, prefix=settings.API_V1_STR)
app.include_router(config.router, prefix=settings.API_V1_STR)
app.include_router(evolution.router, prefix=settings.API_V1_STR)
app.include_router(contributions.router, prefix=settings.API_V1_STR)
app.include_router(synonyms.router, prefix=settings.API_V1_STR)
app.include_router(classification.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(content_management.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Radar API"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
