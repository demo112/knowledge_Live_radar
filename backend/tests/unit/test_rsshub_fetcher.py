import pytest
from app.services.fetchers.rsshub import RSSHubFetcher

@pytest.mark.asyncio
async def test_rsshub_url_conversion():
    # Test WeChat MP
    fetcher = RSSHubFetcher("WECHAT_MP")
    assert fetcher._get_rsshub_path("my-gzh-id") == "/wechat/gzh/my-gzh-id"

    # Test Bilibili User ID
    fetcher = RSSHubFetcher("BILIBILI_USER")
    assert fetcher._get_rsshub_path("123456") == "/bilibili/user/video/123456"
    assert fetcher._get_rsshub_path("https://space.bilibili.com/123456") == "/bilibili/user/video/123456"

    # Test Juejin Column
    fetcher = RSSHubFetcher("JUEJIN_COLUMN")
    assert fetcher._get_rsshub_path("789012") == "/juejin/columns/789012"
