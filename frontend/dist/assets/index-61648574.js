import{_ as S,r as s,i as n,j as $,o as i,q as u,w as e,k as t,a as c,l as A,c as E,y as I,F as T,x as U,A as q,t as z,C as J,G as H}from"./index-1aea0b7d.js";import{g as h}from"./group-83d1f4e6.js";const K=["src"],M={style:{height:"100%",display:"flex","flex-direction":"column","justify-content":"center","align-items":"flex-start"}},O={class:"text"},P={__name:"index",setup(Q){const r=s(""),p=s([]),_=s(!1),f=s(!1),y=s(!1),v=s(!1),g=()=>{if(r.value===""){q("Enter");return}h.SelectGroup({kw:r.value}).then(l=>{l.code===200&&(p.value=[l.data],v.value=!0,_.value=!1,f.value=!0,y.value=!1)})},k=l=>{h.JoinGroup({id:l}).then(o=>{o.code===200&&(J(o.msg),H.push({name:"Friend"}))})};return(l,o)=>{const x=n("van-icon"),m=n("el-col"),w=n("van-search"),C=n("el-row"),F=n("el-header"),d=n("van-col"),b=n("van-button"),V=n("van-row"),B=n("van-cell"),j=n("van-list"),D=n("el-main"),G=n("el-container"),L=$("autofocus");return i(),u(G,null,{default:e(()=>[t(F,null,{default:e(()=>[c("div",null,[t(C,null,{default:e(()=>[t(m,{span:2},{default:e(()=>[c("div",{class:"left-back",onClick:o[0]||(o[0]=a=>l.$router.back())},[t(x,{name:"arrow-left",size:"20"})])]),_:1}),t(m,{span:22},{default:e(()=>[A((i(),u(w,{modelValue:r.value,"onUpdate:modelValue":o[1]||(o[1]=a=>r.value=a),"show-action":"",placeholder:"Group ID, name"},{action:e(()=>[c("div",{style:{color:"#FFFFFF"},onClick:g},"search")]),_:1},8,["modelValue"])),[[L]])]),_:1})]),_:1})])]),_:1}),t(D,null,{default:e(()=>[v.value?(i(),u(j,{key:0,loading:_.value,"onUpdate:loading":o[2]||(o[2]=a=>_.value=a),finished:f.value,"finished-text":"No more...",onLoad:l.onLoad},{default:e(()=>[(i(!0),E(T,null,I(p.value,(a,N)=>(i(),u(B,{key:N,onClick:R=>k(a.id)},{default:e(()=>[t(V,{gutter:"10"},{default:e(()=>[t(d,{span:"6",style:{display:"flex","align-items":"center","justify-content":"center"}},{default:e(()=>[c("img",{src:a.avatar,alt:""},null,8,K)]),_:2},1024),t(d,{span:"12"},{default:e(()=>[c("div",M,[c("span",O,z(a.name),1)])]),_:2},1024),t(d,{span:"6",style:{display:"flex","align-items":"center","justify-content":"center"}},{default:e(()=>[t(b,{icon:"plus",type:"primary",round:""})]),_:1})]),_:2},1024)]),_:2},1032,["onClick"]))),128))]),_:1},8,["loading","finished","onLoad"])):U("",!0)]),_:1})]),_:1})}}},Y=S(P,[["__scopeId","data-v-4d6f237b"]]);export{Y as default};
