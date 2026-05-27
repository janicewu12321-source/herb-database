"""
中药材（饮片/药材）图片批量下载脚本
数据源：Wikimedia Commons API → Baidu Baike
图片保存至 ./images/ 目录，文件名格式：med_{id:03d}_{name}.jpg
"""

import os, sys, time, json, urllib.request, urllib.parse, urllib.error, ssl
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGES_DIR = Path(__file__).parent / 'images'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# 134种药材（106药食同源 + 28种7.6独有）
HERBS = [
    # === 106 药食同源 ===
    {"id":1,"name":"八角茴香","latin":"Illicium verum"},
    {"id":2,"name":"刀豆","latin":"Canavalia gladiata"},
    {"id":3,"name":"小茴香","latin":"Foeniculum vulgare"},
    {"id":4,"name":"山楂","latin":"Crataegus pinnatifida"},
    {"id":5,"name":"乌梅","latin":"Prunus mume"},
    {"id":6,"name":"木瓜","latin":"Chaenomeles speciosa"},
    {"id":7,"name":"火麻仁","latin":"Cannabis sativa"},
    {"id":8,"name":"龙眼肉","latin":"Dimocarpus longan"},
    {"id":9,"name":"决明子","latin":"Senna obtusifolia"},
    {"id":10,"name":"肉豆蔻","latin":"Myristica fragrans"},
    {"id":11,"name":"余甘子","latin":"Phyllanthus emblica"},
    {"id":12,"name":"佛手","latin":"Citrus medica"},
    {"id":13,"name":"杏仁","latin":"Prunus armeniaca"},
    {"id":14,"name":"沙棘","latin":"Hippophae rhamnoides"},
    {"id":15,"name":"芡实","latin":"Euryale ferox"},
    {"id":16,"name":"花椒","latin":"Zanthoxylum bungeanum"},
    {"id":17,"name":"赤小豆","latin":"Vigna umbellata"},
    {"id":18,"name":"麦芽","latin":"Hordeum vulgare"},
    {"id":19,"name":"枣","latin":"Ziziphus jujuba"},
    {"id":20,"name":"罗汉果","latin":"Siraitia grosvenorii"},
    {"id":21,"name":"郁李仁","latin":"Prunus humilis"},
    {"id":22,"name":"青果","latin":"Canarium album"},
    {"id":23,"name":"枳椇子","latin":"Hovenia dulcis"},
    {"id":24,"name":"枸杞子","latin":"Lycium barbarum"},
    {"id":25,"name":"栀子","latin":"Gardenia jasminoides"},
    {"id":26,"name":"砂仁","latin":"Amomum villosum"},
    {"id":27,"name":"胖大海","latin":"Sterculia lychnophora"},
    {"id":28,"name":"桃仁","latin":"Prunus persica"},
    {"id":29,"name":"桑椹","latin":"Morus alba"},
    {"id":30,"name":"益智仁","latin":"Alpinia oxyphylla"},
    {"id":31,"name":"莱菔子","latin":"Raphanus sativus"},
    {"id":32,"name":"莲子","latin":"Nelumbo nucifera"},
    {"id":33,"name":"黄芥子","latin":"Brassica juncea"},
    {"id":34,"name":"紫苏籽","latin":"Perilla frutescens"},
    {"id":35,"name":"黑芝麻","latin":"Sesamum indicum"},
    {"id":36,"name":"黑胡椒","latin":"Piper nigrum"},
    {"id":37,"name":"槐米","latin":"Styphnolobium japonicum"},
    {"id":38,"name":"榧子","latin":"Torreya grandis"},
    {"id":39,"name":"酸枣仁","latin":"Ziziphus jujuba"},
    {"id":40,"name":"薏苡仁","latin":"Coix lacryma-jobi"},
    {"id":41,"name":"覆盆子","latin":"Rubus chingii"},
    {"id":42,"name":"橘皮","latin":"Citrus reticulata"},
    {"id":43,"name":"丁香","latin":"Syzygium aromaticum"},
    {"id":44,"name":"小蓟","latin":"Cirsium arvense"},
    {"id":45,"name":"马齿苋","latin":"Portulaca oleracea"},
    {"id":46,"name":"代代花","latin":"Citrus aurantium"},
    {"id":47,"name":"白扁豆花","latin":"Lablab purpureus"},
    {"id":48,"name":"鱼腥草","latin":"Houttuynia cordata"},
    {"id":49,"name":"薄荷","latin":"Mentha canadensis"},
    {"id":50,"name":"金银花","latin":"Lonicera japonica"},
    {"id":51,"name":"香薷","latin":"Mosla chinensis"},
    {"id":52,"name":"桑叶","latin":"Morus alba"},
    {"id":53,"name":"荷叶","latin":"Nelumbo nucifera"},
    {"id":54,"name":"淡竹叶","latin":"Lophatherum gracile"},
    {"id":55,"name":"菊花","latin":"Chrysanthemum morifolium"},
    {"id":56,"name":"槐花","latin":"Styphnolobium japonicum"},
    {"id":57,"name":"蒲公英","latin":"Taraxacum mongolicum"},
    {"id":58,"name":"藿香","latin":"Pogostemon cablin"},
    {"id":59,"name":"紫苏","latin":"Perilla frutescens"},
    {"id":60,"name":"山药","latin":"Dioscorea polystachya"},
    {"id":61,"name":"玉竹","latin":"Polygonatum odoratum"},
    {"id":62,"name":"甘草","latin":"Glycyrrhiza uralensis"},
    {"id":63,"name":"白芷","latin":"Angelica dahurica"},
    {"id":64,"name":"百合","latin":"Lilium lancifolium"},
    {"id":65,"name":"肉桂","latin":"Cinnamomum cassia"},
    {"id":66,"name":"姜","latin":"Zingiber officinale"},
    {"id":67,"name":"桔梗","latin":"Platycodon grandiflorus"},
    {"id":68,"name":"高良姜","latin":"Alpinia officinarum"},
    {"id":69,"name":"黄精","latin":"Polygonatum sibiricum"},
    {"id":70,"name":"葛根","latin":"Pueraria montana"},
    {"id":71,"name":"薤白","latin":"Allium macrostemon"},
    {"id":72,"name":"桔红","latin":"Citrus reticulata"},
    {"id":73,"name":"鲜白茅根","latin":"Imperata cylindrica"},
    {"id":74,"name":"鲜芦根","latin":"Phragmites australis"},
    {"id":75,"name":"昆布","latin":"Saccharina japonica"},
    {"id":76,"name":"茯苓","latin":"Wolfiporia extensa"},
    {"id":77,"name":"淡豆豉","latin":"Glycine max"},
    {"id":78,"name":"乌梢蛇","latin":"Ptyas dhumnades"},
    {"id":79,"name":"牡蛎","latin":"Crassostrea gigas"},
    {"id":80,"name":"阿胶","latin":"Equus asinus"},
    {"id":81,"name":"鸡内金","latin":"Gallus gallus"},
    {"id":82,"name":"蜂蜜","latin":"Apis cerana"},
    {"id":83,"name":"蝮蛇","latin":"Deinagkistrodon acutus"},
    {"id":84,"name":"白果","latin":"Ginkgo biloba"},
    {"id":85,"name":"白扁豆","latin":"Lablab purpureus"},
    {"id":86,"name":"菊苣","latin":"Cichorium intybus"},
    {"id":87,"name":"香橼","latin":"Citrus medica"},
    {"id":88,"name":"当归","latin":"Angelica sinensis"},
    {"id":89,"name":"山柰","latin":"Kaempferia galanga"},
    {"id":90,"name":"西红花","latin":"Crocus sativus"},
    {"id":91,"name":"草果","latin":"Amomum tsao-ko"},
    {"id":92,"name":"姜黄","latin":"Curcuma longa"},
    {"id":93,"name":"荜茇","latin":"Piper longum"},
    {"id":94,"name":"党参","latin":"Codonopsis pilosula"},
    {"id":95,"name":"肉苁蓉","latin":"Cistanche deserticola"},
    {"id":96,"name":"铁皮石斛","latin":"Dendrobium officinale"},
    {"id":97,"name":"西洋参","latin":"Panax quinquefolius"},
    {"id":98,"name":"黄芪","latin":"Astragalus mongholicus"},
    {"id":99,"name":"灵芝","latin":"Ganoderma lucidum"},
    {"id":100,"name":"山茱萸","latin":"Cornus officinalis"},
    {"id":101,"name":"天麻","latin":"Gastrodia elata"},
    {"id":102,"name":"杜仲叶","latin":"Eucommia ulmoides"},
    {"id":103,"name":"地黄","latin":"Rehmannia glutinosa"},
    {"id":104,"name":"麦冬","latin":"Ophiopogon japonicus"},
    {"id":105,"name":"天冬","latin":"Asparagus cochinchinensis"},
    {"id":106,"name":"化橘红","latin":"Citrus grandis"},
    # === 28种 7.6独有 ===
    {"id":107,"name":"白术","latin":"Atractylodes macrocephala"},
    {"id":108,"name":"白芍","latin":"Paeonia lactiflora"},
    {"id":109,"name":"苍术","latin":"Atractylodes lancea"},
    {"id":110,"name":"川芎","latin":"Ligusticum striatum"},
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
    {"id":131,"name":"夏枯草","latin":"Prunella vulgaris"},
    {"id":132,"name":"香附","latin":"Cyperus rotundus"},
    {"id":133,"name":"辛夷","latin":"Magnolia biondii"},
    {"id":134,"name":"积雪草","latin":"Centella asiatica"},
]

def make_request(url, retries=2):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=12) as resp:
                return resp.read()
        except Exception:
            if attempt == retries - 1: raise
            time.sleep(1)
    return None

def search_wikimedia_medicine(latin, chinese_name):
    """搜索Wikimedia Commons上中药材/饮片相关图片"""
    # 搜索策略：拉丁名 + 中文名 + 药用部位关键词
    queries = [
        f"{latin} dried root slice",
        f"{latin} medicinal",
        f"{chinese_name} 饮片",
        f"{chinese_name} 药材",
        f"{latin} root",
    ]

    for query in queries:
        try:
            url = (f"https://commons.wikimedia.org/w/api.php?action=query"
                   f"&list=search&srsearch={urllib.parse.quote(query)}"
                   f"&srnamespace=6&format=json&srlimit=5")
            data = make_request(url)
            if not data: continue
            result = json.loads(data.decode())
            pages = result.get("query", {}).get("search", [])
            for page in pages:
                title = page.get("title", "")
                if title.lower().endswith(('.jpg', '.jpeg', '.png')):
                    encoded = urllib.parse.quote(title.replace("File:", ""))
                    img_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=400"
                    return {"img_url": img_url, "source": "wikimedia", "query": query}
        except Exception:
            continue
    return None

def download_image(url, filepath):
    try:
        data = make_request(url)
        if data and len(data) > 2000:
            with open(filepath, 'wb') as f:
                f.write(data)
            return True
    except Exception:
        pass
    return False

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    success = 0
    prefix = "med"

    print("=" * 60)
    print("中药材/饮片图片批量下载（Wikimedia Commons）")
    print(f"共 {len(HERBS)} 种")
    print("=" * 60)

    for i, h in enumerate(HERBS, 1):
        hid = h["id"]
        name = h["name"]
        latin = h["latin"]

        # 对于非植物类（动物/矿物），文件名特殊处理
        if h["id"] >= 107:
            filename = f"{prefix}_76_{h['id']-106:03d}_{name}.jpg"
        else:
            filename = f"{prefix}_{h['id']:03d}_{name}.jpg"

        filepath = IMAGES_DIR / filename

        print(f"\n[{i}/{len(HERBS)}] {name} ({latin})")

        if filepath.exists() and filepath.stat().st_size > 2000:
            print(f"  [skip] 已存在")
            success += 1
            continue

        result = search_wikimedia_medicine(latin, name)
        if result and result.get("img_url"):
            if download_image(result["img_url"], filepath):
                print(f"  [OK] Wikimedia ({result.get('query','')})")
                success += 1
            else:
                print(f"  [FAIL] 下载失败")
        else:
            print(f"  [MISS] 未找到药材图片")

        if i < len(HERBS):
            time.sleep(1.0)

    print(f"\n{'='*60}")
    print(f"完成: {success}/{len(HERBS)} 种药材图片已下载")
    print(f"图片目录: {IMAGES_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
