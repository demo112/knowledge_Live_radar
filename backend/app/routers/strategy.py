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
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger crawl strategy optimization.
    """
    adapter = StrategyAdapter(db)
    
    # Run synchronously to return results
    changes = await adapter.optimize_strategies()
    
    return {
        "success": True, 
        "message": f"Strategy optimization completed. {len(changes)} sources adjusted.",
        "changes": changes
    }
