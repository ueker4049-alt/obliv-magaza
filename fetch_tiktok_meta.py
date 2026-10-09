import urllib.request, re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
urls = [
    'https://www.tiktok.com/@dreampay2/video/7647918894744636704',
    'https://www.tiktok.com/@mostwize.society/video/7462972807756958981'
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            title = re.findall(r'<title>(.*?)</title>', html)
            desc = re.findall(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', html)
            if not desc:
                desc = re.findall(r'name="description"\s*content="([^"]*)"', html)
            print(url)
            print("TITLE:", title)
            print("DESC:", desc)
    except Exception as e:
        print(url, "ERROR:", e)
