# -*- coding: utf-8 -*-
"""补抓被限流的省份（间隔 2s，重试 3 次）"""
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

PROV_MAP = {
    '520000':'贵州', '530000':'云南', '540000':'西藏', '610000':'陕西',
    '620000':'甘肃', '630000':'青海', '640000':'宁夏', '650000':'新疆',
}
CORE = [
    (77,'大白菜'), (135,'西红柿'), (139,'黄瓜'), (138,'茄子'), (137,'青椒'), (136,'尖椒'),
    (101,'土豆'), (100,'胡萝卜'), (1234,'白萝卜'), (109,'芹菜'), (82,'菠菜'), (79,'油菜'),
    (95,'韭菜'), (150,'豆角'), (119,'蒜薹'), (107,'大蒜'), (106,'生姜'), (140,'西葫芦'),
    (130,'西兰花'), (129,'菜花'), (143,'冬瓜'), (142,'南瓜'),
    (1492,'猪肉(白条猪)'), (923,'牛肉'), (927,'羊肉'), (941,'鸡肉'), (972,'鸡蛋'),
    (1027,'带鱼'), (1001,'活鲫鱼'), (1002,'活鲤鱼'), (1000,'活草鱼'),
    (6,'大米'), (2,'面粉'), (847,'花生油'), (846,'一级豆油(散装)'),
    (165,'苹果'), (209,'香蕉'), (229,'西瓜'), (173,'葡萄'), (166,'梨'), (1378,'橙子'),
    (1244,'香菇'), (1237,'平菇'),
]

def _req(url, method='GET', params=None, retry=3):
    if params:
        url = url + '?' + urllib.parse.urlencode(params)
    last = None
    for i in range(retry + 1):
        try:
            r = urllib.request.Request(url, headers=HEADERS, method=method)
            with urllib.request.urlopen(r, timeout=20, context=CTX) as resp:
                d = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    d = gzip.decompress(d)
                return json.loads(d.decode('utf-8', 'ignore'))
        except Exception as e:
            last = e
            time.sleep(5.0)
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

def chart(pcode, vid):
    j = _req(BASE + '/price_portal/index/getMarketReportPriceChart', method='POST',
             params={'marketIDs': '', 'provinceCodes': pcode, 'varietyID': str(vid)})
    if j.get('code') == 403 or not j.get('data'):
        raise RuntimeError(f"limited/empty code={j.get('code')}")
    d = decrypt(j['data'])
    return json.loads(d) if d else {'x': [], 'y': []}

def main():
    # 读取现有 JSON，只覆盖这 8 省
    path = os.path.join(DATA_DIR, 'province_prices.json')
    with open(path, encoding='utf-8') as f:
        out = json.load(f)
    date = out.get('date')
    t0 = time.time()
    for pcode, pname in PROV_MAP.items():
        prov_data = {}
        for vid, vname in CORE:
            o = None
            for attempt in range(3):
                try:
                    o = chart(pcode, vid)
                    break
                except Exception as e:
                    print(f"  retry {pname}/{vname} #{attempt}: {repr(e)[:60]}", flush=True)
                    time.sleep(9.0)
            if o:
                date = date or o.get('date')
                xs = list(dict.fromkeys(o.get('x', [])))
                ys = [v for v in o.get('y', []) if isinstance(v, (int, float))]
                n = len(xs)
                prov_data[vname] = {'p': round(sum(ys) / len(ys), 2) if ys else None, 'markets': n, 'cat': ''}
            else:
                prov_data[vname] = {'p': None, 'markets': 0, 'cat': ''}
            time.sleep(8.0)
        # 合并 cat（从旧数据带过来）
        old = out['provinces'].get(pname, {})
        for vn, d in prov_data.items():
            if old.get(vn):
                d['cat'] = old[vn].get('cat', '')
        out['provinces'][pname] = prov_data
        n_ok = sum(1 for v in prov_data.values() if v['p'])
        print(f"[{pname}] 完成 有价={n_ok} 耗时={time.time()-t0:.0f}s", flush=True)
        time.sleep(20.0)
    if date:
        out['date'] = date
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("写入完成:", path)

if __name__ == '__main__':
    main()
