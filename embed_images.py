"""
将 images/ 目录中的图片转为 base64 内嵌到 index.html 中，
生成一个完全自包含的 HTML 文件，无需外部图片文件即可在任何浏览器打开。
支持植株图片和药材图片（med_前缀）。
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

# 读取所有图片并转为 base64 data URI（分为植株和药材两类）
plant_cache = {}
med_cache = {}
print("读取图片文件...")
if IMAGES_DIR.exists():
    for f in sorted(IMAGES_DIR.iterdir()):
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
            with open(f, 'rb') as img_file:
                data = base64.b64encode(img_file.read()).decode('ascii')
            ext = f.suffix.lower().replace('.', '')
            if ext == 'jpg': ext = 'jpeg'
            mime = f'image/{ext}'
            key = f.stem
            b64 = f'data:{mime};base64,{data}'
            if key.startswith('med_'):
                med_cache[key] = b64
            else:
                plant_cache[key] = b64
            print(f'  OK {key} ({len(data)//1024}KB)')
print(f'\nPlant: {len(plant_cache)}, Medicinal: {len(med_cache)}, Total: {len(plant_cache)+len(med_cache)} images')

# 读取原始 HTML
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 构建 base64 图片映射
plant_map = ',\n'.join(f'  "{k}": "{v}"' for k, v in sorted(plant_cache.items()))
med_map = ',\n'.join(f'  "{k}": "{v}"' for k, v in sorted(med_cache.items()))

# 替换 getImagePath 函数（植株图片）
new_plant = f'''// Plant images embedded as base64
const EMBEDDED_IMAGES = {{
{plant_map}
}};

function getImagePath(h) {{
  if (h.id >= 107) {{
    const key = `76_${{String(h.id-106).padStart(3,"0")}}_${{h.name}}`;
    if (EMBEDDED_IMAGES[key]) return EMBEDDED_IMAGES[key];
    return `images/76_${{String(h.id-106).padStart(3,"0")}}_${{h.name}}.jpg`;
  }}
  const key = `${{String(h.id).padStart(3,"0")}}_${{h.name}}`;
  if (EMBEDDED_IMAGES[key]) return EMBEDDED_IMAGES[key];
  return `images/${{String(h.id).padStart(3,"0")}}_${{h.name}}.jpg`;
}}'''

html = re.sub(r'function getImagePath\(h\) \{[\s\S]*?\n\}', new_plant, html)

# 替换 getMedImagePath 函数（药材图片）
new_med = f'''// Medicinal images embedded as base64
const EMBEDDED_MED_IMAGES = {{
{med_map}
}};

function getMedImagePath(h) {{
  if (h.id >= 107) {{
    const key = `med_76_${{String(h.id-106).padStart(3,"0")}}_${{h.name}}`;
    if (EMBEDDED_MED_IMAGES[key]) return EMBEDDED_MED_IMAGES[key];
    return `images/med_76_${{String(h.id-106).padStart(3,"0")}}_${{h.name}}.jpg`;
  }}
  const key = `med_${{String(h.id).padStart(3,"0")}}_${{h.name}}`;
  if (EMBEDDED_MED_IMAGES[key]) return EMBEDDED_MED_IMAGES[key];
  return `images/med_${{String(h.id).padStart(3,"0")}}_${{h.name}}.jpg`;
}}'''

html = re.sub(r'function getMedImagePath\(h\) \{[\s\S]*?\n\}', new_med, html)

# 更新提示文字
html = html.replace(
    '本地图片由 download_images.py 脚本下载。若未显示图片，请运行脚本或点击上方链接查看外部数据库照片。',
    f'植物图片{len(plant_cache)}张 + 药材图片{len(med_cache)}张已内嵌为 base64。'
)

# 写入输出文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(html)

size_mb = os.path.getsize(OUTPUT_FILE) / (1024*1024)
total = len(plant_cache) + len(med_cache)
print(f'\nGenerated: {OUTPUT_FILE}')
print(f'File size: {size_mb:.1f} MB')
print(f'Images embedded: {total} (plant: {len(plant_cache)}, medicinal: {len(med_cache)})')
