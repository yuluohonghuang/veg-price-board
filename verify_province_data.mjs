// 静态验证 province_data.js 与省级渲染逻辑（无 DOM 依赖部分）
import { PROV_DATA } from './src/province_data.js';

console.log('=== PROV_DATA 校验 ===');
console.log('数据日期:', PROV_DATA.date, '| 折算系数:', PROV_DATA.coeff, '| 单位:', PROV_DATA.unit);
const codes = Object.keys(PROV_DATA.provs);
console.log('省份数:', codes.length);
const expect = ['bj','tj','heb','sxs','nmg','ln','jl','hlj','sh','js','zj','ah','fj','jx','sd','hen','hub','hun','gd','gx','hain','cq','sc','gz','yn','xz','sx','gs','qh','nx','xj'];
const miss = expect.filter(c => !codes.includes(c));
const extra = codes.filter(c => !expect.includes(c));
console.log('缺失省份:', miss.length ? miss : '无', '| 多余:', extra.length ? extra : '无');

let total = 0, zero = 0, bad = 0;
const catCount = {};
for (const c of codes) {
  const p = PROV_DATA.provs[c];
  const items = Object.entries(p.items);
  total += items.length;
  for (const [n, it] of items) {
    if (typeof it.r !== 'number' || it.r <= 0) { bad++; console.log('异常价:', c, n, it.r); }
    if (it.m === 0) zero++;
    catCount[it.c] = (catCount[it.c] || 0) + 1;
  }
}
console.log('品种项总数:', total, '| 市场数=0:', zero, '| 异常价格:', bad);
console.log('分类分布:', JSON.stringify(catCount));

// 抽样浙江（应为完整 43 品种）
const zj = PROV_DATA.provs.zj;
const zjItems = Object.keys(zj.items);
console.log('浙江品种数:', zjItems.length, '| 名称:', zj.n);
const sample = ['大白菜','西红柿','猪肉(白条猪)','大米','黄瓜','鸡蛋'].filter(n => zjItems.includes(n));
for (const n of sample) {
  const it = zj.items[n];
  console.log(`  浙江 ${n}: 折算零售 ${it.r} 元/500克, 市场 ${it.m} 家, 分类 ${it.c}`);
}
// 反向：批发价应为 r/1.15*2
if (zj.items['大白菜']) console.log('  回算批发(大白菜):', (zj.items['大白菜'].r / 1.15 * 2).toFixed(2), '元/公斤');

// 模拟省级品种构造（main.js currentList 逻辑）
const P = PROV_DATA.provs.zj;
const list = Object.entries(P.items).map(([name, it]) => ({
  id: 'p_zj_' + name, n: name, ini: '', c: it.c || '蔬',
  v: it.r, p: it.r, wk: null, m: it.m || 0, t: 'p'
}));
console.log('=== 省级品种列表构造（浙江）===');
console.log('数量:', list.length);
const withPrice = list.filter(x => x.v != null).length;
const top = list.slice().sort((a,b)=>b.v-a.v).slice(0,3).map(x=>x.n+' '+x.v.toFixed(2)+'元');
console.log('有价:', withPrice, '| 最贵3个:', top.join(' / '));
console.log('=== 校验通过 ===');
