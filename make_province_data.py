# -*- coding: utf-8 -*-
"""生成 src/province_data.js：各省批发价 → 零售折算(元/500克)
零售 = 批发(元/公斤) / 2 × coeff(1.15)  —— 批发→零售市场加成约 10-20%，取 1.15，口径在页面标注
输入：data/province_prices.json（当日快照）+ data/province_history.json（历史序列，可选）
输出 items: {品种: {r:零售折算值, m:该省上报市场数, c:分类, s:近12周采样序列(周度,折算零售)}}
"""
import json, os, io, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'data', 'province_prices.json')
HIST = os.path.join(HERE, 'data', 'province_history.json')
OUT = os.path.join(HERE, 'src', 'province_data.js')

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
WEEKS = 12

def sample_weekly(dates, prices, weeks=WEEKS):
    """近 weeks 周采样：按日期每 7 天取 1 点（从最新往回），返回升序；不足 2 点返回 None
    数据点少于 8 个时保留逐日点（首版即可画出曲线），点数足够后再按周采样"""
    if not dates or not prices or len(prices) < 2:
        return None
    if len(prices) < 8:
        pts = [p for p in prices if isinstance(p, (int, float))]
        return pts if len(pts) >= 2 else None
    pts = []
    last = None
    for i in range(len(dates) - 1, -1, -1):
        try:
            d = datetime.datetime.strptime(str(dates[i])[:10], '%Y-%m-%d').date()
        except Exception:
            continue
        if last is None or (last - d).days >= 7:
            pts.append(prices[i])
            last = d
        if len(pts) >= weeks:
            break
    pts.reverse()
    return pts if len(pts) >= 2 else None

with open(SRC, encoding='utf-8') as f:
    data = json.load(f)
hist = {}
if os.path.exists(HIST):
    try:
        with open(HIST, encoding='utf-8') as f:
            hist = json.load(f)
    except Exception:
        hist = {}

provs = {}
n_with_price = 0
n_with_series = 0
for pname, vv in data['provinces'].items():
    code = PROV_CODE.get(pname)
    if not code:
        continue
    items = {}
    hist_prov = hist.get(pname, {}) if isinstance(hist.get(pname), dict) else {}
    for vn, d in vv.items():
        p = d.get('p')
        markets = d.get('markets') or 0
        if p is None:
            continue
        r = round(p / 2.0 * COEFF, 2)
        item = {'r': r, 'm': markets, 'c': CAT_MAP.get(d.get('cat'), '蔬')}
        hp = hist_prov.get(vn)
        if isinstance(hp, dict) and hp.get('dates') and hp.get('prices'):
            wk = sample_weekly(hp['dates'], hp['prices'])
            if wk:
                item['s'] = [round(v / 2.0 * COEFF, 2) for v in wk]
                n_with_series += 1
        items[vn] = item
        n_with_price += 1
    provs[code] = {'n': pname, 'items': items}

lines = []
lines.append("/* 各省基础农产品价格（自动生成，勿手改）")
lines.append(" * 来源：农业农村部全国农产品批发市场价格信息系统 pfsc.agri.cn（日度批发价）")
lines.append(" * 数据日期：" + str(data.get('date', '')))
lines.append(" * 零售折算：批发价(元/公斤) ÷ 2 × " + str(COEFF) + " = 元/500克（批发→零售市场加成取 1.15）")
lines.append(" * items: {品种: {r:零售折算值, m:该省上报市场数, c:分类, s:近12周采样序列(周度,折算零售)}}")
lines.append(" * 序列来源：每日快照累积（pfsc 仅提供当日截面，无历史曲线接口，按日存档后周采样）")
lines.append(" */")
lines.append("export const PROV_DATA = {")
lines.append("  date: '" + str(data.get('date', '')) + "',")
lines.append("  coeff: " + str(COEFF) + ",")
lines.append("  unit: '元/500克（省级=批发÷2×" + str(COEFF) + " 折算零售）',")
lines.append("  provs: {")
for code in PROV_CODE.values():
    p = provs.get(code)
    if not p:
        continue
    lines.append("    " + code + ": {n:'" + p['n'] + "', items:{")
    for vn, it in sorted(p['items'].items()):
        if 's' in it:
            lines.append(f"      '{vn}': {{r:{it['r']}, m:{it['m']}, c:'{it['c']}', s:[{','.join(str(x) for x in it['s'])}]}},")
        else:
            lines.append(f"      '{vn}': {{r:{it['r']}, m:{it['m']}, c:'{it['c']}'}},")
    lines.append("    }},")
lines.append("  },")
lines.append("};")
lines.append("")

body = "\n".join(lines)
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    f.write(body)
print("写入:", OUT)
print("省份:", len(provs), "有价品种项:", n_with_price, "带序列项:", n_with_series)
sz = os.path.getsize(OUT)
print("大小:", sz, "字节")

# 同构 JSON（供小程序 network 拉取，与 PROV_DATA 结构完全一致）
json_out = {
    'date': str(data.get('date', '')),
    'coeff': COEFF,
    'unit': '元/500克（省级=批发÷2×' + str(COEFF) + ' 折算零售）',
    'provs': provs,
}
JSON_OUT = os.path.join(HERE, 'data', 'prov_data.json')
with open(JSON_OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(json_out, f, ensure_ascii=False, separators=(',', ':'))
print("写入:", JSON_OUT, os.path.getsize(JSON_OUT), "字节")
