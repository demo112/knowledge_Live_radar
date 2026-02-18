import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple, Optional

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_report import HealthReport, HealthReportType
from app.models.pyramid import Pyramid, PyramidNode
from app.models.source import InformationSource
from app.models.content import ContentItem
from app.models.approval import Approval
from app.models.hotspot import Hotspot
from app.models.crawl_job import CrawlJob
from app.core.ai.client import ai_client
from app.core.ai.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)


class HealthDetector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _generate_issue_description(
        self,
        issue_type: str,
        severity: str,
        context: Dict[str, Any],
        entity_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用 AI 生成问题描述和建议

        Args:
            issue_type: 问题类型
            severity: 严重程度
            context: 上下文信息
            entity_info: 实体信息

        Returns:
            包含 description, suggestions, impact 的字典
        """
        try:
            prompt_content, metadata = prompt_loader.render_prompt(
                "health_issue_analysis",
                {
                    "issue_type": issue_type,
                    "severity": severity,
                    "context": json.dumps(context, ensure_ascii=False),
                    "entity_info": json.dumps(entity_info, ensure_ascii=False),
                }
            )

            if not prompt_content:
                logger.warning(f"无法加载健康问题分析 Prompt，使用默认描述")
                return self._get_fallback_description(issue_type, entity_info)

            model = metadata.get("model") if metadata else None
            messages = [{"role": "user", "content": prompt_content}]

            logger.info(f"调用 AI 生成问题描述: {issue_type}")
            response_text = await ai_client.chat_completion(messages, model=model)

            if not response_text:
                logger.warning("AI 返回空响应，使用默认描述")
                return self._get_fallback_description(issue_type, entity_info)

            result = ai_client.parse_json(response_text)

            if not result:
                logger.warning(f"无法解析 AI 响应，使用默认描述: {response_text[:200]}")
                return self._get_fallback_description(issue_type, entity_info)

            return {
                "description": result.get("description", ""),
                "suggestions": result.get("suggestions", []),
                "impact": result.get("impact", ""),
            }

        except Exception as e:
            logger.error(f"生成问题描述失败: {e}")
            return self._get_fallback_description(issue_type, entity_info)

    def _get_fallback_description(
        self,
        issue_type: str,
        entity_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI 调用失败时的降级描述

        Args:
            issue_type: 问题类型
            entity_info: 实体信息

        Returns:
            基础描述字典
        """
        fallback_descriptions = {
            "empty_pyramid": {
                "description": f"金字塔 '{entity_info.get('name', '未知')}' 没有任何节点",
                "suggestions": [{"action": "add_nodes", "detail": "建议添加知识节点构建金字塔结构", "priority": "high"}],
                "impact": "空金字塔无法发挥知识组织作用",
            },
            "sparse_pyramid": {
                "description": f"金字塔 '{entity_info.get('name', '未知')}' 节点数量过少 ({entity_info.get('node_count', 0)})",
                "suggestions": [{"action": "expand_structure", "detail": "建议扩展金字塔结构，增加更多知识节点", "priority": "medium"}],
                "impact": "结构稀疏可能导致知识覆盖不全面",
            },
            "source_failing": {
                "description": f"信息源 '{entity_info.get('name', '未知')}' 连续失败 ({entity_info.get('error_count', 0)} 次)",
                "suggestions": [{"action": "check_source", "detail": "建议检查信息源可用性和配置", "priority": "high"}],
                "impact": "信息源不可用将导致内容获取中断",
            },
            "no_new_content": {
                "description": "过去 24 小时未获取新内容",
                "suggestions": [{"action": "check_crawl", "detail": "建议检查抓取任务是否正常运行", "priority": "medium"}],
                "impact": "内容更新停滞可能导致知识库过时",
            },
            "high_backlog": {
                "description": f"审批积压严重：{entity_info.get('pending_count', 0)} 个待处理提案",
                "suggestions": [{"action": "process_approvals", "detail": "建议尽快处理积压的审批提案", "priority": "high"}],
                "impact": "审批积压会阻塞系统进化流程",
            },
            "moderate_backlog": {
                "description": f"审批积压中等：{entity_info.get('pending_count', 0)} 个待处理提案",
                "suggestions": [{"action": "process_approvals", "detail": "建议定期处理审批提案", "priority": "medium"}],
                "impact": "审批积压可能影响系统响应速度",
            },
        }

        return fallback_descriptions.get(
            issue_type,
            {"description": f"检测到问题: {issue_type}", "suggestions": [], "impact": "未知影响"}
        )

    async def run_full_detection(self, report_type: HealthReportType = HealthReportType.SCHEDULED) -> HealthReport:
        logger.info(f"Starting full system health detection (type={report_type})")

        try:
            pyramid_scores, pyramid_issues = await self.evaluate_pyramid_structure()
            source_score, source_issues = await self.evaluate_source_health()
            coverage_score, coverage_issues = await self.evaluate_content_coverage()
            hotspot_stats, hotspot_issues = await self.evaluate_hotspot_distribution()
            backlog_stats, backlog_issues = await self.evaluate_approval_backlog()
            crawl_stats = await self.collect_crawl_stats()

            avg_pyramid_score = sum(pyramid_scores.values()) / len(pyramid_scores) if pyramid_scores else 100.0

            overall_score = (
                avg_pyramid_score * 0.3 +
                source_score * 0.3 +
                coverage_score * 0.2 +
                (100 - min(backlog_stats.get("backlog_penalty", 0), 100)) * 0.2
            )

            all_issues = pyramid_issues + source_issues + coverage_issues + hotspot_issues + backlog_issues

            report = HealthReport(
                report_type=report_type,
                overall_score=round(overall_score, 1),
                pyramid_scores=pyramid_scores,
                source_health_score=round(source_score, 1),
                content_coverage_score=round(coverage_score, 1),
                hotspot_distribution=hotspot_stats,
                approval_backlog=backlog_stats,
                crawl_stats=crawl_stats,
                issues=all_issues
            )

            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)

            logger.info(f"Health detection completed. Overall Score: {report.overall_score}")
            return report

        except Exception as e:
            logger.error(f"Error during health detection: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise

    async def evaluate_pyramid_structure(self) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
        scores = {}
        issues = []

        result = await self.db.execute(select(Pyramid).where(Pyramid.is_deleted == False))
        pyramids = result.scalars().all()

        for pyramid in pyramids:
            score = 100.0
            count_result = await self.db.execute(
                select(func.count(PyramidNode.id))
                .where(PyramidNode.pyramid_id == pyramid.id)
                .where(PyramidNode.is_deleted == False)
            )
            node_count = count_result.scalar() or 0

            if node_count == 0:
                score -= 50
                ai_result = await self._generate_issue_description(
                    issue_type="empty_pyramid",
                    severity="high",
                    context={"node_count": 0},
                    entity_info={"name": pyramid.name, "pyramid_id": str(pyramid.id)}
                )
                issues.append({
                    "type": "empty_pyramid",
                    "category": "pyramid",
                    "severity": "high",
                    "description": ai_result["description"],
                    "suggestions": ai_result.get("suggestions", []),
                    "impact": ai_result.get("impact", ""),
                    "entity_id": str(pyramid.id)
                })
            elif node_count < 3:
                score -= 20
                ai_result = await self._generate_issue_description(
                    issue_type="sparse_pyramid",
                    severity="medium",
                    context={"node_count": node_count},
                    entity_info={"name": pyramid.name, "pyramid_id": str(pyramid.id), "node_count": node_count}
                )
                issues.append({
                    "type": "sparse_pyramid",
                    "category": "pyramid",
                    "severity": "medium",
                    "description": ai_result["description"],
                    "suggestions": ai_result.get("suggestions", []),
                    "impact": ai_result.get("impact", ""),
                    "entity_id": str(pyramid.id)
                })

            scores[str(pyramid.id)] = max(0.0, score)

        return scores, issues

    async def evaluate_source_health(self) -> Tuple[float, List[Dict[str, Any]]]:
        result = await self.db.execute(
            select(InformationSource).where(InformationSource.is_deleted == False)
        )
        sources = result.scalars().all()
        if not sources:
            return 100.0, []

        total_score = 0.0
        issues = []

        for source in sources:
            source_score = 100.0

            if source.error_count > 0:
                penalty = min(source.error_count * 10, 80)
                source_score -= penalty
                severity = "high" if source.error_count > 3 else "medium"
                ai_result = await self._generate_issue_description(
                    issue_type="source_failing",
                    severity=severity,
                    context={"error_count": source.error_count, "last_error": source.last_error_message},
                    entity_info={"name": source.name, "source_id": str(source.id), "error_count": source.error_count}
                )
                issues.append({
                    "type": "source_failing",
                    "category": "source",
                    "severity": severity,
                    "description": ai_result["description"],
                    "suggestions": ai_result.get("suggestions", []),
                    "impact": ai_result.get("impact", ""),
                    "entity_id": str(source.id)
                })

            total_score += max(0.0, source_score)

        return total_score / len(sources), issues

    async def evaluate_content_coverage(self) -> Tuple[float, List[Dict[str, Any]]]:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        count_result = await self.db.execute(
            select(func.count(ContentItem.id)).where(ContentItem.created_at >= yesterday)
        )
        new_content_count = count_result.scalar() or 0

        issues = []
        score = 100.0

        if new_content_count == 0:
            score = 50.0
            ai_result = await self._generate_issue_description(
                issue_type="no_new_content",
                severity="medium",
                context={"hours": 24, "new_content_count": 0},
                entity_info={"time_range": "24小时"}
            )
            issues.append({
                "type": "no_new_content",
                "category": "content",
                "severity": "medium",
                "description": ai_result["description"],
                "suggestions": ai_result.get("suggestions", []),
                "impact": ai_result.get("impact", ""),
                "entity_id": None
            })
        elif new_content_count < 10:
            score = 80.0

        return score, issues

    async def evaluate_hotspot_distribution(self) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:
        stats = {}
        issues = []

        try:
            result = await self.db.execute(
                select(Hotspot.status, func.count(Hotspot.id)).group_by(Hotspot.status)
            )
            results = result.all()

            for status, count in results:
                status_key = status.value if hasattr(status, 'value') else str(status)
                stats[status_key] = count

        except Exception as e:
            logger.warning(f"Could not evaluate hotspot distribution: {e}")
            stats = {"error": 1}

        return stats, issues

    async def evaluate_approval_backlog(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        count_result = await self.db.execute(
            select(func.count(Approval.id)).where(Approval.status == "pending")
        )
        pending_count = count_result.scalar() or 0

        stats = {"pending_count": pending_count}
        issues = []
        penalty = 0

        if pending_count > 50:
            penalty = 50
            ai_result = await self._generate_issue_description(
                issue_type="high_backlog",
                severity="high",
                context={"pending_count": pending_count, "threshold": 50},
                entity_info={"pending_count": pending_count}
            )
            issues.append({
                "type": "high_backlog",
                "category": "approval",
                "severity": "high",
                "description": ai_result["description"],
                "suggestions": ai_result.get("suggestions", []),
                "impact": ai_result.get("impact", ""),
                "entity_id": None
            })
        elif pending_count > 20:
            penalty = 20
            ai_result = await self._generate_issue_description(
                issue_type="moderate_backlog",
                severity="medium",
                context={"pending_count": pending_count, "threshold": 20},
                entity_info={"pending_count": pending_count}
            )
            issues.append({
                "type": "moderate_backlog",
                "category": "approval",
                "severity": "medium",
                "description": ai_result["description"],
                "suggestions": ai_result.get("suggestions", []),
                "impact": ai_result.get("impact", ""),
                "entity_id": None
            })

        stats["backlog_penalty"] = penalty
        return stats, issues

    async def collect_crawl_stats(self) -> Dict[str, Any]:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        try:
            result = await self.db.execute(
                select(CrawlJob).where(CrawlJob.started_at >= yesterday)
            )
            jobs = result.scalars().all()

            total_jobs = len(jobs)
            total_items = sum((j.items_new or 0) for j in jobs)
            failed_jobs = sum(1 for j in jobs if str(j.status).lower() == "failed")

            return {
                "jobs_last_24h": total_jobs,
                "items_new_last_24h": total_items,
                "failed_jobs_last_24h": failed_jobs
            }
        except Exception as e:
            logger.warning(f"Could not collect crawl stats: {e}")
            return {}
