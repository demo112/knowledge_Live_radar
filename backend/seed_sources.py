"""
初始化信源种子数据
为 AI Radar 平台提供覆盖 AI 应用领域的初始信息源和域名白名单。

覆盖领域：
- AI 开发工具链
- Agent 生态
- Prompt 工程
- 模型应用能力
- 热点追踪（行业动态）

使用方式：
  cd backend
  python seed_sources.py
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.source import InformationSource
from app.models.domain_whitelist import DomainWhitelist
from sqlalchemy import select


# ── 域名白名单 ──────────────────────────────────────────────
WHITELIST_DOMAINS = [
    # 学术 / 论文
    {"domain": "arxiv.org", "credibility": 95, "reason": "顶级预印本平台，AI 领域核心论文来源"},
    {"domain": "*.arxiv.org", "credibility": 95, "reason": "arXiv 子域名"},
    {"domain": "paperswithcode.com", "credibility": 90, "reason": "论文+代码对照平台，学术可信度高"},
    {"domain": "semanticscholar.org", "credibility": 90, "reason": "AI2 语义学术搜索引擎"},
    {"domain": "huggingface.co", "credibility": 90, "reason": "开源模型社区，模型/数据集权威来源"},
    # 官方博客
    {"domain": "openai.com", "credibility": 95, "reason": "OpenAI 官方，GPT 系列一手信息"},
    {"domain": "blog.openai.com", "credibility": 95, "reason": "OpenAI 官方博客"},
    {"domain": "anthropic.com", "credibility": 95, "reason": "Anthropic 官方，Claude 系列一手信息"},
    {"domain": "blog.google", "credibility": 90, "reason": "Google 官方博客"},
    {"domain": "ai.google", "credibility": 95, "reason": "Google AI 官方"},
    {"domain": "ai.meta.com", "credibility": 95, "reason": "Meta AI 官方，LLaMA 系列一手信息"},
    {"domain": "deepmind.google", "credibility": 95, "reason": "DeepMind 官方"},
    {"domain": "mistral.ai", "credibility": 90, "reason": "Mistral AI 官方"},
    {"domain": "docs.cohere.com", "credibility": 85, "reason": "Cohere 官方文档"},
    # 开发者平台
    {"domain": "github.com", "credibility": 85, "reason": "全球最大代码托管平台"},
    {"domain": "github.blog", "credibility": 85, "reason": "GitHub 官方博客"},
    {"domain": "docs.langchain.com", "credibility": 85, "reason": "LangChain 官方文档"},
    {"domain": "docs.llamaindex.ai", "credibility": 85, "reason": "LlamaIndex 官方文档"},
    {"domain": "docs.crewai.com", "credibility": 80, "reason": "CrewAI 官方文档"},
    {"domain": "docs.autogen.ai", "credibility": 80, "reason": "AutoGen 官方文档"},
    # 技术媒体
    {"domain": "techcrunch.com", "credibility": 75, "reason": "知名科技媒体"},
    {"domain": "theverge.com", "credibility": 75, "reason": "知名科技媒体"},
    {"domain": "venturebeat.com", "credibility": 75, "reason": "AI 领域报道较多的科技媒体"},
    {"domain": "*.medium.com", "credibility": 60, "reason": "Medium 博客平台，质量参差不齐"},
    {"domain": "towardsdatascience.com", "credibility": 70, "reason": "数据科学/AI 技术博客"},
    # 中文来源
    {"domain": "mp.weixin.qq.com", "credibility": 55, "reason": "微信公众号，需按账号评估质量"},
    {"domain": "36kr.com", "credibility": 65, "reason": "36氪，国内科技媒体"},
    {"domain": "jiqizhixin.com", "credibility": 75, "reason": "机器之心，AI 领域专业中文媒体"},
    {"domain": "qbitai.com", "credibility": 70, "reason": "量子位，AI 领域中文媒体"},
    {"domain": "infoq.cn", "credibility": 80, "reason": "InfoQ 中国，高质量技术社区"},
    {"domain": "zhidx.com", "credibility": 70, "reason": "智东西，智能产业媒体"},
    {"domain": "geekpark.net", "credibility": 70, "reason": "极客公园，科技创新者社区"},
    {"domain": "research.baidu.com", "credibility": 85, "reason": "百度研究院"},
    {"domain": "modelscope.cn", "credibility": 90, "reason": "魔搭社区，阿里达摩院推出的模型社区"},
    {"domain": "csdn.net", "credibility": 60, "reason": "CSDN，老牌技术社区"},
]

# ── 信息源 ──────────────────────────────────────────────────
SOURCES = [
    # ━━ RSS 类 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 学术论文
    {
        "name": "arXiv - AI (cs.AI)",
        "type": "RSS",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "check_interval": 3600,
        "config": {"category": "学术论文", "domain": "AI 通用"},
    },
    {
        "name": "arXiv - 计算语言学 (cs.CL)",
        "type": "RSS",
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "check_interval": 3600,
        "config": {"category": "学术论文", "domain": "NLP / 大语言模型"},
    },
    {
        "name": "arXiv - 机器学习 (cs.LG)",
        "type": "RSS",
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "check_interval": 3600,
        "config": {"category": "学术论文", "domain": "机器学习"},
    },
    {
        "name": "arXiv - 多智能体 (cs.MA)",
        "type": "RSS",
        "url": "https://rss.arxiv.org/rss/cs.MA",
        "check_interval": 7200,
        "config": {"category": "学术论文", "domain": "多智能体系统"},
    },
    {
        "name": "arXiv - 软件工程 (cs.SE)",
        "type": "RSS",
        "url": "https://rss.arxiv.org/rss/cs.SE",
        "check_interval": 7200,
        "config": {"category": "学术论文", "domain": "AI 辅助软件工程"},
    },
    {
        "name": "Papers With Code - 最新论文",
        "type": "RSS",
        "url": "https://paperswithcode.com/latest",
        "check_interval": 7200,
        "config": {"category": "学术论文", "domain": "论文+代码"},
    },
    {
        "name": "Semantic Scholar - AI Feed",
        "type": "RSS",
        "url": "https://api.semanticscholar.org/graph/v1/paper/search/rss?query=large+language+model&fieldsOfStudy=Computer+Science",
        "check_interval": 14400,
        "config": {"category": "学术论文", "domain": "LLM 研究"},
    },
    # 官方博客
    {
        "name": "OpenAI Blog",
        "type": "RSS",
        "url": "https://openai.com/blog/rss.xml",
        "check_interval": 3600,
        "config": {"category": "官方博客", "domain": "OpenAI / GPT"},
    },
    {
        "name": "Google AI Blog",
        "type": "RSS",
        "url": "https://blog.google/technology/ai/rss/",
        "check_interval": 7200,
        "config": {"category": "官方博客", "domain": "Google AI / Gemini"},
    },
    {
        "name": "Anthropic Research",
        "type": "RSS",
        "url": "https://www.anthropic.com/research/rss.xml",
        "check_interval": 7200,
        "config": {"category": "官方博客", "domain": "Anthropic / Claude"},
    },
    {
        "name": "Meta AI Blog",
        "type": "RSS",
        "url": "https://ai.meta.com/blog/rss/",
        "check_interval": 7200,
        "config": {"category": "官方博客", "domain": "Meta AI / LLaMA"},
    },
    {
        "name": "Hugging Face Blog",
        "type": "RSS",
        "url": "https://huggingface.co/blog/feed.xml",
        "check_interval": 7200,
        "config": {"category": "官方博客", "domain": "开源模型生态"},
    },
    {
        "name": "GitHub Blog - AI/ML",
        "type": "RSS",
        "url": "https://github.blog/feed/",
        "check_interval": 14400,
        "config": {"category": "开发者平台", "domain": "AI 开发工具"},
    },
    {
        "name": "LangChain Blog",
        "type": "RSS",
        "url": "https://blog.langchain.dev/rss/",
        "check_interval": 14400,
        "config": {"category": "开发者平台", "domain": "Agent 框架 / LangChain"},
    },
    # 技术媒体
    {
        "name": "VentureBeat - AI",
        "type": "RSS",
        "url": "https://venturebeat.com/category/ai/feed/",
        "check_interval": 3600,
        "config": {"category": "技术媒体", "domain": "AI 行业动态"},
    },
    {
        "name": "TechCrunch - AI",
        "type": "RSS",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "check_interval": 3600,
        "config": {"category": "技术媒体", "domain": "AI 行业动态"},
    },
    {
        "name": "The Verge - AI",
        "type": "RSS",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "check_interval": 7200,
        "config": {"category": "技术媒体", "domain": "AI 行业动态"},
    },
    # 中文媒体
    {
        "name": "机器之心",
        "type": "RSS",
        "url": "https://www.jiqizhixin.com/rss",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "AI 综合"},
    },
    {
        "name": "量子位",
        "type": "RSS",
        "url": "https://www.qbitai.com/feed",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "AI 综合"},
    },
    {
        "name": "36氪 - AI",
        "type": "RSS",
        "url": "https://36kr.com/feed",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "科技创投"},
    },
    {
        "name": "InfoQ 中国 - AI",
        "type": "RSS",
        "url": "https://www.infoq.cn/feed",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "技术架构/AI"},
    },
    {
        "name": "智东西",
        "type": "RSS",
        "url": "https://zhidx.com/feed",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "智能产业"},
    },
    {
        "name": "极客公园",
        "type": "RSS",
        "url": "https://www.geekpark.net/rss",
        "check_interval": 3600,
        "config": {"category": "中文媒体", "domain": "产品创新"},
    },
    {
        "name": "百度研究院",
        "type": "RSS",
        "url": "http://research.baidu.com/Blog/rss",
        "check_interval": 14400,
        "config": {"category": "官方博客", "domain": "百度 AI"},
    },

    # ━━ 推荐扩展：高质量中文技术博客 (原生 RSS) ━━━━━━━━━━━━━━━━━━
    {
        "name": "科学空间 (苏剑林)",
        "type": "RSS",
        "url": "https://kexue.fm/feed",
        "check_interval": 86400,
        "config": {"category": "技术博客", "domain": "NLP/数学"},
    },
    {
        "name": "阮一峰的网络日志",
        "type": "RSS",
        "url": "http://www.ruanyifeng.com/blog/atom.xml",
        "check_interval": 86400,
        "config": {"category": "技术博客", "domain": "技术趋势"},
    },
    {
        "name": "酷壳 (CoolShell)",
        "type": "RSS",
        "url": "https://coolshell.cn/feed",
        "check_interval": 86400,
        "config": {"category": "技术博客", "domain": "架构/基础"},
    },
    {
        "name": "AIWalker",
        "type": "RSS",
        "url": "https://aiwalker.cn/atom.xml",
        "check_interval": 86400,
        "config": {"category": "技术博客", "domain": "计算机视觉"},
    },
    {
        "name": "美团技术团队",
        "type": "RSS",
        "url": "https://tech.meituan.com/feed/",
        "check_interval": 86400,
        "config": {"category": "技术博客", "domain": "大厂技术"},
    },

    # ━━ 桥接源：需 RSSHub / WeWe RSS ━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "name": "知乎日报",
        "type": "RSS",
        "url": "https://rsshub.app/zhihu/daily",
        "check_interval": 3600,
        "config": {"category": "聚合媒体", "domain": "综合/知乎"},
    },
    # 示例：微信公众号 (需本地 WeWe RSS，请替换 localhost:4000 为实际地址)
    # {
    #     "name": "机器之心 (公众号)",
    #     "type": "RSS",
    #     "url": "http://localhost:4000/feed/wechat/jiqizhixin", 
    #     "check_interval": 3600,
    #     "config": {"category": "微信公众号", "domain": "AI 媒体"},
    # },

    # ━━ WEB 类 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "name": "Hugging Face - 热门模型",
        "type": "WEB",
        "url": "https://huggingface.co/models?sort=trending",
        "check_interval": 14400,
        "config": {
            "category": "模型生态",
            "domain": "开源模型趋势",
            "selector": ".model-card",
        },
    },
    {
        "name": "GitHub Trending - AI/ML",
        "type": "WEB",
        "url": "https://github.com/trending?since=daily&spoken_language_code=&topic=artificial-intelligence",
        "check_interval": 86400,
        "config": {
            "category": "开发工具",
            "domain": "AI 开源项目趋势",
            "selector": "article.Box-row",
        },
    },
    {
        "name": "Awesome LLM Apps (GitHub)",
        "type": "WEB",
        "url": "https://github.com/Shubhamsaboo/awesome-llm-apps",
        "check_interval": 86400,
        "config": {
            "category": "开发工具",
            "domain": "LLM 应用合集",
        },
    },
    {
        "name": "ModelScope - 热门模型",
        "type": "WEB",
        "url": "https://modelscope.cn/models",
        "check_interval": 14400,
        "config": {
            "category": "模型生态",
            "domain": "魔搭社区",
            "selector": ".model-card",
        },
    },

    # ━━ API 类 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "name": "Hugging Face Daily Papers",
        "type": "API",
        "url": "https://huggingface.co/api/daily_papers",
        "check_interval": 86400,
        "config": {
            "category": "学术论文",
            "domain": "每日精选论文",
            "method": "GET",
            "response_format": "json",
        },
    },
    {
        "name": "Papers With Code - SOTA",
        "type": "API",
        "url": "https://paperswithcode.com/api/v1/papers/",
        "check_interval": 86400,
        "config": {
            "category": "学术论文",
            "domain": "SOTA 论文追踪",
            "method": "GET",
            "response_format": "json",
            "params": {"ordering": "-published", "items_per_page": 20},
        },
    },
]


async def seed_whitelist(session):
    """种子域名白名单"""
    created, updated = 0, 0
    for item in WHITELIST_DOMAINS:
        stmt = select(DomainWhitelist).where(DomainWhitelist.domain == item["domain"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            existing.credibility = item["credibility"]
            existing.reason = item["reason"]
            existing.is_deleted = False
            updated += 1
        else:
            session.add(DomainWhitelist(
                domain=item["domain"],
                credibility=item["credibility"],
                reason=item["reason"],
            ))
            created += 1
    await session.flush()
    print(f"  域名白名单: 新增 {created}, 更新 {updated}")


async def seed_sources(session):
    """种子信息源"""
    created, skipped = 0, 0
    for item in SOURCES:
        stmt = select(InformationSource).where(InformationSource.url == item["url"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue
        session.add(InformationSource(
            name=item["name"],
            type=item["type"],
            url=item["url"],
            config=item.get("config"),
            status="ACTIVE",
            check_interval=item.get("check_interval", 3600),
        ))
        created += 1
    await session.flush()
    print(f"  信息源: 新增 {created}, 跳过(已存在) {skipped}")


async def main():
    print("=" * 50)
    print("AI Radar - 初始化信源种子数据")
    print("=" * 50)

    async with AsyncSessionLocal() as session:
        try:
            await seed_whitelist(session)
            await seed_sources(session)
            await session.commit()
            print("\n✅ 种子数据写入完成")
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 写入失败: {e}")
            raise

    # 打印汇总
    async with AsyncSessionLocal() as session:
        src_count = (await session.execute(
            select(InformationSource).where(InformationSource.is_deleted == False)
        )).scalars().all()
        wl_count = (await session.execute(
            select(DomainWhitelist).where(DomainWhitelist.is_deleted == False)
        )).scalars().all()
        print(f"\n当前数据库状态:")
        print(f"  信息源总数: {len(src_count)}")
        print(f"  白名单域名总数: {len(wl_count)}")

        print(f"\n信息源分类统计:")
        type_counts = {}
        for s in src_count:
            type_counts[s.type] = type_counts.get(s.type, 0) + 1
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
