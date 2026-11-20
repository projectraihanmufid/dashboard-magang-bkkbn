export default function({parentElement, data, setTriggerValue}) {
  const ns = "http://www.w3.org/2000/svg";
  const root = parentElement.querySelector(".atlas");
  const svg = root.querySelector("svg");
  const layer = svg.querySelector("g");
  const tip = root.querySelector(".tooltip");
  const legend = root.querySelector(".legend");
  const zoom = root.querySelector(".zoom");
  layer.replaceChildren();
  legend.replaceChildren();
  const full = "0 0 555 390";
  const main = "0 185 397 204";
  svg.setAttribute("viewBox",root.dataset.zoom === "main" ? main : full);
  zoom.textContent = root.dataset.zoom === "main" ? "Seluruh kepulauan" : "Perbesar daratan utama";
  zoom.onclick = () => {
    const inland = root.dataset.zoom !== "main";
    root.dataset.zoom = inland ? "main" : "all";
    svg.setAttribute("viewBox",inland ? main : full);
    zoom.textContent = inland ? "Seluruh kepulauan" : "Perbesar daratan utama";
    tip.hidden = true;
  };
  function line(txt, tag="div") {
    const el = document.createElement(tag);
    el.textContent = txt;
    return el;
  }
  function show(row, ev, shape) {
    tip.replaceChildren(line(row.name,"strong"),line(row.metric),line(row.detail),line(row.priority));
    tip.hidden = false;
    const rect = root.getBoundingClientRect();
    const bounds = shape.getBoundingClientRect();
    const px = ev.clientX || bounds.left+bounds.width/2;
    const py = ev.clientY || bounds.top+bounds.height/2;
    tip.style.left = Math.max(5,Math.min(rect.width-tip.offsetWidth-7,px-rect.left+10))+"px";
    tip.style.top = Math.max(4,Math.min(rect.height-tip.offsetHeight-6,py-rect.top+10))+"px";
  }
  data.rows.forEach(row => {
    const p = document.createElementNS(ns,"path");
    p.setAttribute("d",row.path);
    p.setAttribute("fill",row.color);
    p.setAttribute("fill-rule","evenodd");
    p.setAttribute("stroke",row.focus?"#152635":"#fcfbf4");
    p.setAttribute("stroke-width",row.focus?"1.8":".54");
    p.setAttribute("vector-effect","non-scaling-stroke");
    p.dataset.id=row.id;
    if(row.active) {
      p.classList.add("active");
      p.setAttribute("tabindex","0");
      p.setAttribute("role","button");
      p.setAttribute("aria-label",row.name+". "+row.metric+". Buka detail wilayah");
      p.onpointermove=e=>show(row,e,p);
      p.onfocus=e=>show(row,e,p);
      p.onpointerleave=p.onblur=()=>{tip.hidden=true;};
      p.onclick=()=>{tip.hidden=true;setTriggerValue("picked",row.id);};
      p.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();p.onclick();}};
    } else {p.setAttribute("aria-hidden","true");}
    layer.append(p);
  });
  for(const [label,color] of data.legend) {
    const item=line(label,"span"), swatch=document.createElement("i");
    swatch.style.background=color;item.prepend(swatch);legend.append(item);
  }
  root.querySelector(".legend-title").textContent=data.title;
}
