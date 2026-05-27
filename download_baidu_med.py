"""
百度百科药材形态图片下载脚本
通过curl获取百度百科页面，提取药材/饮片相关图片
保存至 ./images/med_{id:03d}_{name}.jpg（仅对尚未下载药材图片的品种）
"""
import subprocess, re, sys, os, time
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

IMAGES_DIR = Path(__file__).parent / 'images'

HERBS = [
    (1,"八角茴香"),(2,"刀豆"),(3,"小茴香"),(4,"山楂"),(5,"乌梅"),(6,"木瓜"),
    (7,"火麻仁"),(8,"龙眼肉"),(9,"决明子"),(10,"肉豆蔻"),(11,"余甘子"),(12,"佛手"),
    (13,"杏仁"),(14,"沙棘"),(15,"芡实"),(16,"花椒"),(17,"赤小豆"),(18,"麦芽"),
    (19,"枣"),(20,"罗汉果"),(21,"郁李仁"),(22,"青果"),(23,"枳椇子"),(24,"枸杞子"),
    (25,"栀子"),(26,"砂仁"),(27,"胖大海"),(28,"桃仁"),(29,"桑椹"),(30,"益智仁"),
    (31,"莱菔子"),(32,"莲子"),(33,"黄芥子"),(34,"紫苏籽"),(35,"黑芝麻"),(36,"黑胡椒"),
    (37,"槐米"),(38,"榧子"),(39,"酸枣仁"),(40,"薏苡仁"),(41,"覆盆子"),(42,"橘皮"),
    (43,"丁香"),(44,"小蓟"),(45,"马齿苋"),(46,"代代花"),(47,"白扁豆花"),(48,"鱼腥草"),
    (49,"薄荷"),(50,"金银花"),(51,"香薷"),(52,"桑叶"),(53,"荷叶"),(54,"淡竹叶"),
    (55,"菊花"),(56,"槐花"),(57,"蒲公英"),(58,"藿香"),(59,"紫苏"),(60,"山药"),
    (61,"玉竹"),(62,"甘草"),(63,"白芷"),(64,"百合"),(65,"肉桂"),(66,"姜"),
    (67,"桔梗"),(68,"高良姜"),(69,"黄精"),(70,"葛根"),(71,"薤白"),(72,"桔红"),
    (73,"鲜白茅根"),(74,"鲜芦根"),(75,"昆布"),(76,"茯苓"),(77,"淡豆豉"),
    (78,"乌梢蛇"),(79,"牡蛎"),(80,"阿胶"),(81,"鸡内金"),(82,"蜂蜜"),(83,"蝮蛇"),
    (84,"白果"),(85,"白扁豆"),(86,"菊苣"),(87,"香橼"),(88,"当归"),(89,"山柰"),
    (90,"西红花"),(91,"草果"),(92,"姜黄"),(93,"荜茇"),(94,"党参"),(95,"肉苁蓉"),
    (96,"铁皮石斛"),(97,"西洋参"),(98,"黄芪"),(99,"灵芝"),(100,"山茱萸"),
    (101,"天麻"),(102,"杜仲叶"),(103,"地黄"),(104,"麦冬"),(105,"天冬"),(106,"化橘红"),
    # 7.6独有品种
    (107,"白术"),(108,"白芍"),(109,"苍术"),(110,"川芎"),(111,"车前子"),(112,"车前草"),
    (113,"补骨脂"),(114,"刺五加"),(115,"骨碎补"),(116,"厚朴"),(117,"绞股蓝"),
    (118,"红景天"),(119,"木香"),(120,"女贞子"),(121,"五味子"),(122,"泽泻"),
    (123,"知母"),(124,"枳壳"),(125,"茜草"),(126,"诃子"),(127,"胡芦巴"),
    (128,"菟丝子"),(129,"远志"),(130,"益母草"),(131,"夏枯草"),(132,"香附"),
    (133,"辛夷"),(134,"积雪草"),
]

UA = "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

def fetch_page(name):
    """通过curl获取百度百科页面HTML"""
    url = f"https://baike.baidu.com/item/{name}"
    try:
        result = subprocess.run(
            ["curl", "-sL", "--compressed", "-H", f"User-Agent: {UA}", "-H", "Accept: text/html",
             "--max-time", "20", url],
            capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=25
        )
        if result.returncode == 0 and len(result.stdout) > 5000:
            return result.stdout
    except Exception:
        pass
    return None

def extract_med_image(html, name):
    """从百度百科HTML中提取药材/饮片图片URL"""
    candidates = []

    # 策略1: 找包含"饮片""药材""中药"相关alt/title的图片
    pattern1 = r'<img[^>]*?(?:alt|title)=[\"\\\']([^\"\\\']*(?:饮片|药材|中药|干燥|炮制|饮|片|草药)[^\"\\\']*)[\"\\\'][^>]*?(?:src|data-src)=[\"\\\']([^\"\\\']+\.(?:jpg|jpeg|png))[\"\\\']'
    for m in re.finditer(pattern1, html, re.IGNORECASE):
        candidates.append(m.group(2))

    # 策略2: 找摘要图片（通常是药材实物照片）
    pattern2 = r'class=[\"\\\']summary-pic[\"\\\'][^>]*?src=[\"\\\']([^\"\\\']+\.(?:jpg|jpeg|png))[\"\\\']'
    for m in re.finditer(pattern2, html, re.IGNORECASE):
        candidates.append(m.group(1))

    # 策略3: 找所有百度域名的图片，取前几个
    pattern3 = r'(?:src|data-src)=[\"\\\'](https?://[^\"\\\'\s]+\.baidu\.com[^\"\\\'\s]*\.(?:jpg|jpeg|png))[\"\\\']'
    all_baidu = list(set(re.findall(pattern3, html, re.IGNORECASE)))
    candidates.extend(all_baidu[:3])

    # 优先返回非icon/logo的图片
    good = [u for u in candidates if 'icon' not in u.lower() and 'logo' not in u.lower() and len(u) > 20]
    if good:
        return good[0]
    return None

def download(url, filepath):
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", str(filepath), "-H", f"User-Agent: {UA}",
             "--max-time", "30", url],
            capture_output=True, timeout=35
        )
        if result.returncode == 0 and filepath.exists() and filepath.stat().st_size > 1000:
            return True
    except Exception:
        pass
    return False

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    new_count = 0; skip_count = 0; fail_count = 0
    print("=" * 60)
    print(f"百度百科药材图片下载 ({len(HERBS)} 种)")
    print("=" * 60)

    for i, (hid, name) in enumerate(HERBS, 1):
        if hid >= 107:
            filename = f"med_76_{hid-106:03d}_{name}.jpg"
        else:
            filename = f"med_{hid:03d}_{name}.jpg"
        filepath = IMAGES_DIR / filename

        if filepath.exists() and filepath.stat().st_size > 1000:
            skip_count += 1
            if skip_count % 20 == 0:
                print(f"[{i:3d}/{len(HERBS)}] ... {skip_count} skipped, {new_count} new")
            continue

        print(f"[{i:3d}/{len(HERBS)}] {name}: ", end='', flush=True)
        html = fetch_page(name)
        if not html:
            print("page fetch failed")
            fail_count += 1
            continue

        img_url = extract_med_image(html, name)
        if not img_url:
            print("no med image found")
            fail_count += 1
            continue

        if download(img_url, filepath):
            size_kb = filepath.stat().st_size // 1024
            print(f"OK ({size_kb}KB)")
            new_count += 1
        else:
            print("download failed")
            fail_count += 1

        time.sleep(1.5)

    print(f"\n{'='*60}")
    print(f"Done: {new_count} new, {skip_count} skipped, {fail_count} failed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
