import re, json

html = open('page_dump.html', encoding='utf-8', errors='ignore').read()

# Look for SIGI_STATE or __UNIVERSAL_DATA_FOR_REHYDRATION__
m = re.search(r'id="__UNIVERSAL_DATA_FOR_REHYDRATION__"([^>]+)>([^<]+)</script>', html)
if m:
    data = json.loads(m.group(2))
    open('universal_data.json', 'w', encoding='utf-8').write(json.dumps(data, indent=2, ensure_ascii=False))
    print("Saved universal_data.json")
else:
    print("Not found universal data")

# Also find all image urls
img_urls = re.findall(r'https://[^"\'\s]+photomode-image\.jpeg[^"\'\s]*', html)
print("Photomode images:", len(img_urls))
open('photomode_urls.txt', 'w', encoding='utf-8').write('\n'.join(list(dict.fromkeys(img_urls))))
