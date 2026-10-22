# -*- coding: utf-8 -*-
"""生成远端 JSON（供小程序 network 拉取，免发版更新）
结构：{date, coeff, unit, provs:{省码:{n, items:{品种:{r,m,c}}}}}
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'data', 'province_prices.json')
OUT = os.path.join(HERE, 'data', 'province_retail.json')

PROV_CODE = {
    '北京':'bj','天津':'tj','河北':'heb','山西':'sxs','内蒙古':'nmg',
    '辽宁':'ln','吉林':'jl','黑龙江':'hlj','上海':'sh','江苏':'js',
    '浙江':'zj','安徽':'ah','福建':'fj','江西':'jx','山东':'sd',
    '河南':'hen','湖北':'hub','湖南':'hun','广东':'gd','广西':'gx',
    '海南':'hain','重庆':'cq','四川':'sc','贵州':'gz','云南':'yn',
    '西藏':'xz','陕西':'sx','甘肃':'gs','青海':'qh','宁夏':'nx','新疆':'xj',
}
CAT_MAP = {'蔬菜':'蔬','粮油':'粮','肉蛋':'肉','水产':'水','水果':'果','食用菌':'蔬'}
COEFF = 1.15

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)

provs = {}
for pname, vv in data['provinces'].items():
    code = PROV_CODE.get(pname)
    if not code:
        continue
    items = {}
    for vn, d in vv.items():
        p = d.get('p')
        if p is None:
            continue
        items[vn] = {'r': round(p / 2.0 * COEFF, 2), 'm': d.get('markets') or 0,
                     'c': CAT_MAP.get(d.get('cat'), '蔬')}
    provs[code] = {'n': pname, 'items': items}

out = {
    'date': data.get('date', ''),
    'coeff': COEFF,
    'unit': '元/500克（省级=批发÷2×1.15 折算零售）',
    'updatedAt': '',
    'provs': provs,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=0, separators=(',', ':'))
print('写入:', OUT)
print('省份:', len(provs))
print('大小:', os.path.getsize(OUT), '字节')
