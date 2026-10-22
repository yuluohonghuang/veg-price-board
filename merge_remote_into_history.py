# -*- coding: utf-8 -*-
"""把远端 province_retail.json（昨日折算零售快照）反算批发原值并入历史序列首日点
用途：pfsc 无历史曲线接口，历史序列靠每日快照累积；首版曲线需要至少 2 个点，
远端 JSON 里的昨日(10-21)折算零售价可反算批发原值(批发=零售/1.15*2)作为第一个点。
"""
import json, os, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, 'data', 'province_history.json')
REMOTE = 'https://yuluohonghuang.github.io/veg-price-data/province_retail.json'
COEFF = 1.15
# 远端 JSON 的 provs key 是省码（bj/zj/...），历史文件 key 是省名（浙江/北京/...）
REV_MAP = {
    'bj': '北京', 'tj': '天津', 'heb': '河北', 'sxs': '山西', 'nmg': '内蒙古',
    'ln': '辽宁', 'jl': '吉林', 'hlj': '黑龙江', 'sh': '上海', 'js': '江苏',
    'zj': '浙江', 'ah': '安徽', 'fj': '福建', 'jx': '江西', 'sd': '山东',
    'hen': '河南', 'hub': '湖北', 'hun': '湖南', 'gd': '广东', 'gx': '广西',
    'hain': '海南', 'cq': '重庆', 'sc': '四川', 'gz': '贵州', 'yn': '云南',
    'xz': '西藏', 'sx': '陕西', 'gs': '甘肃', 'qh': '青海', 'nx': '宁夏', 'xj': '新疆',
}

with urllib.request.urlopen(REMOTE, timeout=20) as resp:
    remote = json.loads(resp.read().decode('utf-8'))
rdate = remote.get('date', '')
print("远端日期:", rdate)

hist = json.load(open(HIST, encoding='utf-8'))
# 清理上一轮误写入的省码 key（其数据并入省名 key）
for code in REV_MAP:
    if code in hist:
        del hist[code]
added = 0
for code, pv in remote.get('provs', {}).items():
    pname = REV_MAP.get(code)
    if not pname or not isinstance(pv, dict):
        continue
    hprov = hist.setdefault(pname, {})
    for vn, it in pv.get('items', {}).items():
        r = it.get('r')
        if r is None:
            continue
        wh = round(r / COEFF * 2.0, 2)  # 折算零售 → 批发原值
        h = hprov.setdefault(vn, {'dates': [], 'prices': []})
        if rdate in h['dates']:
            h['prices'][h['dates'].index(rdate)] = wh
        else:
            h['dates'].append(rdate)
            h['prices'].append(wh)
            added += 1
# 每省按日期排序（插入首日点后保持升序）
for pname, pv in hist.items():
    if pname == '_meta' or not isinstance(pv, dict):
        continue
    for it in pv.values():
        if isinstance(it, dict) and it.get('dates'):
            z = sorted(zip(it['dates'], it['prices']))
            it['dates'], it['prices'] = [x[0] for x in z], [x[1] for x in z]
hist['_meta'] = dict(hist.get('_meta', {}), backfilled=rdate)
with open(HIST, 'w', encoding='utf-8') as f:
    json.dump(hist, f, ensure_ascii=False, indent=1)
print("已并入首日点:", added, "->", HIST)
