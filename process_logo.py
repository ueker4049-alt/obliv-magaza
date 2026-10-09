from PIL import Image
import os

img_path = r"c:\Users\Umut\Desktop\magaza\static\images\logo.png"
img = Image.open(img_path).convert("RGBA")

datas = img.getdata()
newData = []
for item in datas:
    r, g, b, a = item
    brightness = max(r, g, b)
    if brightness < 30:
        newData.append((0, 0, 0, 0))
    elif brightness < 60:
        alpha = int(((brightness - 30) / 30.0) * a)
        newData.append((r, g, b, alpha))
    else:
        newData.append(item)

img.putdata(newData)

bbox = img.getbbox()
if bbox:
    cropped = img.crop(bbox)
    padded = Image.new("RGBA", (cropped.width + 16, cropped.height + 16), (0, 0, 0, 0))
    padded.paste(cropped, (8, 8))
    padded.save(r"c:\Users\Umut\Desktop\magaza\static\images\logo_transparent.png", "PNG")
    print("Logo transparent created and cropped successfully.")
else:
    img.save(r"c:\Users\Umut\Desktop\magaza\static\images\logo_transparent.png", "PNG")
    print("Saved without crop.")
