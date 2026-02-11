from PIL import Image

img = Image.open('i8.png')

if img.mode == 'RGBA':
    img = img.convert('RGB')

# Force exact 4K dimensions (may distort)
img_4k = img.resize((3840, 2160), Image.Resampling.LANCZOS)
img_4k.save('output_exact_4k.jpg', quality=95, optimize=True)

print(f"Original size: {img.size}")
print(f"New size: {img_4k.size}")


