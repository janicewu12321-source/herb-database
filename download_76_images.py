"""
下载饲料原料目录7.6类品种植物图片（最新征求意见稿154种）
来源：iNaturalist API
图片保存至 ./images/，格式：76_{id:03d}_{name}.jpg
"""

import os, sys, time, json, urllib.request, urllib.parse, ssl
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGES_DIR = Path(__file__).parent / 'images'
UA = 'Mozilla/5.0 (compatible; HerbBot/1.0)'
CTX = ssl.create_default_context()
CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

HERBS_76 = [
    {"id":107,"name":"白术","latin":"Atractylodes macrocephala"},
    {"id":108,"name":"白芍","latin":"Paeonia lactiflora"},
    {"id":109,"name":"苍术","latin":"Atractylodes lancea"},
    {"id":110,"name":"川芎","latin":"Ligusticum chuanxiong"},
    {"id":111,"name":"车前子","latin":"Plantago asiatica"},
    {"id":112,"name":"车前草","latin":"Plantago asiatica"},
    {"id":113,"name":"补骨脂","latin":"Psoralea corylifolia"},
    {"id":114,"name":"刺五加","latin":"Eleutherococcus senticosus"},
    {"id":115,"name":"骨碎补","latin":"Drynaria fortunei"},
    {"id":116,"name":"厚朴","latin":"Magnolia officinalis"},
    {"id":117,"name":"绞股蓝","latin":"Gynostemma pentaphyllum"},
    {"id":118,"name":"红景天","latin":"Rhodiola rosea"},
    {"id":119,"name":"木香","latin":"Dolomiaea costus"},
    {"id":120,"name":"女贞子","latin":"Ligustrum lucidum"},
    {"id":121,"name":"五味子","latin":"Schisandra chinensis"},
    {"id":122,"name":"泽泻","latin":"Alisma plantago-aquatica"},
    {"id":123,"name":"知母","latin":"Anemarrhena asphodeloides"},
    {"id":124,"name":"枳壳","latin":"Citrus aurantium"},
    {"id":125,"name":"茜草","latin":"Rubia cordifolia"},
    {"id":126,"name":"诃子","latin":"Terminalia chebula"},
    {"id":127,"name":"胡芦巴","latin":"Trigonella foenum-graecum"},
    {"id":128,"name":"菟丝子","latin":"Cuscuta chinensis"},
    {"id":129,"name":"远志","latin":"Polygala tenuifolia"},
    {"id":130,"name":"益母草","latin":"Leonurus japonicus"},
    {"id":132,"name":"香附","latin":"Cyperus rotundus"},
    {"id":134,"name":"积雪草","latin":"Centella asiatica"},
    # 新增41种
    {"id":135,"name":"白子菜","latin":"Gynura divaricata"},
    {"id":136,"name":"柏子仁","latin":"Platycladus orientalis"},
    {"id":137,"name":"侧柏叶","latin":"Platycladus orientalis"},
    {"id":138,"name":"赤芍","latin":"Paeonia lactiflora"},
    {"id":139,"name":"大蓟","latin":"Cirsium japonicum"},
    {"id":140,"name":"地骨皮","latin":"Lycium chinense"},
    {"id":141,"name":"杜仲","latin":"Eucommia ulmoides"},
    {"id":142,"name":"厚朴花","latin":"Magnolia officinalis"},
    {"id":143,"name":"槐角","latin":"Styphnolobium japonicum"},
    {"id":144,"name":"金荞麦","latin":"Fagopyrum dibotrys"},
    {"id":145,"name":"金樱子","latin":"Rosa laevigata"},
    {"id":146,"name":"韭菜子","latin":"Allium tuberosum"},
    {"id":147,"name":"芦荟","latin":"Aloe vera"},
    {"id":148,"name":"玫瑰花","latin":"Rosa rugosa"},
    {"id":149,"name":"迷迭香","latin":"Salvia rosmarinus"},
    {"id":150,"name":"牛蒡子","latin":"Arctium lappa"},
    {"id":151,"name":"青皮","latin":"Citrus reticulata"},
    {"id":152,"name":"人参","latin":"Panax ginseng"},
    {"id":153,"name":"人参叶","latin":"Panax ginseng"},
    {"id":154,"name":"桑白皮","latin":"Morus alba"},
    {"id":155,"name":"桑枝","latin":"Morus alba"},
    {"id":156,"name":"升麻","latin":"Actaea cimicifuga"},
    {"id":157,"name":"酸角","latin":"Tamarindus indica"},
    {"id":158,"name":"土茯苓","latin":"Smilax glabra"},
    {"id":159,"name":"五加皮","latin":"Eleutherococcus gracilistylus"},
    {"id":160,"name":"五指毛桃","latin":"Ficus hirta"},
    {"id":161,"name":"洋槐花","latin":"Robinia pseudoacacia"},
    {"id":162,"name":"野菊花","latin":"Chrysanthemum indicum"},
    {"id":163,"name":"银杏叶","latin":"Ginkgo biloba"},
    {"id":164,"name":"越橘","latin":"Vaccinium vitis-idaea"},
    {"id":165,"name":"泽兰","latin":"Lycopus lucidus"},
    {"id":166,"name":"制何首乌","latin":"Reynoutria multiflora"},
    {"id":167,"name":"牛蒡根","latin":"Arctium lappa"},
    {"id":168,"name":"蒲黄","latin":"Typha angustifolia"},
    {"id":169,"name":"首乌藤","latin":"Reynoutria multiflora"},
    {"id":170,"name":"冬青科苦丁茶","latin":"Ilex kudingcha"},
    {"id":171,"name":"玫瑰茄","latin":"Hibiscus sabdariffa"},
    {"id":172,"name":"粗壮女贞苦丁茶","latin":"Ligustrum robustum"},
    {"id":173,"name":"平卧菊三七","latin":"Gynura procumbens"},
    {"id":174,"name":"杨树花","latin":"Populus"},
    {"id":175,"name":"绿茶","latin":"Camellia sinensis"},
]

def req(url, retries=2):
    rq = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(retries):
        try:
            with urllib.request.urlopen(rq, context=CTX, timeout=15) as resp:
                return resp.read()
        except Exception:
            if i == retries - 1: raise
            time.sleep(1)

def search_inaturalist(latin):
    url = f'https://api.inaturalist.org/v1/taxa/autocomplete?q={urllib.parse.quote(latin)}&is_active=true'
    try:
        data = req(url)
        result = json.loads(data.decode())
        for r in result.get('results', [])[:3]:
            photo = r.get('default_photo', {})
            if photo:
                img_url = photo.get('medium_url', '')
                if img_url:
                    return img_url
    except Exception:
        pass
    return None

def download(url, filepath):
    try:
        data = req(url)
        if data and len(data) > 2000:
            with open(filepath, 'wb') as f: f.write(data)
            return True
    except Exception: pass
    return False

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    success = 0; skip = 0; fail = 0
    print("=" * 60)
    print(f"7.6类品种图片下载 (iNaturalist, {len(HERBS_76)} 种)")
    print("=" * 60)

    for i, h in enumerate(HERBS_76, 1):
        hid = h["id"]; name = h["name"]; latin = h["latin"]
        filename = f"76_{hid:03d}_{name}.jpg"
        filepath = IMAGES_DIR / filename

        if filepath.exists() and filepath.stat().st_size > 2000:
            skip += 1
            continue

        url = search_inaturalist(latin)
        if url:
            if download(url, filepath):
                print(f"[{i:3d}/{len(HERBS_76)}] {name}: OK")
                success += 1
            else:
                print(f"[{i:3d}/{len(HERBS_76)}] {name}: download failed")
                fail += 1
        else:
            print(f"[{i:3d}/{len(HERBS_76)}] {name}: no image")
            fail += 1

        if i < len(HERBS_76): time.sleep(1.2)

    print(f"\n{'='*60}")
    print(f"Done: {success} new, {skip} skipped, {fail} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
