"""
中药材形态图片下载脚本（优化版）
来源：Wikimedia Commons API，使用拉丁名+英文关键词搜索
保存至 ./images/med_{id:03d}_{name}.jpg
支持VPN网络环境
"""
import os, sys, time, json, urllib.request, urllib.parse, ssl
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGES_DIR = Path(__file__).parent / 'images'
UA = 'Mozilla/5.0 (compatible; HerbImageBot/1.0)'
CTX = ssl.create_default_context()
CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

HERBS = [
    {"id":1,"name":"八角茴香","latin":"Illicium verum","en":"star anise"},
    {"id":2,"name":"刀豆","latin":"Canavalia gladiata","en":"sword bean"},
    {"id":3,"name":"小茴香","latin":"Foeniculum vulgare","en":"fennel seed"},
    {"id":4,"name":"山楂","latin":"Crataegus pinnatifida","en":"hawthorn fruit"},
    {"id":5,"name":"乌梅","latin":"Prunus mume","en":"smoked plum"},
    {"id":6,"name":"木瓜","latin":"Chaenomeles speciosa","en":"quince fruit"},
    {"id":7,"name":"火麻仁","latin":"Cannabis sativa","en":"hemp seed"},
    {"id":8,"name":"龙眼肉","latin":"Dimocarpus longan","en":"longan fruit"},
    {"id":9,"name":"决明子","latin":"Senna obtusifolia","en":"cassia seed"},
    {"id":10,"name":"肉豆蔻","latin":"Myristica fragrans","en":"nutmeg"},
    {"id":11,"name":"余甘子","latin":"Phyllanthus emblica","en":"amla fruit"},
    {"id":12,"name":"佛手","latin":"Citrus medica","en":"buddha hand fruit"},
    {"id":13,"name":"杏仁","latin":"Prunus armeniaca","en":"apricot kernel"},
    {"id":14,"name":"沙棘","latin":"Hippophae rhamnoides","en":"sea buckthorn"},
    {"id":15,"name":"芡实","latin":"Euryale ferox","en":"fox nut"},
    {"id":16,"name":"花椒","latin":"Zanthoxylum bungeanum","en":"sichuan pepper"},
    {"id":17,"name":"赤小豆","latin":"Vigna umbellata","en":"adzuki bean"},
    {"id":18,"name":"麦芽","latin":"Hordeum vulgare","en":"malt"},
    {"id":19,"name":"枣","latin":"Ziziphus jujuba","en":"jujube fruit"},
    {"id":20,"name":"罗汉果","latin":"Siraitia grosvenorii","en":"monk fruit"},
    {"id":21,"name":"郁李仁","latin":"Prunus humilis","en":"bush cherry kernel"},
    {"id":22,"name":"青果","latin":"Canarium album","en":"chinese olive"},
    {"id":23,"name":"枳椇子","latin":"Hovenia dulcis","en":"raisin tree fruit"},
    {"id":24,"name":"枸杞子","latin":"Lycium barbarum","en":"goji berry dried fruit"},
    {"id":25,"name":"栀子","latin":"Gardenia jasminoides","en":"gardenia fruit"},
    {"id":26,"name":"砂仁","latin":"Amomum villosum","en":"cardamom fruit"},
    {"id":27,"name":"胖大海","latin":"Sterculia lychnophora","en":"malva nut"},
    {"id":28,"name":"桃仁","latin":"Prunus persica","en":"peach kernel"},
    {"id":29,"name":"桑椹","latin":"Morus alba","en":"mulberry fruit"},
    {"id":30,"name":"益智仁","latin":"Alpinia oxyphylla","en":"black cardamom"},
    {"id":31,"name":"莱菔子","latin":"Raphanus sativus","en":"radish seed"},
    {"id":32,"name":"莲子","latin":"Nelumbo nucifera","en":"lotus seed dried"},
    {"id":33,"name":"黄芥子","latin":"Brassica juncea","en":"mustard seed"},
    {"id":34,"name":"紫苏籽","latin":"Perilla frutescens","en":"perilla seed"},
    {"id":35,"name":"黑芝麻","latin":"Sesamum indicum","en":"black sesame seed"},
    {"id":36,"name":"黑胡椒","latin":"Piper nigrum","en":"black pepper dried"},
    {"id":37,"name":"槐米","latin":"Styphnolobium japonicum","en":"pagoda tree bud"},
    {"id":38,"name":"榧子","latin":"Torreya grandis","en":"torreya nut"},
    {"id":39,"name":"酸枣仁","latin":"Ziziphus jujuba","en":"sour jujube seed"},
    {"id":40,"name":"薏苡仁","latin":"Coix lacryma-jobi","en":"jobs tears seed"},
    {"id":41,"name":"覆盆子","latin":"Rubus chingii","en":"raspberry fruit dried"},
    {"id":42,"name":"橘皮","latin":"Citrus reticulata","en":"tangerine peel dried"},
    {"id":43,"name":"丁香","latin":"Syzygium aromaticum","en":"clove dried"},
    {"id":44,"name":"小蓟","latin":"Cirsium arvense","en":"field thistle"},
    {"id":45,"name":"马齿苋","latin":"Portulaca oleracea","en":"purslane dried"},
    {"id":46,"name":"代代花","latin":"Citrus aurantium","en":"bitter orange flower"},
    {"id":47,"name":"白扁豆花","latin":"Lablab purpureus","en":"hyacinth bean flower"},
    {"id":48,"name":"鱼腥草","latin":"Houttuynia cordata","en":"houttuynia dried"},
    {"id":49,"name":"薄荷","latin":"Mentha canadensis","en":"mint dried leaf"},
    {"id":50,"name":"金银花","latin":"Lonicera japonica","en":"honeysuckle dried flower"},
    {"id":51,"name":"香薷","latin":"Mosla chinensis","en":"mosla herb"},
    {"id":52,"name":"桑叶","latin":"Morus alba","en":"mulberry leaf dried"},
    {"id":53,"name":"荷叶","latin":"Nelumbo nucifera","en":"lotus leaf dried"},
    {"id":54,"name":"淡竹叶","latin":"Lophatherum gracile","en":"lophatherum herb"},
    {"id":55,"name":"菊花","latin":"Chrysanthemum morifolium","en":"chrysanthemum dried flower"},
    {"id":56,"name":"槐花","latin":"Styphnolobium japonicum","en":"pagoda flower"},
    {"id":57,"name":"蒲公英","latin":"Taraxacum mongolicum","en":"dandelion dried root"},
    {"id":58,"name":"藿香","latin":"Pogostemon cablin","en":"patchouli dried"},
    {"id":59,"name":"紫苏","latin":"Perilla frutescens","en":"perilla leaf dried"},
    {"id":60,"name":"山药","latin":"Dioscorea polystachya","en":"chinese yam dried slice"},
    {"id":61,"name":"玉竹","latin":"Polygonatum odoratum","en":"solomon seal rhizome"},
    {"id":62,"name":"甘草","latin":"Glycyrrhiza uralensis","en":"licorice root dried slice"},
    {"id":63,"name":"白芷","latin":"Angelica dahurica","en":"angelica root dried"},
    {"id":64,"name":"百合","latin":"Lilium lancifolium","en":"lily bulb dried"},
    {"id":65,"name":"肉桂","latin":"Cinnamomum cassia","en":"cinnamon bark dried"},
    {"id":66,"name":"姜","latin":"Zingiber officinale","en":"ginger dried rhizome"},
    {"id":67,"name":"桔梗","latin":"Platycodon grandiflorus","en":"balloon flower root dried"},
    {"id":68,"name":"高良姜","latin":"Alpinia officinarum","en":"galangal dried rhizome"},
    {"id":69,"name":"黄精","latin":"Polygonatum sibiricum","en":"solomon seal dried"},
    {"id":70,"name":"葛根","latin":"Pueraria montana","en":"kudzu root dried slice"},
    {"id":71,"name":"薤白","latin":"Allium macrostemon","en":"chinese onion bulb"},
    {"id":72,"name":"桔红","latin":"Citrus reticulata","en":"tangerine red peel"},
    {"id":73,"name":"鲜白茅根","latin":"Imperata cylindrica","en":"cogon grass rhizome"},
    {"id":74,"name":"鲜芦根","latin":"Phragmites australis","en":"reed rhizome dried"},
    {"id":75,"name":"昆布","latin":"Saccharina japonica","en":"kelp dried"},
    {"id":76,"name":"茯苓","latin":"Wolfiporia extensa","en":"poria dried sclerotium"},
    {"id":77,"name":"淡豆豉","latin":"Glycine max","en":"fermented soybean"},
    {"id":78,"name":"乌梢蛇","latin":"Ptyas dhumnades","en":"rat snake dried"},
    {"id":79,"name":"牡蛎","latin":"Crassostrea gigas","en":"oyster shell dried"},
    {"id":80,"name":"阿胶","latin":"Equus asinus","en":"donkey hide gelatin"},
    {"id":81,"name":"鸡内金","latin":"Gallus gallus","en":"chicken gizzard lining"},
    {"id":82,"name":"蜂蜜","latin":"Apis cerana","en":"honey"},
    {"id":83,"name":"蝮蛇","latin":"Deinagkistrodon acutus","en":"pit viper dried"},
    {"id":84,"name":"白果","latin":"Ginkgo biloba","en":"ginkgo nut dried"},
    {"id":85,"name":"白扁豆","latin":"Lablab purpureus","en":"hyacinth bean dried"},
    {"id":86,"name":"菊苣","latin":"Cichorium intybus","en":"chicory root dried"},
    {"id":87,"name":"香橼","latin":"Citrus medica","en":"citron fruit dried"},
    {"id":88,"name":"当归","latin":"Angelica sinensis","en":"dong quai root dried slice"},
    {"id":89,"name":"山柰","latin":"Kaempferia galanga","en":"galangal lesser dried"},
    {"id":90,"name":"西红花","latin":"Crocus sativus","en":"saffron dried stigma"},
    {"id":91,"name":"草果","latin":"Amomum tsao-ko","en":"black cardamom dried"},
    {"id":92,"name":"姜黄","latin":"Curcuma longa","en":"turmeric dried rhizome"},
    {"id":93,"name":"荜茇","latin":"Piper longum","en":"long pepper dried"},
    {"id":94,"name":"党参","latin":"Codonopsis pilosula","en":"codonopsis root dried"},
    {"id":95,"name":"肉苁蓉","latin":"Cistanche deserticola","en":"cistanche dried"},
    {"id":96,"name":"铁皮石斛","latin":"Dendrobium officinale","en":"dendrobium dried"},
    {"id":97,"name":"西洋参","latin":"Panax quinquefolius","en":"american ginseng root dried"},
    {"id":98,"name":"黄芪","latin":"Astragalus mongholicus","en":"astragalus root dried slice"},
    {"id":99,"name":"灵芝","latin":"Ganoderma lucidum","en":"reishi mushroom dried"},
    {"id":100,"name":"山茱萸","latin":"Cornus officinalis","en":"cornelian cherry dried"},
    {"id":101,"name":"天麻","latin":"Gastrodia elata","en":"gastrodia dried rhizome"},
    {"id":102,"name":"杜仲叶","latin":"Eucommia ulmoides","en":"eucommia leaf dried"},
    {"id":103,"name":"地黄","latin":"Rehmannia glutinosa","en":"rehmannia root dried"},
    {"id":104,"name":"麦冬","latin":"Ophiopogon japonicus","en":"ophiopogon root dried"},
    {"id":105,"name":"天冬","latin":"Asparagus cochinchinensis","en":"asparagus root dried"},
    {"id":106,"name":"化橘红","latin":"Citrus grandis","en":"pomelo peel dried"},
    # 28 种 7.6独有
    {"id":107,"name":"白术","latin":"Atractylodes macrocephala","en":"atractylodes dried rhizome"},
    {"id":108,"name":"白芍","latin":"Paeonia lactiflora","en":"white peony root dried slice"},
    {"id":109,"name":"苍术","latin":"Atractylodes lancea","en":"atractylodes dried"},
    {"id":110,"name":"川芎","latin":"Ligusticum striatum","en":"chuanxiong dried rhizome"},
    {"id":111,"name":"车前子","latin":"Plantago asiatica","en":"plantain seed dried"},
    {"id":112,"name":"车前草","latin":"Plantago asiatica","en":"plantain herb dried"},
    {"id":113,"name":"补骨脂","latin":"Psoralea corylifolia","en":"psoralea fruit dried"},
    {"id":114,"name":"刺五加","latin":"Eleutherococcus senticosus","en":"siberian ginseng root dried"},
    {"id":115,"name":"骨碎补","latin":"Drynaria fortunei","en":"drynaria rhizome dried"},
    {"id":116,"name":"厚朴","latin":"Magnolia officinalis","en":"magnolia bark dried"},
    {"id":117,"name":"绞股蓝","latin":"Gynostemma pentaphyllum","en":"jiaogulan dried leaf"},
    {"id":118,"name":"红景天","latin":"Rhodiola rosea","en":"rhodiola root dried"},
    {"id":119,"name":"木香","latin":"Dolomiaea costus","en":"costus root dried"},
    {"id":120,"name":"女贞子","latin":"Ligustrum lucidum","en":"privet fruit dried"},
    {"id":121,"name":"五味子","latin":"Schisandra chinensis","en":"schisandra fruit dried"},
    {"id":122,"name":"泽泻","latin":"Alisma plantago-aquatica","en":"alisma dried rhizome"},
    {"id":123,"name":"知母","latin":"Anemarrhena asphodeloides","en":"anemarrhena dried rhizome"},
    {"id":124,"name":"枳壳","latin":"Citrus aurantium","en":"bitter orange dried"},
    {"id":125,"name":"茜草","latin":"Rubia cordifolia","en":"madder root dried"},
    {"id":126,"name":"诃子","latin":"Terminalia chebula","en":"chebulic myrobalan dried"},
    {"id":127,"name":"胡芦巴","latin":"Trigonella foenum-graecum","en":"fenugreek seed dried"},
    {"id":128,"name":"菟丝子","latin":"Cuscuta chinensis","en":"dodder seed dried"},
    {"id":129,"name":"远志","latin":"Polygala tenuifolia","en":"polygala root dried"},
    {"id":130,"name":"益母草","latin":"Leonurus japonicus","en":"motherwort dried"},
    {"id":131,"name":"夏枯草","latin":"Prunella vulgaris","en":"self-heal dried"},
    {"id":132,"name":"香附","latin":"Cyperus rotundus","en":"nutgrass dried rhizome"},
    {"id":133,"name":"辛夷","latin":"Magnolia biondii","en":"magnolia flower bud dried"},
    {"id":134,"name":"积雪草","latin":"Centella asiatica","en":"gotu kola dried"},
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

def search_wikimedia(latin, en_name, name):
    """多策略搜索Wikimedia Commons药材图片"""
    queries = []
    if en_name:
        queries.append(en_name)
    if latin:
        queries.append(f"{latin} dried")
        queries.append(f"{latin} root")

    for query in queries:
        url = (f"https://commons.wikimedia.org/w/api.php?action=query"
               f"&list=search&srsearch={urllib.parse.quote(query)}"
               f"&srnamespace=6&format=json&srlimit=8")
        try:
            data = req(url)
            result = json.loads(data.decode())
            pages = result.get("query", {}).get("search", [])
            for page in pages:
                title = page.get("title", "")
                if title.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    encoded = urllib.parse.quote(title.replace("File:", ""))
                    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=500"
        except Exception:
            continue
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
    success = 0
    print("=" * 60)
    print(f"中药材形态图片下载 (Wikimedia Commons, {len(HERBS)} 种)")
    print("=" * 60)

    for i, h in enumerate(HERBS, 1):
        hid = h["id"]
        name = h["name"]
        latin = h.get("latin","")
        en = h.get("en","")

        if hid >= 107:
            filename = f"med_76_{hid-106:03d}_{name}.jpg"
        else:
            filename = f"med_{hid:03d}_{name}.jpg"
        filepath = IMAGES_DIR / filename

        if filepath.exists() and filepath.stat().st_size > 2000:
            success += 1
            continue

        url = search_wikimedia(latin, en, name)
        if url:
            if download(url, filepath):
                success += 1
                print(f"[{i:3d}/{len(HERBS)}] {name}: OK")
            else:
                print(f"[{i:3d}/{len(HERBS)}] {name}: download failed")
        else:
            print(f"[{i:3d}/{len(HERBS)}] {name}: no image found")

        if i < len(HERBS):
            time.sleep(0.8)

    print(f"\n{'='*60}")
    print(f"Done: {success}/{len(HERBS)} downloaded")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
