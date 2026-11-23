# -*- coding: utf-8 -*-
"""每日全国大盘 + 指数数据抓取（方案2：官方日度大盘，替代演示值）

输入1：ncpscxx.moa.gov.cn/common-price-index/getIndexByLevel —— 农产品批发价格200指数等 8 个分项指数日度值（免鉴权 POST）
输入2：scs.moa.gov.cn/jcyj/ —— 农业农村部市场与信息化司每日行情稿（200指数、菜篮子、5肉蛋、28种蔬菜均价、6种水果均价、4种鱼、46品种涨跌前五）
输出：data/national_daily.json —— 按日追加 {date:{indexes,meat,vegAvg,fruitAvg,fish,rise,fall}}，同日去重
"""
import urllib.request, urllib.parse, ssl, gzip, json, os, re, sys, time, datetime

BASE_SCS = 'https://scs.moa.gov.cn'
BASE_NCPS = 'https://ncpscxx.moa.gov.cn'
BASE_PFS = 'https://pfsc.agri.cn'
# pfsc 门户指数日序列 -> national_daily 的指数名（用于补齐漏跑日期的指数）
PFS_IDX_MAP = {
    'agriculture': '农产品批发价格200指数',
    'grainAndOil': '粮油产品批发价格指数',
    'vegetableBasket': '“菜篮子”产品批发价格指数',
}
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36'
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data')
OUT = os.path.join(DATA_DIR, 'national_daily.json')


def get(url, headers=None, retry=3):
    h = {'User-Agent': UA, 'Accept-Encoding': 'gzip'}
    if headers: h.update(headers)
    last = None
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
                d = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    d = gzip.decompress(d)
                return d.decode('utf-8', 'ignore')
        except Exception as e:
            last = e
            time.sleep(5.0)
    raise last


def post(url, data=None, headers=None, retry=3):
    h = {'User-Agent': UA, 'Accept-Encoding': 'gzip',
         'Content-Type': 'application/x-www-form-urlencoded',
         'Origin': BASE_NCPS, 'Referer': BASE_NCPS + '/product-app/'}
    if headers: h.update(headers)
    body = urllib.parse.urlencode(data or {}).encode()
    last = None
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=h, method='POST')
            with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
                d = resp.read()
                if resp.headers.get('Content-Encoding') == 'gzip':
                    d = gzip.decompress(d)
                return d.decode('utf-8', 'ignore')
        except Exception as e:
            last = e
            time.sleep(5.0)
    raise last


def fetch_indexes():
    """ncpscxx 指数接口：返回 {指数名: value}"""
    txt = post(BASE_NCPS + '/product/common-price-index/getIndexByLevel')
    j = json.loads(txt)
    if j.get('code') != 0:
        raise RuntimeError('index api code=' + str(j.get('code')))
    out = {}
    for grp in j.get('data') or []:
        for it in grp:
            name = it.get('indexName', '')
            val = it.get('indexValue')
            if name and val is not None and name not in out:
                out[name] = float(val)
    return out


def fetch_pfs_index_history(pages=1, size=60, retry=2):
    """pfsc 门户指数日序列（按发布日返回最近 N 天）：{YYYY-MM-DD: {agriculture, grainAndOil, vegetableBasket}}
    用途：某天漏跑时，指数仍可从上游补齐，不必等下一次快照；只补指数，不含肉蛋/蔬菜均价等稿件字段"""
    url = BASE_PFS + '/price_portal/pi-info-day/getPortalPiInfoDay'
    h = {'User-Agent': UA, 'Accept': 'application/json, text/plain, */*',
         'Origin': BASE_PFS, 'Referer': BASE_PFS + '/', 'Content-Type': 'application/json'}
    out = {}
    for pn in range(1, pages + 1):
        last = None
        for i in range(retry + 1):
            try:
                body = json.dumps({'pageNum': pn, 'pageSize': size}).encode()
                req = urllib.request.Request(url, data=body, headers=h, method='POST')
                with urllib.request.urlopen(req, timeout=25, context=CTX) as resp:
                    d = resp.read()
                    if resp.headers.get('Content-Encoding') == 'gzip':
                        d = gzip.decompress(d)
                    j = json.loads(d.decode('utf-8', 'ignore'))
                for it in j.get('content') or []:
                    day = str(it.get('publishDate') or '')
                    if len(day) == 10:
                        out[day] = it
                last = None
                break
            except Exception as e:
                last = e
                time.sleep(5.0)
        if last is not None:
            raise last
    return out


def backfill_indexes(db, hist):
    """把 pfsc 指数日序列并入 national_daily：仅填补缺失的指数值，不覆盖已有数据"""
    filled = 0
    days_added = 0
    for day, it in hist.items():
        rec = db.get(day)
        if rec is None:
            rec = {'date': day}
            db[day] = rec
            days_added += 1
        idx = rec.setdefault('indexes', {})
        for src, dst in PFS_IDX_MAP.items():
            v = it.get(src)
            if v is None:
                continue
            if idx.get(dst) is None:
                idx[dst] = float(v)
                filled += 1
    return filled, days_added


def fetch_scs_article():
    """scs 列表页 -> 最新一篇行情稿 URL -> 正文文本"""
    list_url = BASE_SCS + '/jcyj/'
    list_html = get(list_url)
    def abs_url(u):
        return urllib.parse.urljoin(list_url, u)
    m = re.search(r'href="([^"]*t(\d{8})_[0-9]+\.htm)"[^>]*>(\d{1,2}月\d{1,2}日[^<]*200指数[^<]*)', list_html)
    if not m:
        # 兜底：任意 t2026xxxx 链接
        m2 = re.search(r'href="([^"]*t(20\d{6})_[0-9]+\.htm)"', list_html)
        if not m2:
            raise RuntimeError('scs list: no article link found')
        url, date8 = abs_url(m2.group(1)), m2.group(2)
    else:
        url, date8 = abs_url(m.group(1)), m.group(2)
    html = get(url)
    # 提取正文段落文本（去掉标签）
    body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', html)
    paras = re.findall(r'<p[^>]*>([\s\S]*?)</p>', body)
    txt = ' '.join(re.sub(r'<[^>]+>', '', p).strip() for p in paras)
    if not txt or '200指数' not in txt:
        raise RuntimeError('scs article: no content for ' + url)
    date = date8[:4] + '-' + date8[4:6] + '-' + date8[6:8]
    return date, txt


def parse_scs(txt):
    """解析行情稿正文 -> dict（_chg 带符号：负=降 正=升）"""
    out = {}
    def num(s):
        s = s.strip()
        return float(s) if re.fullmatch(r'-?\d+(\.\d+)?', s) else None
    def signed(dirw, val):
        """方向词+数字 -> 带符号变化值"""
        v = num(val)
        if v is None:
            return None
        if '上升' in dirw or '上涨' in dirw:
            return v
        if '下降' in dirw or '下跌' in dirw:
            return -v
        return 0.0
    m = re.search(r'“农产品批发价格200指数”为([\d.]+)，比([^，。0-9]{1,12})([0-9]+(?:\.[0-9]+)?)个点', txt)
    if m:
        out['p200'] = num(m.group(1)); out['p200_chg'] = signed(m.group(2), m.group(3))
    m = re.search(r'“菜篮子”产品批发价格指数为([\d.]+)，比([^，。0-9]{1,12})([0-9]+(?:\.[0-9]+)?)个点', txt)
    if m:
        out['basket'] = num(m.group(1)); out['basket_chg'] = signed(m.group(2), m.group(3))
    meat = {}
    for name, key in [('猪肉', 'pork'), ('牛肉', 'beef'), ('羊肉', 'mutton'), ('鸡蛋', 'egg'), ('白条鸡', 'chicken')]:
        m = re.search(name + r'(?:平均价格为|为)?([0-9]+(?:\.[0-9]+)?)元/公斤，比([^；%0-9]{1,14})([0-9]+(?:\.[0-9]+)?)%', txt)
        if m:
            meat[key] = num(m.group(1)); meat[key + '_chg'] = signed(m.group(2), m.group(3))
    if meat: out['meat'] = meat
    m = re.search(r'重点监测的28种蔬菜平均价格为([0-9]+(?:\.[0-9]+)?)元/公斤，比([^；%0-9]{1,14})([0-9]+(?:\.[0-9]+)?)%', txt)
    if m: out['vegAvg'] = num(m.group(1)); out['vegAvg_chg'] = signed(m.group(2), m.group(3))
    m = re.search(r'重点监测的6种水果平均价格为([0-9]+(?:\.[0-9]+)?)元/公斤，比([^；%0-9]{1,14})([0-9]+(?:\.[0-9]+)?)%', txt)
    if m: out['fruitAvg'] = num(m.group(1)); out['fruitAvg_chg'] = signed(m.group(2), m.group(3))
    fish = {}
    for name, key in [('鲫鱼', 'crucian'), ('鲤鱼', 'carp'), ('白鲢鱼', 'silvercarp'), ('大带鱼', 'hairtail')]:
        m = re.search(name + r'([0-9]+(?:\.[0-9]+)?)元/公斤，比([^；%0-9]{1,14})([0-9]+(?:\.[0-9]+)?)%', txt)
        if m:
            fish[key] = num(m.group(1)); fish[key + '_chg'] = signed(m.group(2), m.group(3))
    if fish: out['fish'] = fish
    m = re.search(r'价格升幅前五名的是([^，]+)、([^，]+)、([^，]+)、([^，]+)和([^，]+)，幅度分别为([\d.]+)%、([\d.]+)%、([\d.]+)%、([\d.]+)%和([\d.]+)%', txt)
    if m:
        out['rise'] = [{'n': m.group(1), 'v': num(m.group(6))}, {'n': m.group(2), 'v': num(m.group(7))},
                       {'n': m.group(3), 'v': num(m.group(8))}, {'n': m.group(4), 'v': num(m.group(9))},
                       {'n': m.group(5), 'v': num(m.group(10))}]
    m = re.search(r'价格降幅前五名的是([^，]+)、([^，]+)、([^，]+)、([^，]+)和([^，]+)，幅度分别为([\d.]+)%、([\d.]+)%、([\d.]+)%、([\d.]+)%和([\d.]+)%', txt)
    if m:
        out['fall'] = [{'n': m.group(1), 'v': num(m.group(6))}, {'n': m.group(2), 'v': num(m.group(7))},
                       {'n': m.group(3), 'v': num(m.group(8))}, {'n': m.group(4), 'v': num(m.group(9))},
                       {'n': m.group(5), 'v': num(m.group(10))}]
    return out


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    db = {}
    if os.path.exists(OUT):
        try:
            db = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            db = {}
    # 0) 指数历史补齐：pfsc 门户按发布日提供近 90 天指数，漏跑日期也能补回，避免序列断点
    try:
        pfs_hist = fetch_pfs_index_history()
        filled, added = backfill_indexes(db, pfs_hist)
        print('PFS_BACKFILL covered=%d days filled=%d values new_days=%d' % (len(pfs_hist), filled, added))
    except Exception as e:
        print('PFS_BACKFILL_FAIL', str(e)[:120])
    # 1) 指数
    try:
        indexes = fetch_indexes()
    except Exception as e:
        print('INDEX_FAIL', str(e)[:120])
        indexes = {}
    # 2) scs 行情稿
    try:
        date, txt = fetch_scs_article()
        scs = parse_scs(txt)
    except Exception as e:
        print('SCS_FAIL', str(e)[:120])
        date = datetime.date.today().isoformat()
        scs = {}
    rec = db.get(date, {})
    rec['date'] = date
    rec['indexes'] = indexes or rec.get('indexes', {})
    if scs:
        for k in ('p200', 'p200_chg', 'basket', 'basket_chg', 'meat', 'vegAvg', 'vegAvg_chg',
                  'fruitAvg', 'fruitAvg_chg', 'fish', 'rise', 'fall'):
            if k in scs:
                rec[k] = scs[k]
    db[date] = rec
    # 写盘（断点保护）
    tmp = OUT + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, OUT)
    print('SAVED', date, 'indexes=%d' % len(rec.get('indexes', {})),
          'meat=%s' % ('Y' if 'meat' in rec else 'N'),
          'vegAvg=%s' % ('Y' if 'vegAvg' in rec else 'N'),
          'rise=%s' % ('Y' if 'rise' in rec else 'N'),
          'total_days=%d' % len(db))


if __name__ == '__main__':
    main()
