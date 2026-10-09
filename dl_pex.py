import urllib.request
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

test_urls = [
    ('pex_1.jpg', 'https://images.pexels.com/photos/14724112/pexels-photo-14724112.jpeg?auto=compress&cs=tinysrgb&w=800'),
    ('pex_2.jpg', 'https://images.pexels.com/photos/17733583/pexels-photo-17733583.jpeg?auto=compress&cs=tinysrgb&w=800'),
    ('pex_3.jpg', 'https://images.pexels.com/photos/4576911/pexels-photo-4576911.jpeg?auto=compress&cs=tinysrgb&w=800'),
    ('pex_4.jpg', 'https://images.pexels.com/photos/5225115/pexels-photo-5225115.jpeg?auto=compress&cs=tinysrgb&w=800'),
    ('pex_5.jpg', 'https://images.pexels.com/photos/18961047/pexels-photo-18961047.jpeg?auto=compress&cs=tinysrgb&w=800'),
    ('pex_6.jpg', 'https://images.pexels.com/photos/1871340/pexels-photo-1871340.jpeg?auto=compress&cs=tinysrgb&w=800'),
]

for name, u in test_urls:
    try:
        req = urllib.request.Request(u, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(name, 'wb') as f:
                f.write(data)
            print(f"Downloaded {name} ({len(data)} bytes)")
    except Exception as e:
        print(f"Failed {name}: {e}")
