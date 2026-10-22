# -*- coding: utf-8 -*-
"""商务部商务预报 36 城食用农产品零售价（周度，方案1：零售主源）

输入1：POST cif.mofcom.gov.cn/cif/moreReport.fhtml（nodeId=10163 分页 JSON 列表）
输入2：详情页 HTML 表格（品种/零售价/环比/同比，元/公斤、升）
输出：data/cif_retail.json —— {日期: {dateLabel, pubDate, items:{品种:{v,w,y}}}} 周度追加，按周去重

说明：本机直连 cif.mofcom.gov.cn 可能被网络层拦截（SSL 握手失败），
此脚本设计为在 GitHub Actions 上运行；本地验证用 data/cif_sample.html。
"""
import urllib.request, urllib.parse, ssl, gzip, json, os, re, sys, time, html as htmlmod

BASE = 'https://cif.mofcom.gov.cn'
NODE_ID = '10163'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36'
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data')
OUT = os.path.join(DATA_DIR, 'cif_retail.json')
SAMPLE = os.path.join(DATA_DIR, 'cif_sample.html')


def _open(req, retry=3):
    last = None
    for i in range(retry + 1):
        try:
            with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
                d = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    d = gzip.decompress(d)
                return d
        except Exception as e:
            last = e
            time.sleep(5.0)
    raise last


def fetch_list():
    """moreReport.fhtml 分页 JSON -> 最新一条 36 城零售价格条目"""
    body = urllib.parse.urlencode({'nodeId': NODE_ID, 'pageNo': '1', 'pageSize': '6'}).encode()
    req = urllib.request.Request(BASE + '/cif/moreReport.fhtml', data=body,
                                 headers={'User-Agent': UA, 'Content-Type': 'application/x-www-form-urlencoded',
                                          'Referer': BASE + '/cif/listIndex.fhtml?nodeid=10163'},
                                 method='POST')
    raw = _open(req)
    txt = raw.decode('utf-8', 'ignore')
    j = json.loads(txt)
    # 结构探测：可能是 {list:[...]} 或 [{...}] 或 {rows:[...]}
    items = None
    for k in ('list', 'rows', 'data', 'result'):
        if isinstance(j, dict) and isinstance(j.get(k), list):
            items = j[k]
            break
    if items is None and isinstance(j, list):
        items = j
    if items is None:
        raise RuntimeError('cif list: unknown json shape: ' + txt[:200])
    for it in items:
        title = str(it.get('title', ''))
        rel = it.get('relpath', '')
        if '36个大中城市食用农产品零售价格' in title and rel:
            return {'title': title, 'relpath': rel, 'publishDate': it.get('publishDate', '')}
    raise RuntimeError('cif list: no retail-price article in page 1, titles=' + json.dumps([it.get('title') for it in items[:6]], ensure_ascii=False))


def fetch_detail_html(relpath):
    url = rel if relpath.startswith('http') else BASE + '/' + relpath.lstrip('/')
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    return _open(req).decode('utf-8', 'ignore')


def parse_table(html):
    """解析详情页表格：逐行 tr -> td 文本；第1个td(可能colspan)为品种，后3个为价格/环比/同比"""
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)
    items = {}
    order = []
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        if len(tds) < 4:
            continue
        cells = []
        for td in tds:
            s = re.sub(r'<[^>]+>', '', td)
            s = htmlmod.unescape(s).replace('\xa0', ' ').strip()
            cells.append(s)
        # cells[0] = 品种（可能含缩进），cells[1..3] = 价格/环比/同比
        name = cells[0].replace('　', '').strip()
        price, wk, yr = cells[1], cells[2], cells[3]
        # 分组行（价格空）跳过；纯数字校验
        def is_num(s):
            s = s.replace('%', '').replace('—', '').replace('-', '').replace('.', '').strip()
            return s.isdigit() and s != ''
        if not name or name in ('品种', '零售价格') or not is_num(price):
            continue
        try:
            pv = float(cells[1])
        except ValueError:
            continue
        def fnum(s):
            s = s.strip().replace('%', '')
            try:
                return float(s) if s else None
            except ValueError:
                return None
        items[name] = {'v': pv, 'w': fnum(cells[2]), 'y': fnum(cells[3])}
        order.append(name)
    return items, order


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    db = {}
    if os.path.exists(OUT):
        try:
            db = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            db = {}
    if os.path.exists(SAMPLE) and '--sample' in sys.argv:
        # 本地解析验证模式
        html = open(SAMPLE, encoding='utf-8').read()
        items, order = parse_table(html)
        print('SAMPLE_PARSE items=%d' % len(items))
        for n in order[:12]:
            print(' ', n, items[n])
        return
    meta = fetch_list()
    html = fetch_detail_html(meta['relpath'])
    items, order = parse_table(html)
    if not items:
        raise RuntimeError('cif detail: parse empty, html len=' + len(html))
    # 记录键：用标题里的周区间（dateLabel），加发布日期保证唯一
    date_label = meta['title'].replace('商务预报：', '').strip()
    key = date_label
    rec = {'dateLabel': date_label, 'pubDate': meta['publishDate'], 'items': items, 'order': order}
    db[key] = rec
    tmp = OUT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, OUT)
    print('SAVED', key, 'items=%d' % len(items), 'total_weeks=%d' % len(db))


if __name__ == '__main__':
    main()
