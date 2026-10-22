# -*- coding: utf-8 -*-
"""
菜篮子-各省基础农产品批发价格抓取
来源：农业农村部全国农产品批发市场价格信息系统 pfsc.agri.cn（日度批发价，元/公斤）
- 品种表：GET /price_portal/sys-user-relation/getVarietiesTree（attributelist: id/varietyName/varietyTypeName）
- 市场表：POST /api/priceQuotationController/getMarketByProvinceCode（302市场，marketName→provinceName）
- 价格：POST /price_portal/index/getMarketReportPriceChart?varietyID=&provinceCodes=（AES-CBC 解密）
输出：data/province_prices.json + 覆盖统计
"""
import urllib.request, urllib.parse, ssl, gzip, json, base64, os, sys, collections
from Crypto.Cipher import AES

BASE = 'https://pfsc.agri.cn'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36',
           'Accept': 'application/json, text/plain, */*', 'Accept-Encoding': 'gzip',
           'Origin': BASE, 'Referer': BASE + '/', 'Content-Type': 'application/json'}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
KEY = b'7s9K$pG2xQ8zR5mB7vA3sD9fH2jW40cV'
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 省级行政区划代码 -> 名称
PROV_MAP = {
    '110000':'北京','120000':'天津','130000':'河北','140000':'山西','150000':'内蒙古',
    '210000':'辽宁','220000':'吉林','230000':'黑龙江','310000':'上海','320000':'江苏',
    '330000':'浙江','340000':'安徽','350000':'福建','360000':'江西','370000':'山东',
    '410000':'河南','420000':'湖北','430000':'湖南','440000':'广东','450000':'广西',
    '460000':'海南','500000':'重庆','510000':'四川','520000':'贵州','530000':'云南',
    '540000':'西藏','610000':'陕西','620000':'甘肃','630000':'青海','640000':'宁夏',
    '650000':'新疆',
}

def _req(url, method='GET', params=None):
    if params:
        url = url + '?' + urllib.parse.urlencode(params)
    r = urllib.request.Request(url, headers=HEADERS, method=method)
    with urllib.request.urlopen(r, timeout=40, context=CTX) as resp:
        d = resp.read()
        if resp.headers.get('Content-Encoding') == 'gzip':
            d = gzip.decompress(d)
        return json.loads(d.decode('utf-8', 'ignore'))

def decrypt(data_b64):
    s = data_b64
    iv = s[:16].encode('utf-8')
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    raw = cipher.decrypt(base64.b64decode(s[16:]))
    pad = raw[-1]
    if 1 <= pad <= 16:
        raw = raw[:-pad]
    return raw.decode('utf-8', 'ignore')

def get_varieties():
    tree = _req(BASE + '/price_portal/sys-user-relation/getVarietiesTree')
    root = tree['content'][0]['content']
    out = []
    def walk(nodes):
        for n in nodes:
            for a in (n.get('attributelist') or []):
                if a.get('varietyName'):
                    out.append({'id': a.get('id'), 'code': a.get('varietyCode'),
                                'name': a.get('varietyName'), 'cat': a.get('varietyTypeName'),
                                'unit': a.get('meteringUnit')})
            if n.get('children'):
                walk(n['children'])
    walk(root['children'])
    # 去重（按名称）
    seen, uniq = set(), []
    for v in out:
        if v['name'] not in seen:
            seen.add(v['name']); uniq.append(v)
    return uniq

def get_markets():
    j = _req(BASE + '/api/priceQuotationController/getMarketByProvinceCode', method='POST', params={'provinceCode': ''})
    ms = []
    for m in j.get('content', []):
        pc = m.get('province')
        ms.append({'code': m.get('marketCode'), 'name': m.get('marketName'),
                   'prov': PROV_MAP.get(pc) or m.get('provinceName'),
                   'provCode': pc,
                   'area': m.get('areaName')})
    return ms

def get_price(variety_id, province_codes=''):
    j = _req(BASE + '/price_portal/index/getMarketReportPriceChart', method='POST',
             params={'marketIDs': '', 'provinceCodes': province_codes, 'varietyID': str(variety_id)})
    obj = json.loads(decrypt(j['data']))
    rows = []
    for name, price in zip(obj['x'], obj['y']):
        rows.append({'market': name, 'price': price})
    return obj.get('date'), rows

def main():
    print("1) 抓品种表...")
    varieties = get_varieties()
    print(f"   品种总数: {len(varieties)}")
    # 核心品种匹配（优先常见菜篮子品种）
    CORE = ['大白菜','西红柿','黄瓜','茄子','青椒','尖椒','土豆','洋葱','胡萝卜','白萝卜','芹菜','菠菜','油菜','韭菜','豆角','蒜薹','大蒜','生姜','西葫芦','西兰花','菜花','冬瓜','南瓜','猪肉','牛肉','羊肉','鸡肉','鸡蛋','带鱼','鲫鱼','鲤鱼','草鱼','大米','面粉','食用油','花生油','豆油','苹果','香蕉','西瓜','葡萄','梨','橙子','桔子','香菇','平菇']
    by_name = {}
    for v in varieties:
        by_name.setdefault(v['name'], []).append(v)
    chosen = []
    for c in CORE:
        hits = by_name.get(c) or [x[0] for k, x in by_name.items() if c in k]
        if hits:
            chosen.append(hits[0])
    print(f"   核心品种命中: {len(chosen)}")
    for v in chosen:
        print(f"     {v['id']} {v['name']} ({v['cat']})")

    print("2) 抓市场表...")
    markets = get_markets()
    name2prov = {}
    for m in markets:
        if m['name'] and not name2prov.get(m['name']):
            name2prov[m['name']] = m
    print(f"   市场总数: {len(markets)}, 名称唯一: {len(name2prov)}")

    print("3) 抓核心品种价格(全国)...")
    date = None
    prov_prices = {}   # prov -> {variety -> [prices]}
    market_prov = {}   # market -> prov
    for v in chosen:
        d, rows = get_price(v['id'])
        date = date or d
        for r in rows:
            prov = name2prov.get(r['market'])
            pv = prov['prov'] if prov else None
            if not pv:
                continue
            market_prov.setdefault(r['market'], pv)
            prov_prices.setdefault(pv, {}).setdefault(v['name'], []).append(r['price'])
        print(f"   {v['name']}: {len(rows)} 市场")
        sys.stdout.flush()

    # 聚合：省×品种均值（两位小数）
    prov_agg = {}
    prov_markets = {}
    for pv, vv in prov_prices.items():
        prov_agg[pv] = {}
        prov_markets[pv] = len(vv.get(next(iter(vv), ''), [])) if vv else 0
        for vname, prices in vv.items():
            if prices:
                avg = sum(prices) / len(prices)
                prov_agg[pv][vname] = round(avg, 2)
    # 覆盖统计
    total = {v['name']: 0 for v in chosen}
    for pv, vv in prov_agg.items():
        for vname in vv:
            total[vname] += 1
    print("\n=== 覆盖统计 ===")
    for vname, cnt in sorted(total.items(), key=lambda x: -x[1]):
        print(f"  {vname}: {cnt} 省")

    out = {
        'date': date,
        'source': '农业农村部全国农产品批发市场价格信息系统(pfsc.agri.cn)',
        'unit': '元/公斤',
        'note': '各省批发价=该省各定点批发市场当日上报价均值；未上报省份留空',
        'provinces': prov_agg,
        'markets_per_prov': prov_markets,
    }
    path = os.path.join(DATA_DIR, 'province_prices.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n已写入 {path}")

if __name__ == '__main__':
    main()
