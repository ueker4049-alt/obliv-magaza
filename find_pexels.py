import urllib.request
import re

url = 'https://www.pexels.com/search/girl%20mirror%20selfie/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        pattern = r'https://images\.pexels\.com/photos/\d+/[a-zA-Z0-9_\-\.]+\.(?:jpeg|jpg)'
        matches = list(set(re.findall(pattern, html)))
        print(f"Found {len(matches)} matches")
        for m in matches[:10]:
            print(m)
except Exception as e:
    print("Error:", e)
