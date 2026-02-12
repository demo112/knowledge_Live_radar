from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.evolution.strategy_adapter import StrategyAdapter

router = APIRouter(
    prefix="/strategy",
    tags=["strategy"]
)

@router.post("/optimize")
async def optimize_strategies(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger crawl strategy optimization.
    """
    adapter = StrategyAdapter(db)
    
    # Run in background
    background_tasks.add_task(adapter.optimize_strategies)
    
    return {"status": "accepted", "message": "Strategy optimization started in background"}
