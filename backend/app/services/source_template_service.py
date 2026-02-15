from typing import List, Dict, Any, Optional
from app.schemas.source_template import SourceTemplate, SourceTemplateConfigField

class SourceTemplateService:
    def __init__(self):
        self._templates = self._init_templates()

    def _init_templates(self) -> List[SourceTemplate]:
        return [
            SourceTemplate(
                id="arxiv_rss",
                name="arXiv 订阅源",
                description="订阅 arXiv 特定类别的最新论文更新",
                source_type="RSS",
                config_schema=[
                    SourceTemplateConfigField(
                        name="category",
                        label="arXiv 类别",
                        type="text",
                        default="cs.AI",
                        description="例如: cs.AI (人工智能), cs.LG (机器学习), cs.CL (计算语言学)"
                    )
                ],
                default_config={
                    "url_template": "http://export.arxiv.org/rss/{category}",
                    "content_selector": "summary"
                }
            ),
            SourceTemplate(
                id="github_trending",
                name="GitHub 趋势",
                description="订阅 GitHub 热门项目趋势",
                source_type="API",
                config_schema=[
                    SourceTemplateConfigField(
                        name="language",
                        label="编程语言",
                        type="text",
                        default="python",
                        description="例如: python, typescript, rust"
                    ),
                    SourceTemplateConfigField(
                        name="since",
                        label="时间范围",
                        type="select",
                        default="daily",
                        options=[
                            {"label": "今天", "value": "daily"},
                            {"label": "本周", "value": "weekly"},
                            {"label": "本月", "value": "monthly"}
                        ]
                    )
                ],
                default_config={
                    "url": "https://api.gitterapp.com/repositories", # 示例 API
                    "headers": {"Accept": "application/json"}
                }
            ),
            SourceTemplate(
                id="huggingface_daily",
                name="HuggingFace 每日论文",
                description="获取 HuggingFace Daily Papers",
                source_type="WEB",
                config_schema=[],
                default_config={
                    "url": "https://huggingface.co/papers",
                    "content_selector": "article.flex.flex-col"
                }
            ),
            SourceTemplate(
                id="blog_rss",
                name="通用博客 RSS",
                description="订阅支持 RSS/Atom 的技术博客",
                source_type="RSS",
                config_schema=[
                    SourceTemplateConfigField(
                        name="rss_url",
                        label="RSS 地址",
                        type="text",
                        required=True,
                        description="博客的 RSS 或 Atom Feed URL"
                    )
                ],
                default_config={}
            ),
            SourceTemplate(
                id="substack_newsletter",
                name="Substack 专栏",
                description="订阅 Substack 专栏文章",
                source_type="RSS",
                config_schema=[
                    SourceTemplateConfigField(
                        name="subdomain",
                        label="Substack 子域名",
                        type="text",
                        default="example",
                        description="例如: 'lilianweng' (lilianweng.substack.com)"
                    )
                ],
                default_config={
                    "url_template": "https://{subdomain}.substack.com/feed",
                    "content_selector": "content:encoded"
                }
            ),
            SourceTemplate(
                id="github_release",
                name="GitHub 版本发布",
                description="监控 GitHub 项目版本发布",
                source_type="API",
                config_schema=[
                    SourceTemplateConfigField(
                        name="repo",
                        label="仓库路径",
                        type="text",
                        default="owner/repo",
                        description="例如: 'facebook/react'"
                    )
                ],
                default_config={
                    "url_template": "https://api.github.com/repos/{repo}/releases",
                    "content_selector": "body"
                }
            ),
            SourceTemplate(
                id="website_sitemap",
                name="网站 Sitemap",
                description="通过 Sitemap 抓取网站更新",
                source_type="Sitemap",
                config_schema=[
                    SourceTemplateConfigField(
                        name="url",
                        label="Sitemap URL",
                        type="text",
                        default="https://example.com/sitemap.xml",
                        description="完整的 Sitemap XML 地址"
                    )
                ],
                default_config={
                    "url_template": "{url}",
                    "content_selector": "loc"
                }
            )
        ]

    def get_templates(self) -> List[SourceTemplate]:
        return self._templates

    def get_template(self, template_id: str) -> Optional[SourceTemplate]:
        for t in self._templates:
            if t.id == template_id:
                return t
        return None

    def generate_source_config(self, template_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据模板和参数生成信息源配置
        返回字典包含: name (默认), type, url, config
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        result = {
            "type": template.source_type,
            "config": {}
        }

        # 1. arXiv RSS
        if template.id == "arxiv_rss":
            category = params.get("category", "cs.AI")
            url = template.default_config["url_template"].format(category=category)
            result["url"] = url
            result["name"] = f"arXiv {category}"
            result["config"] = {"content_selector": template.default_config.get("content_selector")}
            
        # 2. GitHub Trending
        elif template.id == "github_trending":
            language = params.get("language", "python")
            since = params.get("since", "daily")
            # 这里只是示例 URL，实际可能需要专门的 Fetcher 支持
            result["url"] = f"https://github.com/trending/{language}?since={since}"
            result["name"] = f"GitHub 趋势 ({language})"
            result["config"] = {
                "fetcher_type": "github_trending", # 指示使用特定的 Fetcher 逻辑
                "params": {"language": language, "since": since}
            }

        # 3. HuggingFace Daily
        elif template.id == "huggingface_daily":
            result["url"] = template.default_config["url"]
            result["name"] = "HuggingFace 每日论文"
            result["config"] = {
                "content_selector": template.default_config.get("content_selector")
            }

        # 4. Generic RSS
        elif template.id == "blog_rss":
            url = params.get("rss_url")
            if not url:
                raise ValueError("rss_url is required for blog_rss template")
            result["url"] = url
            # 尝试从 URL 提取名称作为默认名，或者让用户后续修改
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            result["name"] = f"博客 ({domain})"
            result["config"] = {}

        return result
