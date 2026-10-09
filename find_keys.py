import json

data = json.load(open('universal_data.json', encoding='utf-8'))

def find_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(term in k.lower() for term in ['item', 'video', 'image', 'photo', 'post', 'music', 'sound', 'title']):
                print(f"Match key: {path}.{k} -> {type(v).__name__}")
            find_keys(v, f"{path}.{k}")
    elif isinstance(obj, list) and len(obj) > 0:
        find_keys(obj[0], f"{path}[0]")

find_keys(data)
