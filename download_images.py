"""
药食同源中药植物图片批量下载脚本
数据源：PPBC中国植物图像库 (ppbc.iplant.cn) / iPlant植物智 (iplant.cn)
图片保存至 ./images/ 目录，文件名格式：{id}_{name}.jpg
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import re
from pathlib import Path

# 修复Windows GBK编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ======================== 配置 ========================
IMAGES_DIR = Path(__file__).parent / "images"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_DELAY = 1.5  # 请求间隔（秒），礼貌爬取
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ======================== 106种药材数据 ========================
HERBS = [
    {"id":1,"name":"八角茴香","latin":"Illicium verum"},
    {"id":2,"name":"刀豆","latin":"Canavalia gladiata"},
    {"id":3,"name":"小茴香","latin":"Foeniculum vulgare"},
    {"id":4,"name":"山楂","latin":"Crataegus pinnatifida"},
    {"id":5,"name":"乌梅","latin":"Prunus mume"},
    {"id":6,"name":"木瓜","latin":"Chaenomeles speciosa"},
    {"id":7,"name":"火麻仁","latin":"Cannabis sativa"},
    {"id":8,"name":"龙眼肉","latin":"Dimocarpus longan"},
    {"id":9,"name":"决明子","latin":"Cassia obtusifolia"},
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
    {"id":37,"name":"槐米","latin":"Sophora japonica"},
    {"id":38,"name":"榧子","latin":"Torreya grandis"},
    {"id":39,"name":"酸枣仁","latin":"Ziziphus jujuba"},
    {"id":40,"name":"薏苡仁","latin":"Coix lacryma-jobi"},
    {"id":41,"name":"覆盆子","latin":"Rubus chingii"},
    {"id":42,"name":"橘皮","latin":"Citrus reticulata"},
    {"id":43,"name":"丁香","latin":"Syzygium aromaticum"},
    {"id":44,"name":"小蓟","latin":"Cirsium setosum"},
    {"id":45,"name":"马齿苋","latin":"Portulaca oleracea"},
    {"id":46,"name":"代代花","latin":"Citrus aurantium"},
    {"id":47,"name":"白扁豆花","latin":"Lablab purpureus"},
    {"id":48,"name":"鱼腥草","latin":"Houttuynia cordata"},
    {"id":49,"name":"薄荷","latin":"Mentha haplocalyx"},
    {"id":50,"name":"金银花","latin":"Lonicera japonica"},
    {"id":51,"name":"香薷","latin":"Mosla chinensis"},
    {"id":52,"name":"桑叶","latin":"Morus alba"},
    {"id":53,"name":"荷叶","latin":"Nelumbo nucifera"},
    {"id":54,"name":"淡竹叶","latin":"Lophatherum gracile"},
    {"id":55,"name":"菊花","latin":"Chrysanthemum morifolium"},
    {"id":56,"name":"槐花","latin":"Sophora japonica"},
    {"id":57,"name":"蒲公英","latin":"Taraxacum mongolicum"},
    {"id":58,"name":"藿香","latin":"Pogostemon cablin"},
    {"id":59,"name":"紫苏","latin":"Perilla frutescens"},
    {"id":60,"name":"山药","latin":"Dioscorea opposita"},
    {"id":61,"name":"玉竹","latin":"Polygonatum odoratum"},
    {"id":62,"name":"甘草","latin":"Glycyrrhiza uralensis"},
    {"id":63,"name":"白芷","latin":"Angelica dahurica"},
    {"id":64,"name":"百合","latin":"Lilium lancifolium"},
    {"id":65,"name":"肉桂","latin":"Cinnamomum cassia"},
    {"id":66,"name":"姜","latin":"Zingiber officinale"},
    {"id":67,"name":"桔梗","latin":"Platycodon grandiflorum"},
    {"id":68,"name":"高良姜","latin":"Alpinia officinarum"},
    {"id":69,"name":"黄精","latin":"Polygonatum sibiricum"},
    {"id":70,"name":"葛根","latin":"Pueraria lobata"},
    {"id":71,"name":"薤白","latin":"Allium macrostemon"},
    {"id":72,"name":"桔红","latin":"Citrus reticulata"},
    {"id":73,"name":"鲜白茅根","latin":"Imperata cylindrica"},
    {"id":74,"name":"鲜芦根","latin":"Phragmites communis"},
    {"id":75,"name":"昆布","latin":"Laminaria japonica"},
    {"id":76,"name":"茯苓","latin":"Poria cocos"},
    {"id":77,"name":"淡豆豉","latin":"Glycine max"},
    {"id":78,"name":"乌梢蛇","latin":"Ptyas dhumnades"},
    {"id":79,"name":"牡蛎","latin":"Crassostrea gigas"},
    {"id":80,"name":"阿胶","latin":"Equus asinus"},
    {"id":81,"name":"鸡内金","latin":"Gallus gallus"},
    {"id":82,"name":"蜂蜜","latin":"Apis cerana"},
    {"id":83,"name":"蝮蛇","latin":"Agkistrodon acutus"},
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
    {"id":97,"name":"西洋参","latin":"Panax quinquefolium"},
    {"id":98,"name":"黄芪","latin":"Astragalus membranaceus"},
    {"id":99,"name":"灵芝","latin":"Ganoderma lucidum"},
    {"id":100,"name":"山茱萸","latin":"Cornus officinalis"},
    {"id":101,"name":"天麻","latin":"Gastrodia elata"},
    {"id":102,"name":"杜仲叶","latin":"Eucommia ulmoides"},
    {"id":103,"name":"地黄","latin":"Rehmannia glutinosa"},
    {"id":104,"name":"麦冬","latin":"Ophiopogon japonicus"},
    {"id":105,"name":"天冬","latin":"Asparagus cochinchinensis"},
    {"id":106,"name":"化橘红","latin":"Citrus grandis"},
]

# ======================== 图片源 ========================

def make_request(url, retries=3):
    """发送HTTP请求，带重试"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=15) as resp:
                return resp.read()
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2)
    return None

def search_ppbc_species(latin_name):
    """
    在PPBC中搜索物种，返回物种页面URL和第一张图片URL
    PPBC搜索API: http://ppbc.iplant.cn/search19
    """
    # 尝试通过sp页面直接访问（使用拉丁名构造）
    # PPBC物种页面格式: https://ppbc.iplant.cn/sp/{species_id}
    # 但我们不知道species_id，需要搜索

    # 方法1：使用iPlant搜索API
    search_url = f"http://www.iplant.cn/ashx/getspe.ashx?q={urllib.parse.quote(latin_name)}"
    try:
        data = make_request(search_url)
        if data:
            text = data.decode('utf-8', errors='ignore')
            # 尝试解析JSON响应
            try:
                results = json.loads(text)
                if results and len(results) > 0:
                    return results[0]
            except json.JSONDecodeError:
                pass
    except Exception:
        pass

    # 方法2：尝试PPBC sp页面直接访问
    # PPBC的物种ID可以通过搜索获取
    ppbc_search_url = f"http://ppbc.iplant.cn/ashx/getppbcphoto.ashx?appphoto&n=1&name={urllib.parse.quote(latin_name)}"
    try:
        data = make_request(ppbc_search_url)
        if data:
            text = data.decode('utf-8', errors='ignore')
            # 尝试提取图片路径
            match = re.search(r'"data"\s*:\s*"([^"]+)"', text)
            if match:
                img_path = match.group(1)
                return {"img_url": f"http://img1.iplant.cn/imgf/b/{img_path}"}
    except Exception:
        pass

    return None

def search_wikimedia(latin_name):
    """
    从Wikimedia Commons获取图片URL
    使用Special:FilePath可直接获取图片
    """
    # 先搜索Commons获取文件名
    search_url = (
        f"https://commons.wikimedia.org/w/api.php?"
        f"action=query&list=search&srsearch={urllib.parse.quote(latin_name)}"
        f"&srnamespace=6&format=json&srlimit=3"
    )
    try:
        data = make_request(search_url)
        if data:
            result = json.loads(data.decode('utf-8', errors='ignore'))
            pages = result.get("query", {}).get("search", [])
            for page in pages:
                title = page.get("title", "")
                if title.lower().endswith(('.jpg', '.jpeg', '.png')):
                    # 使用Special:FilePath获取实际图片
                    encoded_title = urllib.parse.quote(title.replace("File:", ""))
                    img_url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded_title}?width=400"
                    return {"img_url": img_url, "source": "wikimedia", "title": title}
    except Exception:
        pass
    return None

def search_inaturalist(latin_name):
    """从iNaturalist获取图片URL"""
    search_url = (
        f"https://api.inaturalist.org/v1/taxa/autocomplete?"
        f"q={urllib.parse.quote(latin_name)}&is_active=true"
    )
    try:
        data = make_request(search_url)
        if data:
            result = json.loads(data.decode('utf-8', errors='ignore'))
            results = result.get("results", [])
            if results:
                taxon = results[0]
                taxon_id = taxon.get("id")
                default_photo = taxon.get("default_photo", {})
                if default_photo:
                    img_url = default_photo.get("medium_url") or default_photo.get("square_url")
                    if img_url:
                        return {"img_url": img_url.replace("square", "medium"), "source": "inaturalist", "taxon_id": taxon_id}
    except Exception:
        pass
    return None

def download_image(url, filepath):
    """下载图片到指定路径"""
    try:
        data = make_request(url)
        if data and len(data) > 2000:  # 至少2KB才算有效图片
            with open(filepath, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"    下载失败: {e}")
    return False

# ======================== 主流程 ========================

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    success_count = 0

    print("=" * 60)
    print("药食同源中药植物图片批量下载")
    print(f"目标目录: {IMAGES_DIR}")
    print(f"共 {len(HERBS)} 种药材")
    print("=" * 60)

    for i, herb in enumerate(HERBS, 1):
        herb_id = herb["id"]
        herb_name = herb["name"]
        latin = herb["latin"]
        filename = f"{herb_id:03d}_{herb_name}.jpg"
        filepath = IMAGES_DIR / filename

        print(f"\n[{i}/{len(HERBS)}] {herb_name} ({latin})")

        # 跳过已下载的
        if filepath.exists() and filepath.stat().st_size > 2000:
            print(f"  ✓ 已存在，跳过")
            success_count += 1
            results.append({"id": herb_id, "name": herb_name, "img": f"images/{filename}", "source": "cached"})
            continue

        downloaded = False
        source = None

        # 策略1：iNaturalist (API最稳定)
        print(f"  尝试 iNaturalist...")
        result = search_inaturalist(latin)
        if result and result.get("img_url"):
            if download_image(result["img_url"], filepath):
                print(f"  ✓ iNaturalist 下载成功")
                downloaded = True
                source = "inaturalist"

        # 策略2：Wikimedia Commons
        if not downloaded:
            print(f"  尝试 Wikimedia Commons...")
            result = search_wikimedia(latin)
            if result and result.get("img_url"):
                if download_image(result["img_url"], filepath):
                    print(f"  ✓ Wikimedia 下载成功")
                    downloaded = True
                    source = "wikimedia"

        # 策略3：PPBC
        if not downloaded:
            print(f"  尝试 PPBC...")
            result = search_ppbc_species(latin)
            if result and result.get("img_url"):
                if download_image(result["img_url"], filepath):
                    print(f"  ✓ PPBC 下载成功")
                    downloaded = True
                    source = "ppbc"

        if downloaded:
            success_count += 1
            results.append({"id": herb_id, "name": herb_name, "img": f"images/{filename}", "source": source})
        else:
            print(f"  ✗ 未找到可用图片")
            results.append({"id": herb_id, "name": herb_name, "img": None, "source": None})

        # 礼貌延迟
        if i < len(HERBS):
            time.sleep(REQUEST_DELAY)

    # 保存下载结果
    results_path = IMAGES_DIR.parent / "image_manifest.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"下载完成: {success_count}/{len(HERBS)} 种药材图片已就绪")
    print(f"清单文件: {results_path}")
    print(f"图片目录: {IMAGES_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
