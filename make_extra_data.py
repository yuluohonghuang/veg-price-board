# -*- coding: utf-8 -*-
"""生成 src/extra_data.js（前端 EXDATA：指数序列 + 全国大盘 + 36城零售）

输入1：data/national_daily.json（指数+大盘，按日累积）
输入2：data/cif_retail.json（商务部周度零售）
输出：src/extra_data.js
"""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data')
OUT = os.path.join(HERE, 'src', 'extra_data.js')

IDX_MAP = {
    '农产品批发价格200指数': 'p200',
    '“菜篮子”产品批发价格指数': 'basket',
    '粮油产品批发价格指数': 'grainOil',
    '粮食': 'grain',
    '食用油': 'oil',
    '蔬菜': 'veg',
    '畜产品': 'animal',
    '水产品': 'aqua',
    '水果': 'fruit',
}


def fmt_date(d):
    """'2026-10-22' -> '10-22'（前端格式）"""
    return d[5:7].lstrip('0') + '-' + d[8:10]


def main():
    nd = {}
    p = os.path.join(DATA_DIR, 'national_daily.json')
    if os.path.exists(p):
        nd = json.load(open(p, encoding='utf-8'))
    # 指数序列：按日期排序，每个指数一条（保留 null 缺口）
    days = sorted(nd.keys())
    if not days:
        raise SystemExit('national_daily.json empty')
    dates = [fmt_date(d) for d in days]
    series = {k: [] for k in IDX_MAP.values()}
    for d in days:
        idx = nd[d].get('indexes', {})
        for cname, key in IDX_MAP.items():
            v = idx.get(cname)
            series[key].append(v if v is not None else None)
    # 最新一日大盘
    last = nd[days[-1]]
    nat = {
        'date': last.get('date', days[-1]),
        'p200': last.get('p200'), 'p200_chg': last.get('p200_chg'),
        'basket': last.get('basket'), 'basket_chg': last.get('basket_chg'),
        'meat': last.get('meat', {}),
        'vegAvg': last.get('vegAvg'), 'vegAvg_chg': last.get('vegAvg_chg'),
        'fruitAvg': last.get('fruitAvg'), 'fruitAvg_chg': last.get('fruitAvg_chg'),
        'fish': last.get('fish', {}),
        'rise': last.get('rise', []),
        'fall': last.get('fall', []),
    }
    # 零售（cif 最新周）
    retail = {'dateLabel': None, 'items': {}}
    cif_p = os.path.join(DATA_DIR, 'cif_retail.json')
    if os.path.exists(cif_p):
        try:
            cif = json.load(open(cif_p, encoding='utf-8'))
            keys = sorted(cif.keys())
            if keys:
                wk = cif[keys[-1]]
                retail = {'dateLabel': wk.get('dateLabel'), 'items': wk.get('items', {})}
        except Exception:
            pass
    obj = {
        'updatedAt': days[-1],
        'idx': {'date': dates, **series},
        'nat': nat,
        'retail': retail,
    }
    body = 'export const EXDATA = ' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ';\n'
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(body)
    print('OK days=%d series=%s nat_date=%s retail=%s' % (
        len(days), ','.join(k for k, v in series.items() if any(x is not None for x in v)),
        nat['date'], retail['dateLabel'] or 'none'))


if __name__ == '__main__':
    main()
