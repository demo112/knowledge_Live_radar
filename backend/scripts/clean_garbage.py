import sys
import os
import asyncio
import logging
from sqlalchemy import text, func, select, delete

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import AsyncSessionLocal
from app.models import (
    ErrorRecord, APIMetric, TaskExecution, Notification, CrawlJob, HealthReport,
    HotspotEvent, StrategyAdjustment,
    Pyramid, PyramidNode, NodeRelation,
    InformationSource, SourceNodeRelation,
    ContentItem, ContentNodeRelation, ValidationResult, AISuggestion,
    Approval, Hotspot,
    Concept, ConceptSynonym, Snapshot, Contribution, SynonymMapping,
    BatchTask, DomainWhitelist, DiscoveredDomain
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def get_counts(session):
    counts = {}
    models = [
        ("Error Records", ErrorRecord),
        ("API Metrics", APIMetric),
        ("Task Executions", TaskExecution),
        ("Notifications", Notification),
        ("Crawl Jobs", CrawlJob),
        ("Health Reports", HealthReport),
        ("Hotspot Events", HotspotEvent),
        ("Strategy Adjustments", StrategyAdjustment),
        
        ("Pyramids", Pyramid),
        ("Pyramid Nodes", PyramidNode),
        ("Node Relations", NodeRelation),
        
        ("Information Sources", InformationSource),
        ("Source Relations", SourceNodeRelation),
        
        ("Content Items", ContentItem),
        ("Content Relations", ContentNodeRelation),
        ("Validation Results", ValidationResult),
        ("AI Suggestions", AISuggestion),
        
        ("Approvals", Approval),
        ("Hotspots", Hotspot),
        
        ("Concepts", Concept),
        ("Snapshots", Snapshot),
        ("Contributions", Contribution),
        ("Batch Tasks", BatchTask),
        ("Discovered Domains", DiscoveredDomain),
        ("Domain Whitelists", DomainWhitelist),
    ]
    
    for name, model in models:
        try:
            result = await session.execute(select(func.count()).select_from(model))
            counts[name] = result.scalar()
        except Exception as e:
            # Table might not exist or other error
            pass
            
    return counts

async def clean_logs(session):
    logger.info("Cleaning System Logs and Operational Data...")
    
    # List of models to clean
    log_models = [
        ErrorRecord, 
        APIMetric, 
        TaskExecution, 
        Notification, 
        HealthReport,
        HotspotEvent,
        StrategyAdjustment
    ]
    
    total_deleted = 0
    for model in log_models:
        stmt = delete(model)
        result = await session.execute(stmt)
        count = result.rowcount
        logger.info(f"Deleted {count} rows from {model.__tablename__}")
        total_deleted += count
        
    # Clean old CrawlJobs (keep last 50 maybe? For now delete all as requested)
    stmt = delete(CrawlJob)
    result = await session.execute(stmt)
    logger.info(f"Deleted {result.rowcount} rows from crawl_jobs")
    total_deleted += result.rowcount

    await session.commit()
    logger.info(f"Total log/operational records deleted: {total_deleted}")

async def clean_business_data(session):
    logger.info("Cleaning Business Data (Pyramids, Sources, Contents, etc.)...")
    
    # Delete order: Child -> Parent to avoid FK constraints issues
    # Some relations might be set to CASCADE, but explicit deletion is safer.
    
    models_to_clean = [
        # 1. Leaf / Relation Tables
        NodeRelation,
        SourceNodeRelation,
        ContentNodeRelation,
        ValidationResult,
        AISuggestion,
        ConceptSynonym,
        SynonymMapping,
        
        # 2. Secondary Entities
        PyramidNode,
        Approval,
        Hotspot,
        Snapshot,
        Contribution,
        BatchTask,
        DiscoveredDomain,
        DomainWhitelist,
        
        # 3. Core Entities
        ContentItem,
        InformationSource,
        Pyramid,
        Concept
    ]
    
    total_deleted = 0
    for model in models_to_clean:
        try:
            stmt = delete(model)
            result = await session.execute(stmt)
            count = result.rowcount
            if count > 0:
                logger.info(f"Deleted {count} rows from {model.__tablename__}")
                total_deleted += count
        except Exception as e:
            # Log but continue, maybe table doesn't exist or other issue
            logger.warning(f"Skipped {model.__tablename__}: {e}")
            
    await session.commit()
    logger.info(f"Total business data records deleted: {total_deleted}")

async def main():
    async with AsyncSessionLocal() as session:
        print("--- Current Data Counts ---")
        counts = await get_counts(session)
        for name, count in counts.items():
            print(f"{name}: {count}")
        print("---------------------------")
        
        # Check args
        mode = "logs" # Default
        if len(sys.argv) > 1:
            if sys.argv[1] == "all":
                mode = "all"
            elif sys.argv[1] == "check":
                mode = "check"
        
        if mode == "check":
            return

        if mode == "all":
            print("\nWARNING: You are about to delete ALL data including Business Data.")
            # confirm = input("Type 'yes' to confirm: ") # Cannot use input in non-interactive
            # Assuming user intent from chat context implies doing it if explicitly asked.
            # But I'll stick to logs first unless specified.
            await clean_logs(session)
            await clean_business_data(session)
        else:
            print("\nCleaning system garbage (logs, metrics, history)...")
            await clean_logs(session)
            print("\nDone. Business data was preserved. To clean everything run with 'all'.")

        print("\n--- Final Data Counts ---")
        counts = await get_counts(session)
        for name, count in counts.items():
            print(f"{name}: {count}")
            
if __name__ == "__main__":
    asyncio.run(main())
