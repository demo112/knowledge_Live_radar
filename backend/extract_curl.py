import subprocess
import re
import sys

def get_wechat_nickname(url):
    try:
        # Use curl to fetch content, emulating a browser
        cmd = [
            'curl', '-L', 
            '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        html = result.stdout
        
        # Pattern 1: var nickname = "..."
        match = re.search(r'var\s+nickname\s*=\s*"([^"]+)"', html)
        if match:
            return match.group(1)
            
        # Pattern 2: profile_nickname">...</strong>
        match = re.search(r'profile_nickname">([^<]+)<', html)
        if match:
            return match.group(1).strip()
            
        # Pattern 3: js_name">...</a>
        match = re.search(r'js_name">\s*([^<]+)\s*<', html)
        if match:
            return match.group(1).strip()
            
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    urls = [
        "https://mp.weixin.qq.com/s/iULo3kWt0Th82FKoaW4SMQ",
        "https://mp.weixin.qq.com/s/tq1w6FREMiYoPzTXCsQsKg"
    ]
    for url in urls:
        print(f"URL: {url}")
        nick = get_wechat_nickname(url)
        print(f"Nickname: {nick}")
