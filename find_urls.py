import re

html = open('page_dump.html', encoding='utf-8', errors='ignore').read()
urls = [u for u in re.findall(r'https://[^"\'\s<>]+', html) if 'tos-' in u or 'photomode' in u or 'tiktokcdn.com' in u]
unique_urls = list(dict.fromkeys(urls))
print(f"Total matching urls: {len(unique_urls)}")
for u in unique_urls[:20]:
    print(u)

with open('all_tiktok_urls.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(unique_urls))
