"""
下载饲料原料目录7.6类独有品种（非药食同源）的植物图片
来源：iNaturalist → Wikimedia Commons → PPBC
图片保存至 ./images/ 目录，文件名格式：76_{id:03d}_{name}.jpg
"""

import os, sys, time, json, urllib.request, urllib.parse, urllib.error, ssl, re
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGES_DIR = Path(__file__).parent / 'images'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# 28种在饲料目录7.6中但不在106种药食同源目录中的植物
HERBS_76 = [
    {"id":1,"name":"白术","latin":"Atractylodes macrocephala","family":"菊科","part":"干燥根茎","efficacy":["健脾祛湿"]},
    {"id":2,"name":"白芍","latin":"Paeonia lactiflora","family":"毛茛科","part":"干燥根","efficacy":["养血柔肝"]},
    {"id":3,"name":"苍术","latin":"Atractylodes lancea","family":"菊科","part":"干燥根茎","efficacy":["燥湿健脾"]},
    {"id":4,"name":"川芎","latin":"Ligusticum chuanxiong","family":"伞形科","part":"干燥根茎","efficacy":["活血行气"]},
    {"id":5,"name":"车前子","latin":"Plantago asiatica","family":"车前科","part":"干燥成熟种子","efficacy":["利尿通淋"]},
    {"id":6,"name":"车前草","latin":"Plantago asiatica","family":"车前科","part":"干燥全草","efficacy":["清热利尿"]},
    {"id":7,"name":"补骨脂","latin":"Psoralea corylifolia","family":"豆科","part":"干燥成熟果实","efficacy":["温肾助阳"]},
    {"id":8,"name":"刺五加","latin":"Acanthopanax senticosus","family":"五加科","part":"干燥根和根茎","efficacy":["益气健脾"]},
    {"id":9,"name":"骨碎补","latin":"Drynaria fortunei","family":"水龙骨科","part":"干燥根茎","efficacy":["补肾强骨"]},
    {"id":10,"name":"厚朴","latin":"Magnolia officinalis","family":"木兰科","part":"干燥干皮/根皮/枝皮","efficacy":["行气燥湿"]},
    {"id":11,"name":"绞股蓝","latin":"Gynostemma pentaphyllum","family":"葫芦科","part":"干燥全草","efficacy":["免疫调节"]},
    {"id":12,"name":"红景天","latin":"Rhodiola rosea","family":"景天科","part":"干燥根和根茎","efficacy":["抗疲劳"]},
    {"id":13,"name":"木香","latin":"Aucklandia lappa","family":"菊科","part":"干燥根","efficacy":["行气止痛"]},
    {"id":14,"name":"女贞子","latin":"Ligustrum lucidum","family":"木犀科","part":"干燥成熟果实","efficacy":["滋补肝肾"]},
    {"id":15,"name":"五味子","latin":"Schisandra chinensis","family":"木兰科","part":"干燥成熟果实","efficacy":["收敛固涩"]},
    {"id":16,"name":"泽泻","latin":"Alisma plantago-aquatica","family":"泽泻科","part":"干燥块茎","efficacy":["利水渗湿"]},
    {"id":17,"name":"知母","latin":"Anemarrhena asphodeloides","family":"百合科","part":"干燥根茎","efficacy":["清热泻火"]},
    {"id":18,"name":"枳壳","latin":"Citrus aurantium","family":"芸香科","part":"干燥未成熟果实","efficacy":["理气宽中"]},
    {"id":19,"name":"茜草","latin":"Rubia cordifolia","family":"茜草科","part":"干燥根和根茎","efficacy":["凉血止血"]},
    {"id":20,"name":"诃子","latin":"Terminalia chebula","family":"使君子科","part":"干燥成熟果实","efficacy":["涩肠敛肺"]},
    {"id":21,"name":"胡芦巴","latin":"Trigonella foenum-graecum","family":"豆科","part":"干燥成熟种子","efficacy":["温肾祛寒"]},
    {"id":22,"name":"菟丝子","latin":"Cuscuta chinensis","family":"旋花科","part":"干燥成熟种子","efficacy":["补肾固精"]},
    {"id":23,"name":"远志","latin":"Polygala tenuifolia","family":"远志科","part":"干燥根","efficacy":["安神益智"]},
    {"id":24,"name":"益母草","latin":"Leonurus japonicus","family":"唇形科","part":"干燥地上部分","efficacy":["活血调经"]},
    {"id":25,"name":"夏枯草","latin":"Prunella vulgaris","family":"唇形科","part":"干燥果穗","efficacy":["清肝明目"]},
    {"id":26,"name":"香附","latin":"Cyperus rotundus","family":"莎草科","part":"干燥根茎","efficacy":["疏肝理气"]},
    {"id":27,"name":"辛夷","latin":"Magnolia biondii","family":"木兰科","part":"干燥花蕾","efficacy":["散风寒"]},
    {"id":28,"name":"积雪草","latin":"Centella asiatica","family":"伞形科","part":"干燥全草","efficacy":["清热利湿"]},
]

def make_request(url, retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
                return resp.read()
        except Exception as e:
            if attempt == retries - 1: raise
            time.sleep(2)
    return None

def search_inaturalist(latin):
    url = f'https://api.inaturalist.org/v1/taxa/autocomplete?q={urllib.parse.quote(latin)}&is_active=true'
    try:
        data = make_request(url)
        if data:
            result = json.loads(data.decode())
            for r in result.get('results', [])[:3]:
                photo = r.get('default_photo', {})
                if photo:
                    img_url = photo.get('medium_url', '')
                    if img_url:
                        return {"img_url": img_url, "source": "inaturalist", "match": r['name']}
    except Exception: pass
    return None

def search_wikimedia(latin):
    url = (f"https://commons.wikimedia.org/w/api.php?action=query&list=search"
           f"&srsearch={urllib.parse.quote(latin)}&srnamespace=6&format=json&srlimit=5")
    try:
        data = make_request(url)
        if data:
            result = json.loads(data.decode())
            for page in result.get("query", {}).get("search", []):
                title = page.get("title", "")
                if title.lower().endswith(('.jpg', '.jpeg', '.png')):
                    encoded = urllib.parse.quote(title.replace("File:", ""))
                    return {"img_url": f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=400", "source": "wikimedia"}
    except Exception: pass
    return None

def download_image(url, filepath):
    try:
        data = make_request(url)
        if data and len(data) > 2000:
            with open(filepath, 'wb') as f: f.write(data)
            return True
    except Exception as e:
        print(f"    下载失败: {e}")
    return False

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    success = 0

    print("=" * 60)
    print("饲料目录7.6独有品种图片下载（非药食同源）")
    print(f"共 {len(HERBS_76)} 种")
    print("=" * 60)

    for i, h in enumerate(HERBS_76, 1):
        filename = f"76_{h['id']:03d}_{h['name']}.jpg"
        filepath = IMAGES_DIR / filename
        latin = h['latin']

        print(f"\n[{i}/{len(HERBS_76)}] {h['name']} ({latin})")

        if filepath.exists() and filepath.stat().st_size > 2000:
            print(f"  ✓ 已存在，跳过")
            success += 1
            continue

        downloaded = False
        sources_tried = []

        # 策略1: iNaturalist
        print(f"  尝试 iNaturalist...")
        result = search_inaturalist(latin)
        if result and result.get('img_url'):
            sources_tried.append(f"iNaturalist (match: {result.get('match', '?')})")
            if download_image(result['img_url'], filepath):
                print(f"  ✓ 下载成功")
                downloaded = True

        # 策略2: Wikimedia
        if not downloaded:
            print(f"  尝试 Wikimedia Commons...")
            result = search_wikimedia(latin)
            if result and result.get('img_url'):
                sources_tried.append("Wikimedia")
                if download_image(result['img_url'], filepath):
                    print(f"  ✓ 下载成功")
                    downloaded = True

        if downloaded:
            success += 1
        else:
            print(f"  ✗ 未找到 ({', '.join(sources_tried) if sources_tried else '无匹配'})")

        if i < len(HERBS_76):
            time.sleep(1.5)

    print(f"\n{'='*60}")
    print(f"完成: {success}/{len(HERBS_76)} 种")
    print(f"图片目录: {IMAGES_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
