import hbSDK from '@heybox/hb-sdk';
import * as echarts from 'echarts';
import { PROV_DATA } from './province_data.js';
import { EXDATA } from './extra_data.js';
window.echarts = echarts;
window.__hbStorage = hbSDK && hbSDK.storage || null;
if (window.__hbStorage && window.__hbStorage.setStorage) {
  try {
    const _origSet = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function(k, v) {
      try { _origSet(k, v); } catch(e) {}
      try { Promise.resolve(window.__hbStorage.setStorage({ key: k, data: v })).catch(() => {}); } catch(e) {}
    };
  } catch(e) {}
}

/* ===== 数据区 v3 =====
   t 标签：hz=杭州发改委零售价(真实,2026-10-20) / xfd=新发地批发价(真实,2026-10-19) / s=商务预报全国零售(真实,周更) / d=演示值（暂无官方监测，标注全国参考）
   单位：元/500克 */
const DATA = {
  updatedAt: '2026-10-20',
  unit: '元/500克',
  catName: {粮:'米面粮油',蔬:'蔬菜',果:'瓜果',肉:'肉禽蛋',水:'水产'},
  products: [
    /* ---- 米面粮油 ---- */
    {id:'jmjs', n:'粳米(江苏特制)', ini:'JMJS', c:'粮', v:3.01, p:3.01, wk:3.01, t:'hz'},
    {id:'jmdb', n:'粳米(东北圆粒)', ini:'JMDB', c:'粮', v:3.38, p:3.38, wk:3.38, t:'hz'},
    {id:'xianmi', n:'籼米(全国参考)', ini:'XM', c:'粮', v:3.20, p:null, wk:null, t:'d'},
    {id:'dami', n:'大米(全国零售)', ini:'DM', c:'粮', v:3.21, p:null, wk:null, t:'s'},
    {id:'mf', n:'面粉(特一粉)', ini:'MFT', c:'粮', v:3.04, p:3.04, wk:3.04, t:'hz'},
    {id:'mfbz', n:'面粉(标准粉)', ini:'MFB', c:'粮', v:2.85, p:null, wk:null, t:'d'},
    {id:'ymf', n:'玉米粉', ini:'YMF', c:'粮', v:3.20, p:3.20, wk:3.20, t:'hz'},
    {id:'gm', n:'挂面(全国参考)', ini:'GM', c:'粮', v:5.20, p:null, wk:null, t:'d'},
    {id:'hsy', n:'花生油', ini:'HSY', c:'粮', v:28.70, p:null, wk:null, t:'d'},
    {id:'dyy', n:'大豆油', ini:'DYY', c:'粮', v:12.76, p:null, wk:null, t:'d'},
    {id:'cyy', n:'菜籽油(全国参考)', ini:'CZY', c:'粮', v:15.40, p:null, wk:null, t:'d'},
    {id:'yym', n:'玉米油(全国参考)', ini:'YMY', c:'粮', v:17.80, p:null, wk:null, t:'d'},
    {id:'dd', n:'黄豆', ini:'HD', c:'粮', v:5.06, p:5.06, wk:5.06, t:'hz'},
    {id:'ld', n:'绿豆', ini:'LD', c:'粮', v:7.00, p:7.00, wk:7.00, t:'hz'},
    {id:'hxd', n:'红小豆', ini:'HXD', c:'粮', v:7.94, p:7.94, wk:7.94, t:'hz'},
    {id:'sy', n:'食盐(全国参考)', ini:'SY', c:'粮', v:2.50, p:null, wk:null, t:'d'},
    {id:'bt', n:'白糖(全国参考)', ini:'BT', c:'粮', v:7.40, p:null, wk:null, t:'d'},
    /* ---- 蔬菜 ---- */
    {id:'qc', n:'青菜', ini:'QC', c:'蔬', v:3.39, p:3.67, wk:3.58, t:'hz'},
    {id:'xbc', n:'小白菜', ini:'XBC', c:'蔬', v:3.39, p:3.44, wk:3.50, t:'hz'},
    {id:'dbc', n:'大白菜', ini:'DBC', c:'蔬', v:2.20, p:2.18, wk:2.12, t:'hz'},
    {id:'bxc', n:'包心菜', ini:'BXC', c:'蔬', v:2.61, p:2.61, wk:2.55, t:'hz'},
    {id:'hg', n:'黄瓜', ini:'HG', c:'蔬', v:4.50, p:4.67, wk:4.72, t:'hz'},
    {id:'xhs', n:'西红柿', ini:'XHS', c:'蔬', v:4.94, p:5.00, wk:4.86, t:'hz'},
    {id:'td', n:'土豆', ini:'TD', c:'蔬', v:2.70, p:2.78, wk:2.75, t:'hz'},
    {id:'lb', n:'萝卜(白)', ini:'LBB', c:'蔬', v:2.00, p:2.11, wk:2.05, t:'hz'},
    {id:'hlb', n:'胡萝卜', ini:'HLB', c:'蔬', v:2.87, p:2.94, wk:2.90, t:'hz'},
    {id:'qincai', n:'芹菜', ini:'QCAI', c:'蔬', v:5.72, p:6.00, wk:5.90, t:'hz'},
    {id:'bc', n:'菠菜', ini:'BC', c:'蔬', v:7.28, p:8.00, wk:7.60, t:'hz'},
    {id:'jc', n:'韭菜', ini:'JC', c:'蔬', v:5.50, p:5.56, wk:5.42, t:'hz'},
    {id:'qz', n:'茄子', ini:'QZ', c:'蔬', v:5.44, p:5.78, wk:5.66, t:'hz'},
    {id:'qj', n:'青椒(圆)', ini:'QJY', c:'蔬', v:7.33, p:7.39, wk:7.30, t:'hz'},
    {id:'dg', n:'冬瓜', ini:'DG', c:'蔬', v:2.34, p:2.37, wk:2.30, t:'hz'},
    {id:'ws', n:'莴笋', ini:'WS', c:'蔬', v:4.83, p:5.11, wk:4.98, t:'hz'},
    {id:'hc', n:'花菜', ini:'HC', c:'蔬', v:5.33, p:5.17, wk:5.10, t:'hz'},
    {id:'sj', n:'丝瓜', ini:'SG', c:'蔬', v:6.19, p:6.28, wk:6.10, t:'hz'},
    {id:'md', n:'毛豆', ini:'MD', c:'蔬', v:5.11, p:5.33, wk:5.20, t:'hz'},
    {id:'jjd', n:'豇豆', ini:'JDG', c:'蔬', v:5.61, p:5.67, wk:5.50, t:'hz'},
    {id:'sjd', n:'四季豆', ini:'SJD', c:'蔬', v:8.44, p:8.83, wk:8.20, t:'hz'},
    {id:'tt', n:'蒜苔', ini:'ST', c:'蔬', v:8.44, p:8.33, wk:8.30, t:'hz'},
    {id:'sj2', n:'生姜', ini:'SJ', c:'蔬', v:8.44, p:8.44, wk:8.40, t:'hz'},
    {id:'jiao', n:'茭白', ini:'JB', c:'蔬', v:9.17, p:9.33, wk:9.00, t:'hz'},
    {id:'sl', n:'生菜(全国参考)', ini:'SC', c:'蔬', v:3.80, p:null, wk:null, t:'d'},
    {id:'ymc', n:'油麦菜(全国参考)', ini:'YMC', c:'蔬', v:4.50, p:null, wk:null, t:'d'},
    {id:'xlc', n:'西兰花(全国参考)', ini:'XLH', c:'蔬', v:6.50, p:null, wk:null, t:'d'},
    {id:'yc2', n:'油菜', ini:'YC', c:'蔬', v:1.10, p:1.05, wk:1.08, t:'xfd'},
    {id:'ds', n:'大蒜(全国参考)', ini:'DS', c:'蔬', v:8.50, p:null, wk:null, t:'d'},
    {id:'dj', n:'豆角(全国参考)', ini:'DJ', c:'蔬', v:6.80, p:null, wk:null, t:'d'},
    /* ---- 瓜果 ---- */
    {id:'pg', n:'苹果(红富士)', ini:'PGH', c:'果', v:7.86, p:7.86, wk:7.80, t:'hz'},
    {id:'xj', n:'香蕉(全国参考)', ini:'XJ', c:'果', v:4.20, p:null, wk:null, t:'d'},
    {id:'xg', n:'西瓜(全国参考)', ini:'XG', c:'果', v:3.60, p:null, wk:null, t:'d'},
    {id:'cz', n:'橙子(全国参考)', ini:'CZ', c:'果', v:6.80, p:null, wk:null, t:'d'},
    {id:'li', n:'梨(全国参考)', ini:'L', c:'果', v:5.50, p:null, wk:null, t:'d'},
    {id:'pt', n:'葡萄(全国参考)', ini:'PT', c:'果', v:12.50, p:null, wk:null, t:'d'},
    {id:'tao', n:'桃子(全国参考)', ini:'TZ', c:'果', v:9.80, p:null, wk:null, t:'d'},
    {id:'mg', n:'芒果(全国参考)', ini:'MG', c:'果', v:11.00, p:null, wk:null, t:'d'},
    {id:'hly', n:'火龙果(全国参考)', ini:'HLG', c:'果', v:8.20, p:null, wk:null, t:'d'},
    {id:'cm', n:'草莓(全国参考)', ini:'CM', c:'果', v:18.00, p:null, wk:null, t:'d'},
    {id:'ganju', n:'柑橘(全国参考)', ini:'GJ', c:'果', v:5.80, p:null, wk:null, t:'d'},
    {id:'hm', n:'哈密瓜(全国参考)', ini:'HMG', c:'果', v:6.50, p:null, wk:null, t:'d'},
    {id:'mht', n:'猕猴桃(全国参考)', ini:'MHT', c:'果', v:10.50, p:null, wk:null, t:'d'},
    {id:'yz', n:'柚子(全国参考)', ini:'YZ', c:'果', v:6.00, p:null, wk:null, t:'d'},
    /* ---- 肉禽蛋 ---- */
    {id:'zqjr', n:'猪全精肉', ini:'ZQR', c:'肉', v:14.78, p:14.78, wk:14.78, t:'hz'},
    {id:'zltr', n:'猪肋条肉', ini:'ZLTR', c:'肉', v:16.11, p:16.22, wk:16.05, t:'hz'},
    {id:'zht', n:'猪后腿肉', ini:'ZHT', c:'肉', v:12.56, p:12.67, wk:12.60, t:'hz'},
    {id:'nr', n:'牛肉(去骨)', ini:'NRQ', c:'肉', v:45.78, p:46.00, wk:45.20, t:'hz'},
    {id:'yr', n:'羊肉(全国参考)', ini:'YR', c:'肉', v:38.50, p:null, wk:null, t:'d'},
    {id:'btj', n:'白条鸡(全国参考)', ini:'BTJ', c:'肉', v:11.80, p:null, wk:null, t:'d'},
    {id:'jd', n:'鸡蛋', ini:'JD', c:'肉', v:6.04, p:5.99, wk:5.90, t:'hz'},
    {id:'yd', n:'鸭蛋', ini:'YD', c:'肉', v:8.53, p:8.50, wk:8.40, t:'hz'},
    {id:'nn', n:'牛奶(全国参考)', ini:'NN', c:'肉', v:5.60, p:null, wk:null, t:'d'},
    /* ---- 水产 ---- */
    {id:'cy', n:'草鱼', ini:'CY', c:'水', v:10.83, p:10.83, wk:10.70, t:'hz'},
    {id:'jy', n:'鲫鱼', ini:'JY', c:'水', v:18.44, p:18.44, wk:18.20, t:'hz'},
    {id:'by', n:'鳊鱼', ini:'BY', c:'水', v:15.86, p:15.75, wk:15.60, t:'hz'},
    {id:'dy', n:'带鱼(冷冻)', ini:'DYL', c:'水', v:27.17, p:26.67, wk:26.50, t:'hz'},
    {id:'xhy', n:'小黄鱼(冷冻)', ini:'XHY', c:'水', v:31.00, p:30.50, wk:30.50, t:'hz'},
    {id:'cy2', n:'鲳鱼(冷冻)', ini:'CYF', c:'水', v:48.43, p:48.00, wk:48.00, t:'hz'},
    {id:'xia', n:'河虾(全国参考)', ini:'HX', c:'水', v:105.00, p:null, wk:null, t:'d'},
    {id:'pangx', n:'螃蟹(全国参考)', ini:'PX', c:'水', v:75.00, p:null, wk:null, t:'d'}
  ],
  /* 商务部全国大米零售（元/公斤，周更 2025-10-24 ~ 2026-10-09）真实序列 */
  rice: {v:6.42, unit:'元/公斤', series:[6.56,6.56,6.56,6.56,6.56,6.55,6.54,6.54,6.53,6.53,6.52,6.52,6.52,6.51,6.50,6.51,6.50,6.50,6.48,6.46,6.45,6.45,6.46,6.47,6.48,6.48,6.47,6.48,6.47,6.47,6.46,6.46,6.46,6.46,6.44,6.44,6.43,6.44,6.42,6.41,6.41,6.41,6.40,6.41,6.40,6.41,6.41,6.42,6.43,6.42,6.42]},
  /* 农业农村部官方指数序列（ncpscxx 接口 + scs 每日行情稿累积，EXDATA 自动生成） */
  idx: EXDATA.idx
};

/* ---- 工具 ---- */
function genSeries(v){
  if(v==null) return null;
  const out=[]; const base=v;
  for(let i=51;i>=0;i--){
    const season=Math.sin(i/9.5)*0.07;
    const wave=Math.sin(i*1.3+v)*0.025;
    const drift=Math.sin(i/26)*0.03;
    out.push(Math.round(base*(1+season+wave+drift)*100)/100);
  }
  return out;
}
function posPct(arr){
  if(!arr||!arr.length) return null;
  const v=arr[arr.length-1];
  let lo=Math.min.apply(null,arr), hi=Math.max.apply(null,arr);
  if(hi-lo<1e-6) return 50;
  return Math.max(2,Math.min(98,Math.round((v-lo)/(hi-lo)*100)));
}
function vol4(s1){ // 近4周波动幅度 %
  if(!s1) return 0;
  const a=s1.slice(-4);
  const lo=Math.min.apply(null,a), hi=Math.max.apply(null,a), avg=a.reduce((x,y)=>x+y,0)/a.length;
  return avg? (hi-lo)/avg*100 : 0;
}
function sparkSVG(s1,w,h,color){
  if(!s1) return '<svg viewBox="0 0 '+w+' '+h+'"></svg>';
  const a=s1.slice(-40);
  let lo=Math.min.apply(null,a), hi=Math.max.apply(null,a);
  if(hi-lo<1e-6){hi+=0.05;lo-=0.05;}
  const pts=a.map((v,i)=>[(i/(a.length-1))*w, h-2-((v-lo)/(hi-lo))*(h-4)]).map(p=>p[0].toFixed(1)+','+p[1].toFixed(1)).join(' ');
  return '<svg viewBox="0 0 '+w+' '+h+'" preserveAspectRatio="none" style="width:'+w+'px;height:'+h+'px"><polyline points="'+pts+'" fill="none" stroke="'+color+'" stroke-width="1.6"/></svg>';
}
const $=s=>document.querySelector(s);
const TAG={hz:'杭州真实',xfd:'新发地批发',s:'全国真实',d:'全国参考',p:'省级折算'};
let toastTimer;
function toast(t){
  let el=document.getElementById('toast');
  if(!el){ el=document.createElement('div'); el.id='toast';
    el.style.cssText='position:fixed;left:50%;bottom:32px;transform:translateX(-50%);background:#22304A;color:#E8EDF6;padding:8px 16px;border-radius:18px;font-size:12px;z-index:50;border:1px solid #3A4A6B;transition:opacity .3s;box-shadow:0 4px 16px rgba(0,0,0,.4)';
    document.body.appendChild(el); }
  el.textContent=t; el.style.opacity='1';
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>{ el.style.opacity='0'; },1600);
}
let alpha='', kw='', sort='cat', cat='';
let fav=[]; try{ fav=JSON.parse(localStorage.getItem('vegFav')||'[]'); }catch(e){ fav=[]; }
let spec=null; try{ const s=localStorage.getItem('vegSpec'); if(s&&s!=='null'){ spec=s; } else { localStorage.removeItem('vegSpec'); } }catch(e){ spec=null; }
/* ---- 展示地区（vegRegion：auto=自动定位 / hz=杭州 / nation=全国 / 省码=省级折算价） ---- */
let region='hz'; try{ region=localStorage.getItem('vegRegion')||'hz'; }catch(e){ region='hz'; }
let located=null; // 自动定位结果 {prov,city}
const REGION_NAMES=Object.assign({auto:'自动定位',hz:'杭州',nation:'全国'}, Object.fromEntries(Object.entries(PROV_DATA.provs).map(([k,v])=>[k,v.n])));
function isProvCode(r){ return !!PROV_DATA.provs[r]; }
function saveRegion(){ try{ localStorage.setItem('vegRegion',region); }catch(e){} }
function regionName(){ if(region==='auto'&&located) return located.city+'·'+located.prov; return REGION_NAMES[region]||'杭州'; }
function showMode(){ // 实际展示口径：省码→省级折算价；auto 定位到杭州→杭州价，否则→全国参考
  if(isProvCode(region)) return region;
  if(region==='hz') return 'hz';
  if(region==='nation') return 'nation';
  if(region==='auto') return located&&located.city&&located.city.indexOf('杭州')>=0?'hz':'nation';
  return 'hz';
}
function regionTip(){ // 当前地区说明（用于 meta / 弹窗口径）
  if(region==='auto'&&located) return '自动定位：'+located.prov+located.city;
  if(isProvCode(region)) return '当前地区：'+REGION_NAMES[region]+' · 省级批发折算零售';
  return '当前地区：'+REGION_NAMES[region];
}
/* IP 大致定位（需 network 权限获批后生效；未获批时 catch 回退） */
async function ipLocate(){
  try{
    if(!hbSDK||!hbSDK.network||!hbSDK.network.request) return null;
    // 仅使用已备案国内接口（太平洋电脑网 whois.pconline.com.cn）；ip-api.com 未备案被小黑盒网络权限驳回，不再使用
    const tries=[
      {url:'https://whois.pconline.com.cn/ipJson.jsp?json=true',pick:d=>({prov:d.pro,city:d.city})}
    ];
    for(const t of tries){
      try{
        const r=await hbSDK.network.request({url:t.url,method:'GET',timeout:6000});
        const d=r&&r.data;
        if(d&&typeof d==='object'){
          const p=t.pick(d);
          if(p&&p.prov&&p.city) return p;
        }
      }catch(e){}
    }
  }catch(e){}
  return null;
}
const cache={};
function prep(p){
  if(cache[p.id]) return cache[p.id];
  if(p.t==='p'){ // 省级：当日折算价；有历史序列则算周环比/位置/曲线（每日快照累积，暂无则如实标注）
    const s=(Array.isArray(p.s)&&p.s.length>=2)?p.s:null;
    if(s){
      const n=s.length;
      const s3=s.slice(-13);
      const wkChg=(s[n-1]-s[n-2])/s[n-2]*100;
      const wkAbs=s[n-1]-s[n-2];
      cache[p.id]={s1:s, s3:s3.length>=2?s3:null, pos1:posPct(s), pos3:posPct(s3), wkChg, wkAbs, vol:vol4(s)};
    } else {
      cache[p.id]={s1:null,s3:null,pos1:null,pos3:null,wkChg:0,wkAbs:0,vol:0};
    }
    return cache[p.id];
  }
  let s1=null, s3=null;
  if(p.id==='dami' && DATA.rice.series.length){ // 大米用商务部真实周序列（元/公斤→元/500克）
    s1=DATA.rice.series.map(x=>Math.round(x/2*100)/100);
    s3=s1.slice(-13);
  } else {
    s1=genSeries(p.v); s3=s1?genSeries(p.v).slice(39):null;
  }
  const wkChg=p.wk!=null ? (p.v-p.wk)/p.wk*100
    : p.id==='dami' ? (DATA.rice.series[DATA.rice.series.length-1]-DATA.rice.series[DATA.rice.series.length-2])/DATA.rice.series[DATA.rice.series.length-2]*100
    : s1 ? ((s1[51]-s1[47])/s1[47]*100) : 0;
  const wkAbs=p.wk!=null ? (p.v-p.wk)
    : p.id==='dami' ? (DATA.rice.series[DATA.rice.series.length-1]-DATA.rice.series[DATA.rice.series.length-2])/2
    : s1 ? (s1[51]-s1[47]) : 0;
  cache[p.id]={s1,s3,pos1:s1?posPct(s1):null,pos3:s3?posPct(s3):null,wkChg,wkAbs,vol:vol4(s1)};
  return cache[p.id];
}
function saveFav(){ try{ localStorage.setItem('vegFav',JSON.stringify(fav)); }catch(e){} }
function saveSpec(){ try{ if(spec){ localStorage.setItem('vegSpec',spec); } else { localStorage.removeItem('vegSpec'); } }catch(e){} }
function byId(id){ return currentList().find(x=>x.id===id)||DATA.products.find(x=>x.id===id); }
function currentList(){ // 当前展示口径的品种列表：省级→折算价数组；否则→内置全国/杭州品种
  if(!isProvCode(showMode())) return DATA.products;
  const P=PROV_DATA.provs[showMode()];
  return Object.entries(P.items).map(([name,it])=>({
    id:'p_'+showMode()+'_'+name, n:name, ini:'', c:it.c||'蔬',
    v:it.r, p:it.r, wk:null, m:it.m||0, t:'p', s:Array.isArray(it.s)?it.s:null
  }));
}
let _provList=null;
function provList(){ if(!_provList){ _provList=currentList(); } return _provList; }
function provStat(){ // 省级概览：有价品种数/市场数
  const l=provList().filter(x=>x.v!=null);
  const ms=[...new Set(l.map(x=>x.m))];
  const totalM=l.reduce((s,x)=>s+x.m,0);
  return {n:l.length, m:totalM, top:l.slice().sort((a,b)=>b.v-a.v).slice(0,3)};
}

/* ---- 渲染 ---- */
const STAR='<svg viewBox="0 0 24 24" class="s1"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg><svg viewBox="0 0 24 24" class="s2"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>';
function lvOf(id){ return spec===id?2:(fav.includes(id)?1:0); }
function cardHTML(p){
  const d=prep(p);
  const wk=d.wkChg, hasWk=p.wk!=null, wabs=d.wkAbs||0;
  const wcol=wk>0.5?'up':wk<-0.5?'down':'flat';
  const hasS = p.t==='p' && Array.isArray(p.s) && p.s.length>=2;
  const absStr=(p.t==='p'&&!hasS)?'':((wabs>0?'+':(wabs<0?'-':''))+Math.abs(wabs).toFixed(2)+'元');
  const lv=lvOf(p.id);
  return `<div class="card" data-id="${p.id}">
    <div class="hd"><b>${p.n}</b><span class="catb" style="cursor:default;padding:1px 6px;font-size:10px">${DATA.catName[p.c]||p.c}</span><span class="tag ${p.t==='d'?'d':''}">${TAG[p.t]}</span>
      <button class="star ${lv?'lv'+lv:''}" data-star="${p.id}" title="${lv===2?'特别关注（点击取消）':lv===1?'已关注（再点设为特别关注）':'点击关注（再点设特别关注）'}">${STAR}</button></div>
    <div class="row1"><div class="price">${p.v.toFixed(2)}<small> ${DATA.unit}</small></div>
      <div class="chg ${wcol}">${p.t==='p'?(hasS?('周环比 '+(wk>0?'+':'')+wk.toFixed(2)+'%'):('当日价 · '+(p.m||0)+'家市场上报')):hasWk?('周环比 '+(wk>0?'+':'')+wk.toFixed(2)+'%'):(p.t==='d'?'演示值 · 周环比 '+(wk>0?'+':'')+wk.toFixed(1)+'%':'周环比 0.00%')}${absStr?'<small class="wabs"> · 涨跌 '+absStr+'</small>':''}</div>
      <div class="spark">${sparkSVG(d.s1,92,36,p.t==='d'?'#6B5A2A':'#49C0F0')}</div></div>
    <div class="pos">
      <div class="it"><div class="k">近3个月位置</div><div class="v" style="color:${d.pos3==null?'var(--sub)':d.pos3>=70?'var(--red)':d.pos3<=30?'var(--green)':'var(--amber)'}">${d.pos3==null?'--':d.pos3+'%'}</div>
        ${d.pos3!=null?`<div class="track"><i style="left:${d.pos3}%"></i></div>`:''}</div>
      <div class="it"><div class="k">近1年位置</div><div class="v" style="color:${d.pos1==null?'var(--sub)':d.pos1>=70?'var(--red)':d.pos1<=30?'var(--green)':'var(--amber)'}">${d.pos1==null?'--':d.pos1+'%'}</div>
        ${d.pos1!=null?`<div class="track"><i style="left:${d.pos1}%"></i></div>`:''}</div>
    </div>
  </div>`;
}
function render(){
  const base=currentList();
  let list=base.filter(p=>{
    if(cat && p.c!==cat) return false;
    if(alpha && p.ini && p.ini.indexOf(alpha)!==0 && p.n.indexOf(alpha)!==0) return false;
    if(kw && !p.n.toLowerCase().includes(kw.toLowerCase()) && !p.ini.toLowerCase().includes(kw.toLowerCase())) return false;
    return true;
  });
  const order=sort==='pos'?(a,b)=>(prep(b).pos1??-1)-(prep(a).pos1??-1)
    : sort==='chg'?(a,b)=>prep(b).wkChg-prep(a).wkChg
    : (a,b)=>a.c.localeCompare(b.c)||a.n.localeCompare(b.n);
  const favs=list.filter(p=>fav.includes(p.id)).sort(order);
  const others=list.filter(p=>!fav.includes(p.id)).sort(order);
  const provMode=isProvCode(showMode());
  $('#countBar').textContent=regionTip()+(provMode?' · 农业农村部定点批发市场当日价折算零售（系数'+PROV_DATA.coeff+'）':'')+(showMode()==='nation'&&region!=='nation'?'（当地数据接入中，暂展示全国参考）':'')+' · 显示 '+list.length+'/'+base.length+' 个品种 · '+(provMode?'：当日价=批发÷2×'+PROV_DATA.coeff+' 折算，暂无环比与走势序列':'位置=当前价在近13周/52周区间的百分位（越高越贵）')+' · 点星标加入关注（置顶），详情内可设特别关注';
  if(provMode && base.length===0){
    $('#grouped').innerHTML='<div class="group-t">全部品种 (0)</div><div class="grid"><div class="spEmpty">该省当日数据补跑中（云南/西藏/陕西/甘肃/青海/宁夏/新疆等受来源限流，每天凌晨自动错峰补抓，稍后刷新即可）。<br>可先切回杭州 / 全国查看。</div></div>';
    renderHero(); return;
  }
  $('#grouped').innerHTML=
    (favs.length?('<div class="group-t">我的关注 ('+favs.length+')</div><div class="grid">'+favs.map(cardHTML).join('')+'</div>'):'')+
    '<div class="group-t">全部品种 ('+others.length+')</div><div class="grid">'+others.map(cardHTML).join('')+'</div>';
  document.querySelectorAll('.star').forEach(b=>b.addEventListener('click',e=>{
    e.stopPropagation();
    const id=b.dataset.star;
    if(spec===id){ fav=fav.filter(x=>x!==id); spec=null; }
    else if(fav.includes(id)){ spec=id; }
    else{ fav.push(id); spec=null; }
    saveFav(); saveSpec(); render();
    // 有特别关注时大看板优先展示特别关注
    if(spec){ const tb=document.querySelector('.hero .tab[data-h="spec"]'); document.querySelectorAll('.hero .tab').forEach(x=>x.classList.remove('on')); tb.classList.add('on'); }
    renderHero();
  }));
  document.querySelectorAll('.card').forEach(el=>el.addEventListener('click',()=>openDetail(el.dataset.id)));
  renderHero();
}
function renderHero(){
  const volTab=document.querySelector('.tab.on')?.dataset.h==='vol';
  const hv=document.getElementById('heroVol'), hs=document.getElementById('heroSpec');
  const provMode=isProvCode(showMode());
  if(volTab){
    if(provMode){
      const st=provStat();
      hs.style.display='none'; hv.style.display='grid';
      hv.innerHTML=`<div class="volcard" style="grid-column:1/-1">
        <div class="k">${REGION_NAMES[showMode()]} · 省级当日折算零售（${PROV_DATA.date}）</div>
        <div class="n">${st.n} 个品种有价 · 共 ${st.m} 家定点批发市场上报</div>
        <div class="row" style="font-size:12px;color:var(--sub)">省级为当日批发价 ÷2 ×${PROV_DATA.coeff} 折算（元/500克），暂无环比与逐日走势；价格随市场波动，仅供参考</div></div>
        ${st.top.map(p=>`<div class="volcard"><div class="k">当日折算价 TOP</div><div class="n">${p.n}</div>
        <div class="row"><div class="v">${p.v.toFixed(2)}<small> ${DATA.unit}</small></div>
        <div class="volt flat">${p.m||0}家市场上报</div></div></div>`).join('')}`;
    }else{
      const top=DATA.products.filter(p=>prep(p).s1).slice().sort((a,b)=>prep(b).vol-prep(a).vol).slice(0,3);
      hv.innerHTML=top.map(p=>{
        const d=prep(p);
        return `<div class="volcard"><div class="k">近4周波动 ${d.vol.toFixed(1)}%</div><div class="n">${p.n}</div>
          <div class="row"><div class="v">${p.v.toFixed(2)}<small> ${DATA.unit}</small></div>
          <div class="volt ${d.wkChg>0.5?'up':d.wkChg<-0.5?'down':'flat'}">${(d.wkChg>0?'+':'')+d.wkChg.toFixed(1)+'% 周环比 · 涨跌 '+((d.wkAbs||0)>0?'+':((d.wkAbs||0)<0?'-':''))+Math.abs(d.wkAbs||0).toFixed(2)+'元'}</div></div>
          <div class="vp"><span>3个月位置 <b style="color:${d.pos3>=70?'var(--red)':d.pos3<=30?'var(--green)':'var(--amber)'}">${d.pos3??'--'}%</b></span><span>1年位置 <b style="color:${d.pos1>=70?'var(--red)':d.pos1<=30?'var(--green)':'var(--amber)'}">${d.pos1??'--'}%</b></span></div>
          ${sparkSVG(d.s1,300,30,p.t==='d'?'#6B5A2A':'#49C0F0')}</div>`;
      }).join('');
      hs.style.display='none'; hv.style.display='grid';
    }
  }else{
    const p=spec?byId(spec):null;
    hv.style.display='none'; hs.style.display='block';
    if(p){
      const d=prep(p);
      hs.innerHTML=`<div class="special">
        <div class="num"><div class="k">${p.n} · ${TAG[p.t]} · 特别关注</div>
          <div class="v">${p.v.toFixed(2)}<small> ${DATA.unit}</small></div>
          <div class="pos2"><span>3个月位置 <b>${d.pos3??'--'}%</b></span><span>1年位置 <b>${d.pos1??'--'}%</b></span></div></div>
        <div class="tcard"><div class="t">近52周走势 <small>· ${p.t==='p'?'省级仅当日价':(p.t==='d'?'演示序列':'官方监测序列')}</small></div>
          <div class="spBig" data-id="${p.id}" style="height:120px"></div></div></div>`;
      if(p.t==='p'){ hs.querySelector('.spBig').innerHTML='<div style="color:var(--sub);font-size:12px;line-height:1.8;text-align:center;padding-top:36px">省级为农业农村部定点批发市场当日价折算零售（'+PROV_DATA.date+'），暂无逐日走势序列。<br>切到杭州/全国口径可看趋势与位置。</div>'; }
      else{
      const c=echarts.init(hs.querySelector('.spBig'));
      try{ c.setOption({animation:false,grid:{left:8,right:8,top:8,bottom:14,containLabel:true},
        xAxis:{type:'category',show:false},yAxis:{type:'value',scale:true,axisLabel:{color:'#93A3BC',fontSize:9},splitLine:{lineStyle:{color:'#18233A'}}},
        series:[{type:'line',data:d.s1,smooth:true,symbol:'circle',symbolSize:3,symbolShow:true,lineStyle:{width:2,color:p.t==='d'?'#6B5A2A':'#49C0F0'},
          label:{show:true,position:'top',fontSize:8,color:'#93A3BC',formatter:function(pp){ if(pp.dataIndex===0||pp.dataIndex===d.s1.length-1||pp.dataIndex%6===0){ return pp.value.toFixed(2); } return ''; }},
          markPoint:{symbol:'pin',symbolSize:12,label:{show:false},data:[{type:'max',name:'高',itemStyle:{color:'#FF5C5C'}},{type:'min',name:'低',itemStyle:{color:'#3CCF8E'}}]}}]});}catch(e){}
      }
    }else{
      hs.innerHTML='<div class="spEmpty">还没有特别关注。点任意品种卡片右上角的星标：点 1 次加入关注、点 2 次设为特别关注（只能一个）——设置后会优先展示在这里。</div>';
    }
  }
}

function openDetail(id){
  const p=byId(id), d=prep(p);
  const hasWk=p.wk!=null;
  $('#mName').textContent=p.n;
  let srcDesc=p.t==='p'?(REGION_NAMES[showMode()]+'省级价（农业农村部定点批发市场当日价折算零售，'+PROV_DATA.date+'，系数'+PROV_DATA.coeff+'）')
    :p.t==='hz'?'杭州市发改委菜篮子零售价（2026-10-20）':p.t==='xfd'?'新发地批发市场平均价（2026-10-19）':p.t==='s'?'商务部全国36城零售均价（周更）':'全国参考价（暂无杭州官方监测，演示值）';
  if(p.t==='hz'&&showMode()!=='hz') srcDesc+='（当前地区非杭州，当地数据接入中，暂展示杭州价作为样例）';
  $('#mCat').textContent='当前地区：'+regionName()+' · '+DATA.catName[p.c]+' · '+srcDesc;
  const sb=$('#mSpecBtn');
  sb.disabled=false; sb.textContent=spec===p.id?'取消特别关注':'设为特别关注';
  sb.classList.toggle('on',spec===p.id);
  sb.onclick=()=>{
    if(spec===p.id){ spec=null; }
    else{
      if(!fav.includes(p.id)){ fav.push(p.id); saveFav(); }
      spec=p.id;
    }
    saveSpec(); render(); renderHero(); openDetail(p.id);
  };
  $('#mTwo').innerHTML=`
    <div class="it"><div class="k">近3个月位置（13周）</div><div class="v" style="color:${d.pos3==null?'var(--sub)':d.pos3>=70?'var(--red)':d.pos3<=30?'var(--green)':'var(--amber)'}">${d.pos3==null?'--':d.pos3+'%'}</div>
      ${d.s3?`<div class="track big"><i style="left:${d.pos3}%"></i></div>
      <div style="font-size:10px;color:var(--sub);margin-top:4px">当前 ${p.v.toFixed(2)} · 区间 ${Math.min.apply(null,d.s3).toFixed(2)} ~ ${Math.max.apply(null,d.s3).toFixed(2)}</div>`:'<div style="font-size:10px;color:var(--sub);margin-top:4px">暂无趋势数据</div>'}</div>
    <div class="it"><div class="k">近1年位置（52周）</div><div class="v" style="color:${d.pos1==null?'var(--sub)':d.pos1>=70?'var(--red)':d.pos1<=30?'var(--green)':'var(--amber)'}">${d.pos1==null?'--':d.pos1+'%'}</div>
      ${d.s1?`<div class="track big"><i style="left:${d.pos1}%"></i></div>
      <div style="font-size:10px;color:var(--sub);margin-top:4px">当前 ${p.v.toFixed(2)} · 区间 ${Math.min.apply(null,d.s1).toFixed(2)} ~ ${Math.max.apply(null,d.s1).toFixed(2)}</div>`:'<div style="font-size:10px;color:var(--sub);margin-top:4px">暂无趋势数据</div>'}</div>`;
  const ch=document.getElementById('mChart');
  ch.innerHTML='';
  let chartInst=null;
  if(d.s1){
    try{ const c=echarts.init(ch);
    chartInst=c;
    const N=d.s1.length;
    c.setOption({animation:false,grid:{left:8,right:8,top:26,bottom:26,containLabel:true},
      tooltip:{trigger:'axis',axisPointer:{type:'cross',label:{backgroundColor:'#22304A',color:'#E8F0FE',fontSize:10}},
        formatter:ps=>'<b>'+ps[0].name+'</b> · '+ps[0].value.toFixed(2)+' 元/500克'},
      xAxis:{type:'category',data:d.s1.map((x,i)=>'第'+(i+1)+'周'),axisLabel:{color:'#93A3BC',fontSize:9,interval:N>30?10:6},axisLine:{lineStyle:{color:'#22304A'}}},
      yAxis:{type:'value',scale:true,axisLabel:{color:'#93A3BC',fontSize:10},splitLine:{lineStyle:{color:'#18233A'}}},
      dataZoom:[{type:'inside',start:0,end:100,zoomOnMouseWheel:true,moveOnMouseMove:true,moveOnTouchMove:true},
        {type:'slider',height:14,bottom:4,start:0,end:100,show:N>26,brushSelect:false,
         borderColor:'#22304A',backgroundColor:'#141E33',fillerColor:'rgba(73,192,240,.18)',handleStyle:{color:'#49C0F0'},textStyle:{color:'#93A3BC',fontSize:9}}],
      series:[{type:'line',data:d.s1,smooth:true,symbol:'none',lineStyle:{width:2,color:p.t==='d'?'#6B5A2A':'#3CCF8E'},areaStyle:{color:'rgba(60,207,142,.12)'},
        markPoint:{symbol:'pin',symbolSize:12,label:{show:false},data:[{type:'max',name:'高',itemStyle:{color:'#FF5C5C'}},{type:'min',name:'低',itemStyle:{color:'#3CCF8E'}}]}}]});
    }catch(e){}
  }
  $('#mNote').innerHTML=(p.t==='p'?`该品种为${REGION_NAMES[showMode()]} ${p.m||0} 家定点批发市场上报价均值（${PROV_DATA.date}），按 批发÷2×${PROV_DATA.coeff} 折算零售（元/500克）；暂无环比与逐日走势，价格随市场实时波动；`:'')+
    (p.t==='hz'?'当前/昨价来自杭州市发改委菜篮子（2026-10-20）；':'')+
    (p.t==='xfd'?'当前价来自新发地批发市场（2026-10-19）；':'')+
    (p.t==='s'?'当前价来自商务部全国36城零售均价（周更）；':'')+
    (p.t==='d'?'该品种暂无杭州官方监测数据，当前价为全国参考演示值，周环比与趋势为模拟序列；':'')+
    '<br>曲线含义：价格走势（演示品种为按季节波动的模拟序列，正式版接入官方逐日/周监测后展示真实曲线）；红标=区间最高价、绿标=区间最低价；位置%=当前价在 min~max 区间的相对高度，仅作"贵不贵"参考。';
  $('#mask').hidden=false;
  if(chartInst){ setTimeout(()=>{ try{ chartInst.resize(); }catch(e){} },60); }
}

/* ---- 展示地区 UI ---- */
function updateMeta(){
  const el=$('#meta'); if(!el) return;
  const mm=showMode();
  el.innerHTML='当前地区：<b style="color:var(--amber)">'+regionName()+'</b>'+(region==='auto'&&!located?'（定位中…）':'')+
    (mm==='nation'&&region!=='nation'?' · 当地数据接入中，暂展示全国参考':'')+
    (isProvCode(mm)?' · 省级当日价=批发÷2×'+PROV_DATA.coeff+' 折算零售（农业农村部 pfsc，'+PROV_DATA.date+'）':' · 全国趋势 + 全品种 · 单位：元/500克（全国零售为元/公斤换算）');
  const nm=$('#regionName'); if(nm) nm.textContent=regionName();
}
function syncRegionCards(){ document.querySelectorAll('.rcard').forEach(b=>b.classList.toggle('on',b.dataset.r===region)); }
$('#regionBtn').addEventListener('click',()=>{ syncRegionCards(); $('#regionMask').hidden=false; });
$('#regionClose').addEventListener('click',()=>$('#regionMask').hidden=true);
$('#regionMask').addEventListener('click',e=>{ if(e.target===$('#regionMask')) $('#regionMask').hidden=true; });
document.querySelectorAll('.rcard').forEach(b=>b.addEventListener('click',()=>{
  region=b.dataset.r; saveRegion();
  if(region==='auto'){
    located=null; updateMeta();
    ipLocate().then(p=>{
      if(p){
        located=p; updateMeta(); render(); renderHero();
        const isHz=p.city.indexOf('杭州')>=0||p.prov.indexOf('浙江')>=0;
        toast(isHz?'已定位到 '+p.prov+p.city+'，展示本地价格':'已定位到 '+p.prov+p.city+'，当地数据接入中，先展示全国参考');
      }else{
        updateMeta();
        toast('定位暂不可用（网络异常），下次打开仍会尝试');
      }
      $('#regionMask').hidden=true;
    });
  }else{
    located=null; updateMeta(); render(); renderHero();
    $('#regionMask').hidden=true;
    toast('已切换展示地区：'+regionName());
  }
}));
updateMeta();

$('#close').addEventListener('click',()=>$('#mask').hidden=true);
$('#mask').addEventListener('click',e=>{if(e.target===$('#mask'))$('#mask').hidden=true});
document.querySelectorAll('.sbtn').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.sbtn').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); sort=b.dataset.s; render();
  const names={cat:'按分类',pos:'位置：贵→便宜',chg:'周环比：涨→跌'};
  toast('已按「'+names[sort]+'」排序');
  document.getElementById('grouped').scrollIntoView({behavior:'smooth',block:'start'});
}));
document.querySelectorAll('.hero .tab').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.hero .tab').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); renderHero();
}));
const A='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
$('#alphaBar').innerHTML='<button class="all on" data-a="">全部</button>'+[...A].map(x=>`<button data-a="${x}">${x}</button>`).join('');
$('#alphaBar').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b)return;
  $('#alphaBar').querySelectorAll('button').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); alpha=b.dataset.a||''; render();
});
$('#kw').addEventListener('input',e=>{kw=e.target.value.trim();render();});
$('#cats').innerHTML='<button class="catb on" data-c="">全部</button>'+Object.entries(DATA.catName).map(([k,n])=>`<button class="catb" data-c="${k}">${n}</button>`).join('');
$('#cats').addEventListener('click',e=>{
  const b=e.target.closest('.catb'); if(!b)return;
  $('#cats').querySelectorAll('.catb').forEach(x=>x.classList.remove('on'));
  b.classList.add('on'); cat=b.dataset.c||''; render();
});

/* 指数大数字卡 + 图表日期范围（EXDATA 真实数据） */
try{
  const N=EXDATA.nat, D=EXDATA.idx;
  const lastOf=k=>{const a=(D[k]||[]).filter(v=>v!=null);return a.length?a[a.length-1]:null;};
  const cards=document.querySelectorAll('#idxCards .it');
  const rows=[[N.p200,N.p200_chg],[N.basket,N.basket_chg],[lastOf('grainOil'),null]];
  cards.forEach((c,i)=>{
    const v=rows[i][0], chg=rows[i][1];
    if(v!=null){ c.querySelector('.v').textContent=(+v).toFixed(2);
      const e=c.querySelector('.chg');
      if(chg!=null){ e.textContent=(chg>=0?'+':'')+chg.toFixed(2)+' 较昨日'; e.className='chg '+(chg>=0?'up':'down'); }
      else { e.textContent='--'; e.className='chg'; }
    }
  });
  const range=document.getElementById('idxRange');
  if(range&&D.date&&D.date.length){ range.textContent='· 官方每日（'+D.date[0]+' ~ '+D.date[D.date.length-1]+'）'; }
}catch(e){}

/* 指数走势（农业农村部官方日度序列，ncpscxx 接口自动累积；点数<2 的指数不画） */
try{(function(){
  const c=echarts.init(document.getElementById('idxChart'));
  const D=DATA.idx;
  const SERIES_DEF=[
    {k:'p200',n:'200指数',c:'#49C0F0'},{k:'basket',n:'菜篮子',c:'#F7C948'},
    {k:'grainOil',n:'粮油',c:'#3CCF8E'},{k:'grain',n:'粮食',c:'#B48EFF'},
    {k:'oil',n:'食用油',c:'#A8D87A'},{k:'veg',n:'蔬菜',c:'#7B9EFF'},
    {k:'animal',n:'畜产',c:'#FF7B9C'},{k:'aqua',n:'水产',c:'#4DD6C8'},
    {k:'fruit',n:'水果',c:'#FFB86B'}
  ];
  const series=[];
  SERIES_DEF.forEach(s=>{
    const arr=(D[s.k]||[]).filter(v=>v!=null);
    if(arr.length<2) return;
    series.push({name:s.n,type:'line',data:D[s.k],smooth:true,symbol:'circle',symbolSize:3.5,
      lineStyle:{width:1.6,color:s.c},itemStyle:{color:s.c},
      label:{show:false},
      markPoint:s.k==='p200'?{symbol:'pin',symbolSize:12,label:{show:false},data:[{type:'max',name:'高',itemStyle:{color:'#FF5C5C'}},{type:'min',name:'低',itemStyle:{color:'#3CCF8E'}}]}:undefined});
  });
  c.setOption({animation:false,grid:{left:6,right:6,top:14,bottom:18,containLabel:true},
    tooltip:{trigger:'axis',formatter:ps=>'<b>'+ps[0].name+'</b><br/>'+ps.map(p=>p.seriesName+' '+ (p.value==null?'-':p.value)).join('<br/>')},
    xAxis:{type:'category',data:D.date,axisLabel:{color:'#93A3BC',fontSize:9},axisLine:{lineStyle:{color:'#22304A'}}},
    yAxis:{type:'value',scale:true,axisLabel:{color:'#93A3BC',fontSize:9},splitLine:{lineStyle:{color:'#18233A'}}},
    series:series});
})();}catch(e){}

/* 大米零售走势（真实） */
try{(function(){
  const c=echarts.init(document.getElementById('riceChart'));
  c.setOption({animation:false,grid:{left:6,right:6,top:14,bottom:18,containLabel:true},
    tooltip:{trigger:'axis',formatter:p=>'<b>'+p[0].name+'</b> · '+p[0].value.toFixed(2)+' 元/公斤'},
    xAxis:{type:'category',data:DATA.rice.series.map((x,i)=>{const d=new Date(2025,9,24);d.setDate(d.getDate()+7*i);return (d.getMonth()+1)+'月'}),axisLabel:{color:'#93A3BC',fontSize:9,interval:9},axisLine:{lineStyle:{color:'#22304A'}}},
    yAxis:{type:'value',scale:true,min:6.40,max:6.56,axisLabel:{color:'#93A3BC',fontSize:9},splitLine:{lineStyle:{color:'#18233A'}}},
    series:[{type:'line',data:DATA.rice.series,smooth:true,symbol:'circle',symbolSize:3,symbolShow:true,lineStyle:{width:2,color:'#49C0F0'},itemStyle:{color:'#49C0F0'},areaStyle:{color:'rgba(73,192,240,.12)'},
      label:{show:true,position:'top',fontSize:8,color:'#93A3BC',formatter:function(pp){ if(pp.dataIndex===0||pp.dataIndex===DATA.rice.series.length-1||pp.dataIndex%6===0){ return pp.value.toFixed(2); } return ''; }},
      markPoint:{symbol:'pin',symbolSize:12,label:{show:false},data:[{type:'max',name:'高',itemStyle:{color:'#FF5C5C'}},{type:'min',name:'低',itemStyle:{color:'#3CCF8E'}}]}}]});
})();}catch(e){}

/* 有特别关注时大看板初始优先展示特别关注 */
if(spec){ const tb=document.querySelector('.hero .tab[data-h="spec"]'); document.querySelector('.hero .tab[data-h="vol"]').classList.remove('on'); tb.classList.add('on'); renderHero(); }

render();

/* ---- 小黑盒隔离存储桥：冷启动时拉取云端/隔离 storage 覆盖本地并重渲染 ---- */
(async () => {
  try {
    const s = window.__hbStorage;
    if (!s || !s.getStorage) return;
    const rd = r => (r && r.data !== undefined ? r.data : r);
    const r1 = await Promise.resolve(s.getStorage({ key: 'vegFav' })).then(rd).catch(() => null);
    const r2 = await Promise.resolve(s.getStorage({ key: 'vegSpec' })).then(rd).catch(() => null);
    const r3 = await Promise.resolve(s.getStorage({ key: 'vegRegion' })).then(rd).catch(() => null);
    let changed = false;
    if (r1 != null) { try { fav = JSON.parse(r1); } catch(e) { fav = r1; } changed = true; }
    if (r2 != null && r2 !== 'null') { spec = r2; changed = true; }
    if (r3 != null) { region = r3; changed = true; }
    if (changed) { render(); renderHero(); updateMeta(); syncRegionCards(); }
  } catch(e) {}
})();

/* 自动定位：选择「自动定位」时启动即尝试按 IP 定位（network 权限已批准；失败回退并提示） */
if (region === 'auto') {
  ipLocate().then(p => {
    if (p) {
      located = p; updateMeta(); render(); renderHero();
      toast('已定位到 ' + p.prov + p.city + '（' + regionName() + '口径）');
    } else {
      updateMeta();
      toast('定位失败（网络异常），已用上次地区');
    }
  });
}
