# -*- coding: utf-8 -*-
"""
菜篮子-各省基础农产品批发价格抓取 v2
来源：农业农村部全国农产品批发市场价格信息系统 pfsc.agri.cn（日度批发价，元/公斤）
方式：省代码(provinceCodes) x 品种(varietyID) 逐项查询 -> AES-CBC 解密
输出：data/province_prices.json
"""
import urllib.request, urllib.parse, ssl, gzip, json, base64, os, sys, time
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

PROV_MAP = {
    '110000':'北京','120000':'天津','130000':'河北','140000':'山西','150000':'内蒙古',
    '210000':'辽宁','220000':'吉林','230000':'黑龙江','310000':'上海','320000':'江苏',
    '330000':'浙江','340000':'安徽','350000':'福建','360000':'江西','370000':'山东',
    '410000':'河南','420000':'湖北','430000':'湖南','440000':'广东','450000':'广西',
    '460000':'海南','500000':'重庆','510000':'四川','520000':'贵州','530000':'云南',
    '540000':'西藏','610000':'陕西','620000':'甘肃','630000':'青海','640000':'宁夏',
    '650000':'新疆',
}

# 核心品种（id 来自 getVarietiesTree attributelist；猪肉用细分品种白条猪 1492）
CORE = [
    (77,'大白菜','蔬菜'), (135,'西红柿','蔬菜'), (139,'黄瓜','蔬菜'), (138,'茄子','蔬菜'),
    (137,'青椒','蔬菜'), (136,'尖椒','蔬菜'), (101,'土豆','蔬菜'), (100,'胡萝卜','蔬菜'),
    (1234,'白萝卜','蔬菜'), (109,'芹菜','蔬菜'), (82,'菠菜','蔬菜'), (79,'油菜','蔬菜'),
    (95,'韭菜','蔬菜'), (150,'豆角','蔬菜'), (119,'蒜薹','蔬菜'), (107,'大蒜','蔬菜'),
    (106,'生姜','蔬菜'), (140,'西葫芦','蔬菜'), (130,'西兰花','蔬菜'), (129,'菜花','蔬菜'),
    (143,'冬瓜','蔬菜'), (142,'南瓜','蔬菜'),
    (1492,'猪肉(白条猪)','肉蛋'), (923,'牛肉','肉蛋'), (927,'羊肉','肉蛋'),
    (941,'鸡肉','肉蛋'), (972,'鸡蛋','肉蛋'),
    (1027,'带鱼','水产'), (1001,'活鲫鱼','水产'), (1002,'活鲤鱼','水产'), (1000,'活草鱼','水产'),
    (6,'大米','粮油'), (2,'面粉','粮油'), (847,'花生油','粮油'), (846,'一级豆油(散装)','粮油'),
    (165,'苹果','水果'), (209,'香蕉','水果'), (229,'西瓜','水果'), (173,'葡萄','水果'),
    (166,'梨','水果'), (1378,'橙子','水果'), (1244,'香菇','食用菌'), (1237,'平菇','食用菌'),
]

def _req(url, method='GET', params=None, retry=1):
    if params:
        url = url + '?' + urllib.parse.urlencode(params)
    last = None
    for i in range(retry + 1):
        try:
            r = urllib.request.Request(url, headers=HEADERS, method=method)
            with urllib.request.urlopen(r, timeout=15, context=CTX) as resp:
                d = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    d = gzip.decompress(d)
                return json.loads(d.decode('utf-8', 'ignore'))
        except Exception as e:
            last = e
            time.sleep(1.0)
    raise last

def decrypt(s):
    if not s:
        return None
    iv = s[:16].encode('utf-8')
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    raw = cipher.decrypt(base64.b64decode(s[16:]))
    pad = raw[-1]
    if 1 <= pad <= 16:
        raw = raw[:-pad]
    return raw.decode('utf-8', 'ignore')

def chart(province_code, variety_id):
    j = _req(BASE + '/price_portal/index/getMarketReportPriceChart', method='POST',
             params={'marketIDs': '', 'provinceCodes': province_code, 'varietyID': str(variety_id)})
    d = decrypt(j.get('data'))
    return json.loads(d) if d else {'x': [], 'y': []}

def main():
    date = None
    result = {}   # 省 -> {品种 -> {'p': 均值, 'markets': n, 'raw': [prices]}}
    fails = []
    total = len(PROV_MAP) * len(CORE)
    done = 0
    t0 = time.time()
    for pcode, pname in PROV_MAP.items():
        prov_data = {}
        for vid, vname, cat in CORE:
            try:
                o = chart(pcode, vid)
                if o.get('date'):
                    date = date or o['date']
                xs = list(dict.fromkeys(o.get('x', [])))
                ys = [v for v in o.get('y', []) if isinstance(v, (int, float))]
                n = len(xs)
                if ys:
                    avg = round(sum(ys) / len(ys), 2)
                    prov_data[vname] = {'p': avg, 'markets': n, 'cat': cat}
                else:
                    prov_data[vname] = {'p': None, 'markets': n, 'cat': cat}
            except Exception as e:
                prov_data[vname] = {'p': None, 'markets': 0, 'cat': cat}
                fails.append(f"{pname}/{vname}: {repr(e)[:80]}")
            done += 1
            if done % 100 == 0:
                el = time.time() - t0
                print(f"  {done}/{total} {el:.0f}s", flush=True)
        result[pname] = prov_data
        print(f"  [{pname}] 完成, 有价品种={sum(1 for v in prov_data.values() if v['p'])}", flush=True)

    out = {
        'date': date,
        'source': '农业农村部全国农产品批发市场价格信息系统(pfsc.agri.cn)',
        'unit': '元/公斤',
        'note': '各省批发价=该省定点批发市场当日上报价均值(p字段)；markets=该省上报该品种的市场数；未上报为null',
        'provinces': result,
    }
    path = os.path.join(DATA_DIR, 'province_prices.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n写入: {path}")
    print(f"耗时: {time.time()-t0:.0f}s, 失败 {len(fails)} 项")
    if fails:
        print("失败样例:", fails[:10])

if __name__ == '__main__':
    main()
