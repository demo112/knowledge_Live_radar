import logging
import time
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.error_record import ErrorRecord
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

@dataclass
class RetryPolicy:
    max_retries: int
    base_delay_seconds: float
    backoff_factor: float

class ErrorHandler:
    # Retry policies
    RETRY_POLICIES = {
        "network": RetryPolicy(max_retries=3, base_delay_seconds=1.0, backoff_factor=1.5),
        "ai_service": RetryPolicy(max_retries=3, base_delay_seconds=5.0, backoff_factor=2.0),
        "database": RetryPolicy(max_retries=0, base_delay_seconds=0.0, backoff_factor=0.0),
        "default": RetryPolicy(max_retries=1, base_delay_seconds=1.0, backoff_factor=1.0),
    }
    
    # Circuit Breaker
    CIRCUIT_BREAKER_THRESHOLD = 10
    CIRCUIT_BREAKER_WINDOW = 300 # 5 minutes
    
    def __init__(self):
        self._error_counts: Dict[str, list] = {} # type: error_type -> list of timestamps
    
    async def handle_error(self, error: Exception, context: Dict[str, Any], error_type: str = "unknown") -> None:
        """Handle error: log, record to DB, trigger circuit breaker check"""
        logger.error(f"Handling error {error_type}: {error}", exc_info=True)
        
        # Record to DB
        try:
            async with AsyncSessionLocal() as session:
                error_record = ErrorRecord(
                    error_type=error_type,
                    error_message=str(error),
                    stack_trace=str(error.__traceback__) if error.__traceback__ else None,
                    context=context,
                    source_service=context.get("source", "unknown"),
                    source_task_id=context.get("task_id"),
                    retry_count=context.get("retry_count", 0),
                    max_retries=self.RETRY_POLICIES.get(error_type, self.RETRY_POLICIES["default"]).max_retries
                )
                session.add(error_record)
                await session.commit()
        except Exception as db_err:
            logger.error(f"Failed to record error to DB: {db_err}")
            
        # Circuit Breaker Logic (InMemory for now)
        now = time.time()
        if error_type not in self._error_counts:
            self._error_counts[error_type] = []
        self._error_counts[error_type].append(now)
        
        # Clean up old errors
        self._error_counts[error_type] = [t for t in self._error_counts[error_type] if now - t < self.CIRCUIT_BREAKER_WINDOW]
        
        if len(self._error_counts[error_type]) > self.CIRCUIT_BREAKER_THRESHOLD:
            logger.critical(f"Circuit breaker triggered for {error_type}!")
            # In a real system, we would set a flag to stop processing this type of task
            
    async def should_retry(self, error_type: str, current_retry: int) -> Tuple[bool, float]:
        policy = self.RETRY_POLICIES.get(error_type, self.RETRY_POLICIES["default"])
        if current_retry < policy.max_retries:
            delay = policy.base_delay_seconds * (policy.backoff_factor ** current_retry)
            return True, delay
        return False, 0.0

error_handler = ErrorHandler()
