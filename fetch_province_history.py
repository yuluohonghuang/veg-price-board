# -*- coding: utf-8 -*-
"""每日省级快照 + 历史序列累积（方案B：每日快照攒点，页面按周采样画曲线）
输入：pfsc.agri.cn 当日各市场上报价（截面）
输出1：data/province_prices.json —— 当日快照（31省 x 43品种 {p, markets, cat}）
输出2：data/province_history.json —— 历史序列 {省: {品种: {dates:[...升序], prices:[...]}}}，同日去重
"""
import urllib.request, urllib.parse, ssl, gzip, json, base64, os, sys, time, datetime
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
    '110000': '北京', '120000': '天津', '130000': '河北', '140000': '山西', '150000': '内蒙古',
    '210000': '辽宁', '220000': '吉林', '230000': '黑龙江', '310000': '上海', '320000': '江苏',
    '330000': '浙江', '340000': '安徽', '350000': '福建', '360000': '江西', '370000': '山东',
    '410000': '河南', '420000': '湖北', '430000': '湖南', '440000': '广东', '450000': '广西',
    '460000': '海南', '500000': '重庆', '510000': '四川', '520000': '贵州', '530000': '云南',
    '540000': '西藏', '610000': '陕西', '620000': '甘肃', '630000': '青海', '640000': '宁夏', '650000': '新疆',
}
CORE = [
    (77, '大白菜'), (135, '西红柿'), (139, '黄瓜'), (138, '茄子'), (137, '青椒'), (136, '尖椒'),
    (101, '土豆'), (100, '胡萝卜'), (1234, '白萝卜'), (109, '芹菜'), (82, '菠菜'), (79, '油菜'),
    (95, '韭菜'), (150, '豆角'), (119, '蒜薹'), (107, '大蒜'), (106, '生姜'), (140, '西葫芦'),
    (130, '西兰花'), (129, '菜花'), (143, '冬瓜'), (142, '南瓜'),
    (1492, '猪肉(白条猪)'), (923, '牛肉'), (927, '羊肉'), (941, '鸡肉'), (972, '鸡蛋'),
    (1027, '带鱼'), (1001, '活鲫鱼'), (1002, '活鲤鱼'), (1000, '活草鱼'),
    (6, '大米'), (2, '面粉'), (847, '花生油'), (846, '一级豆油(散装)'),
    (165, '苹果'), (209, '香蕉'), (229, '西瓜'), (173, '葡萄'), (166, '梨'), (1378, '橙子'),
    (1244, '香菇'), (1237, '平菇'),
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
    return json.loads(d) if d else {'date': None, 'x': [], 'y': []}

def main():
    today = datetime.date.today().isoformat()
    snap_path = os.path.join(DATA_DIR, 'province_prices.json')
    hist_path = os.path.join(DATA_DIR, 'province_history.json')
    # 空窗快速探测：浙江/大白菜对照，接口无数据则退出（避免凌晨数据更新窗口空跑）
    try:
        probe = chart('330000', 77)
        if not probe.get('y'):
            print("EMPTY_WINDOW: pfsc 接口当前无数据（含浙江对照），跳过本轮快照与累积")
            sys.exit(0)
    except Exception as e:
        print(f"PROBE_FAIL {repr(e)[:60]}，仍尝试全量")
    out = json.load(open(snap_path, encoding='utf-8')) if os.path.exists(snap_path) else {'date': today, 'provinces': {}}
    hist = json.load(open(hist_path, encoding='utf-8')) if os.path.exists(hist_path) else {}
    t0 = time.time()
    for pcode, pname in PROV_MAP.items():
        prov_data = out['provinces'].get(pname, {})
        hist_prov = hist.setdefault(pname, {})
        fail_streak = 0
        for vid, vname in CORE:
            o = None
            for attempt in range(3):
                try:
                    o = chart(pcode, vid)
                    break
                except Exception as e:
                    print(f"  retry {pname}/{vname} #{attempt}: {repr(e)[:50]}", flush=True)
                    time.sleep(8.0)
            if o:
                xs = list(dict.fromkeys(o.get('x', [])))
                ys = [v for v in o.get('y', []) if isinstance(v, (int, float))]
                n = len(xs)
                avg = round(sum(ys) / len(ys), 2) if ys else None
                old = prov_data.get(vname, {})
                prov_data[vname] = {'p': avg, 'markets': n, 'cat': old.get('cat', '')}
                if avg is not None:
                    h = hist_prov.setdefault(vname, {'dates': [], 'prices': []})
                    if today in h['dates']:
                        h['prices'][h['dates'].index(today)] = avg
                    else:
                        h['dates'].append(today)
                        h['prices'].append(avg)
            else:
                prov_data.setdefault(vname, {'p': None, 'markets': 0, 'cat': ''})
                fail_streak += 1
                if fail_streak >= 3:
                    print(f"[{pname}] 连续3品种失败（限流/空数据），本次跳过该省，下次任务再试", flush=True)
                    break
            if o is not None:
                fail_streak = 0
            time.sleep(2.5)
        out['provinces'][pname] = prov_data
        n_ok = sum(1 for v in prov_data.values() if v['p'])
        print(f"[{pname}] 有价={n_ok} 耗时={time.time()-t0:.0f}s", flush=True)
        # 每省完成后立即写盘（断点保护：中途中断不丢已抓省份）
        out['date'] = today
        with open(snap_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        hist['_meta'] = {'updated': today, 'note': '每日快照累积，日期升序；同日去重'}
        with open(hist_path, 'w', encoding='utf-8') as f:
            json.dump(hist, f, ensure_ascii=False, indent=1)
        time.sleep(5.0)
    out['date'] = today
    with open(snap_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    hist['_meta'] = {'updated': today, 'note': '每日快照累积，日期升序；同日去重'}
    with open(hist_path, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)
    n_series = 0
    for pname, pv in hist.items():
        if pname == '_meta' or not isinstance(pv, dict):
            continue
        for it in pv.values():
            if isinstance(it, dict) and len(it.get('prices', [])) >= 2:
                n_series += 1
    print("快照:", snap_path)
    print("历史:", hist_path, "有>=2点的省-品种数:", n_series)

if __name__ == '__main__':
    main()
