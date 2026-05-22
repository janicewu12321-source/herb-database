"""
将 images/ 目录中的植物图片转为 base64 内嵌到 index.html 中，
生成一个完全自包含的 HTML 文件，无需外部图片文件即可在任何浏览器打开。
"""

import sys
import os
import base64
import re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / 'images'
HTML_FILE = BASE_DIR / 'index.html'
OUTPUT_FILE = BASE_DIR / 'index_embedded.html'

# 读取所有图片并转为 base64 data URI
image_cache = {}
print("读取图片文件...")
if IMAGES_DIR.exists():
    for f in sorted(IMAGES_DIR.iterdir()):
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            with open(f, 'rb') as img_file:
                data = base64.b64encode(img_file.read()).decode('ascii')
            ext = f.suffix.lower().replace('.', '')
            if ext == 'jpg': ext = 'jpeg'
            mime = f'image/{ext}'
            # key: "001_八角茴香"
            key = f.stem  # e.g. "001_八角茴香"
            image_cache[key] = f'data:{mime};base64,{data}'
            print(f'  ✓ {key} ({len(data)//1024}KB base64)')
else:
    print("images/ 目录不存在，请先运行 download_images.py")

print(f"\n共 {len(image_cache)} 张图片已编码")

# 读取原始 HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 替换 getImagePath 函数为内嵌 base64 版本
# 原函数: images/${id}_{name}.jpg → 直接注入 base64 data URI

new_get_image = '''// ⚠️ 此文件由 embed_images.py 自动生成，图片已内嵌为 base64
const EMBEDDED_IMAGES = {
''' + ',\n'.join(f'  "{k}": "{v}"' for k, v in sorted(image_cache.items())) + '''
};

function getImagePath(h) {
  const key = `${String(h.id).padStart(3,"0")}_${h.name}`;
  if (EMBEDDED_IMAGES[key]) return EMBEDDED_IMAGES[key];
  // fallback: try to load from images/ folder
  return `images/${String(h.id).padStart(3,"0")}_${h.name}.jpg`;
}'''

# 替换旧的 getImagePath 函数
html = re.sub(
    r'function getImagePath\(h\) \{[\s\S]*?\n\}',
    new_get_image,
    html
)

# 更新提示文字
html = html.replace(
    '本地图片由 download_images.py 脚本下载。若未显示图片，请运行脚本或点击上方链接查看外部数据库照片。',
    '图片已内嵌为 base64 编码，此文件可独立使用，无需外部图片文件。'
)

# 写入输出文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(OUTPUT_FILE) / (1024*1024)
print(f"\n✅ 已生成: {OUTPUT_FILE}")
print(f"   文件大小: {size_mb:.1f} MB")
print(f"   内嵌图片: {len(image_cache)} 张")
print(f"   可直接用浏览器打开，无需 images/ 目录")
