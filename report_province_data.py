# -*- coding: utf-8 -*-
"""生成各省批发价数据概览报告"""
import json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, 'data', 'province_prices.json')
with open(path, encoding='utf-8') as f:
    data = json.load(f)

print("数据日期:", data['date'])
print("单位:", data['unit'])
print("来源:", data['source'])
print()
print("=== 各省覆盖（有价品种数/43）===")
rows = []
for prov, vv in data['provinces'].items():
    n_ok = sum(1 for d in vv.values() if d.get('p') is not None)
    rows.append((n_ok, prov))
for n, prov in sorted(rows, reverse=True):
    vv = data['provinces'][prov]
    sample = [k for k, d in vv.items() if d.get('p') is not None][:5]
    print(f"  {prov}: {n}/43  e.g. {sample}")

print()
print("=== 品种覆盖（有数据的省份数）===")
vcnt = collections.Counter()
for prov, vv in data['provinces'].items():
    for vn, d in vv.items():
        if d.get('p') is not None:
            vcnt[vn] += 1
for vn, c in sorted(vcnt.items(), key=lambda x: -x[1]):
    print(f"  {vn}: {c} 省")
