const $=(id)=>document.getElementById(id);
const activity=[];
const waveform=[];
let activeLat=$("latInput")?.value??"";
let activeLon=$("lonInput")?.value??"";
let burnEnabled=false;
let prevData={};
const canvasEl=$("opencvVideo");
const ctx=canvasEl?canvasEl.getContext("2d"):null;
const vidImg=new Image();
let videoOk=true;
let frameInterval=null;

vidImg.onload=()=>{
  if(!canvasEl||!ctx)return;
  if(canvasEl.width!==vidImg.naturalWidth||canvasEl.height!==vidImg.naturalHeight){
    canvasEl.width=vidImg.naturalWidth;canvasEl.height=vidImg.naturalHeight;
  }
  ctx.drawImage(vidImg,0,0,canvasEl.width,canvasEl.height);
  if(!videoOk){$("hudOverlay").classList.remove("no-video");videoOk=true}
};
vidImg.onerror=()=>{
  videoOk=false;
  const overlay=$("hudOverlay");
  if(overlay)overlay.classList.add("no-video");
  if(ctx){ctx.fillStyle="#111";ctx.fillRect(0,0,canvasEl.width,canvasEl.height)}
};
function startVideo(){frameInterval=setInterval(()=>{vidImg.src="/api/frame?t="+Date.now()},67)}
function stopVideo(){if(frameInterval){clearInterval(frameInterval);frameInterval=null}}

function clamp(value,min,max){return Math.max(min,Math.min(max,value))}
function fmt(value,suffix="",decimals=0){
  if(value===null||value===undefined||value===""||Number.isNaN(Number(value)))return`--${suffix}`;
  return`${Number(value).toFixed(decimals)}${suffix}`;
}
function setWidth(id,value,max=100,min=0){
  const el=$(id);
  if(!el||value===null||value===undefined||Number.isNaN(Number(value)))return;
  const pct=((Number(value)-min)/(max-min))*100;
  el.style.width=`${clamp(pct,0,100)}%`;
}
function setMeterColor(id,value,min,max){
  const el=$(id);
  if(!el)return;
  const pct=clamp((Number(value||0)-min)/(max-min),0,1);
  let c1,c2;
  if(pct<.25){c1="#2aa8ff";c2="rgba(42,168,255,.53)"}
  else if(pct<.5){c1="#00e5ff";c2="rgba(0,229,255,.53)"}
  else if(pct<.75){c1="#43ff73";c2="rgba(67,255,115,.53)"}
  else{c1="#ffcc66";c2="rgba(255,204,102,.53)"}
  el.style.background=`linear-gradient(90deg,${c1},${c2})`;
  el.style.boxShadow=`0 0 8px ${c1}44`;
}
function updateSignalBars(signal){
  const bars=document.querySelectorAll("#signalBars span");
  const active=Math.ceil(clamp(Number(signal||0),0,100)/20);
  bars.forEach((bar,idx)=>{
    bar.style.opacity=idx<active?"1":"0.22";
    bar.style.backgroundColor=idx<2?"#ff4d6d":idx<3?"#ffcc66":"#00e5ff";
  });
}
function statusClass(mode,status){
  if(status==="ERROR")return"error";
  if(mode==="fallback"||mode==="simulated-disabled")return"degraded";
  return"";
}
function flashElement(id){
  const el=$(id);
  if(!el)return;
  el.style.transition="none";
    el.style.textShadow="0 0 20px #00e5ff, 0 0 40px #00e5ff";
  el.style.color="#eefbff";
  setTimeout(()=>{
    el.style.transition="text-shadow .6s ease-out, color .6s ease-out";
    el.style.textShadow="";
    el.style.color="";
  },50);
}
function flashValue(id,newVal){
  if(prevData[id]!==undefined&&prevData[id]!==newVal&&newVal!=="--"){
    flashElement(id);
  }
  prevData[id]=newVal;
}
async function fetchStats(){
  const params=new URLSearchParams();
  if(activeLat!==""&&activeLon!==""){params.set("lat",activeLat);params.set("lon",activeLon)}
  const res=await fetch(`/api/stats?${params.toString()}`,{cache:"no-store"});
  if(!res.ok)throw new Error(`Stats HTTP ${res.status}`);
  return await res.json();
}
function renderStats(data){
  $("dateText").textContent=data.date??"--";
  $("timeText").textContent=data.time??"--:--:--";
  $("locationText").textContent=data.location??"--";
  $("locationTop").textContent=data.location??"--";
  $("statusText").textContent=data.status??"--";
  $("refreshTime").textContent=data.time??"--:--:--";
  const dot=$("statusDot");
  dot.classList.remove("degraded","error");
  const cls=statusClass(data.telemetry_mode,data.status);
  if(cls)dot.classList.add(cls);

  flashValue("humidity",data.humidity);
  flashValue("temperature",data.temperature);
  flashValue("pressure",data.pressure);
  flashValue("fps",data.fps);
  flashValue("signal",data.signal);

  $("humidityText").textContent=fmt(data.humidity,"%",1);
  $("temperatureText").textContent=fmt(data.temperature,"°C",1);
  $("apparentText").textContent=fmt(data.apparent_temperature,"°C",1);
  $("pressureText").textContent=fmt(data.pressure," hPa",0);

  $("cloudText").textContent=fmt(data.cloud_cover,"%",0);
  $("uvText").textContent=fmt(data.uv_index,"",1);
  $("precipText").textContent=fmt(data.precipitation," mm",1);
  $("rainText").textContent=fmt(data.rain," mm",1);

  $("airQualityText").textContent=data.air_quality??"--";
  $("aqiText").textContent=`AQI ${data.us_aqi??"--"}`;
  $("signalText").textContent=fmt(data.signal,"%",0);
  $("fpsText").textContent=fmt(data.fps,"",1);
  $("weatherText").textContent=data.weather??"--";
  $("windText").textContent=data.wind??"--";
  $("windGustText").textContent=fmt(data.wind_gusts," km/h",1);
  $("coordsText").textContent=`LAT ${data.latitude??activeLat} · LON ${data.longitude??activeLon}`;
  $("modeText").textContent=`MODO ${data.telemetry_mode??"--"} · CACHE ${data.cache_age_seconds??"--"}s`;
  $("pm25Text").textContent=fmt(data.pm2_5," µg/m³",1);
  $("pm10Text").textContent=fmt(data.pm10," µg/m³",1);
  $("coText").textContent=fmt(data.co," µg/m³",0);
  $("no2Text").textContent=fmt(data.no2," µg/m³",0);
  $("ozoneText").textContent=fmt(data.ozone," µg/m³",0);

  setWidth("humidityBar",Number(data.humidity??0),100);
  setWidth("temperatureBar",Number(data.temperature??0),45,-5);
  setWidth("pressureBar",Number(data.pressure??0),1050,980);

  setMeterColor("humidityBar",Number(data.humidity??0),0,100);
  setMeterColor("temperatureBar",Number(data.temperature??0),-5,45);
  setMeterColor("pressureBar",Number(data.pressure??0),980,1050);

  updateSignalBars(Number(data.signal??0));
  updateWeatherIcon(data.weather_code??0);

  activity.push(Number(data.cpu??0));
  if(activity.length>42)activity.shift();
  waveform.push(Number(data.latency??0));
  if(waveform.length>64)waveform.shift();

  drawWindCompass("windCanvas",Number(data.wind_direction??0),Number(data.wind_speed??0));
}
function updateWeatherIcon(code){
  const icon=$("weatherIcon");
  if(!icon)return;
  const c=Number(code??0);
  let iconText="◉";
  if(c===0)iconText="☀";
  else if(c===1)iconText="🌤";
  else if(c===2)iconText="⛅";
  else if(c===3)iconText="☁";
  else if(c>=45&&c<=48)iconText="🌫";
  else if(c>=51&&c<=55)iconText="🌦";
  else if(c>=61&&c<=65)iconText="🌧";
  else if(c>=71&&c<=75)iconText="❄";
  else if(c>=80&&c<=82)iconText="🌧";
  else if(c>=95&&c<=99)iconText="⛈";
  icon.textContent=iconText;
}
function drawWindCompass(canvasId,degrees,speed){
  const canvas=$(canvasId);
  if(!canvas)return;
  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height,cx=w/2,cy=h/2,r=Math.min(cx,cy)-6;
  ctx.clearRect(0,0,w,h);
  ctx.strokeStyle="rgba(0,229,255,.25)";
  ctx.lineWidth=.5;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,r*.66,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,r*.33,0,Math.PI*2);ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx,cy-r);ctx.lineTo(cx,cy+r);ctx.stroke();
  ctx.beginPath();ctx.moveTo(cx-r,cy);ctx.lineTo(cx+r,cy);ctx.stroke();
  const dirs=["N","NE","E","SE","S","SO","O","NO"];
  ctx.fillStyle="rgba(0,229,255,.5)";
  ctx.font="9px Inter,sans-serif";
  ctx.textAlign="center";
  ctx.textBaseline="middle";
  dirs.forEach((d,i)=>{
    const angle=(i*Math.PI/4)-Math.PI/2;
    ctx.fillText(d,cx+(r+12)*Math.cos(angle),cy+(r+12)*Math.sin(angle));
  });
  if(degrees===undefined||degrees===null||Number.isNaN(degrees))return;
  const rad=((Number(degrees)-90)*Math.PI)/180;
  const arrowLen=Math.min(r*.7,Math.max(r*.15,(speed||0)*1.5));
  ctx.strokeStyle="#00e5ff";
  ctx.lineWidth=2;
  ctx.shadowColor="#00e5ff";
  ctx.shadowBlur=6;
  ctx.beginPath();
  ctx.moveTo(cx+arrowLen*Math.cos(rad),cy+arrowLen*Math.sin(rad));
  ctx.lineTo(cx-r*.12*Math.cos(rad+2.5),cy-r*.12*Math.sin(rad+2.5));
  ctx.lineTo(cx-r*.12*Math.cos(rad-2.5),cy-r*.12*Math.sin(rad-2.5));
  ctx.closePath();
  ctx.fillStyle="#00e5ff";
  ctx.fill();
  ctx.stroke();
  ctx.shadowBlur=0;
}
function drawLineChart(canvasId,values,minY,maxY){
  const canvas=$(canvasId);
  if(!canvas)return;
  const ctx=canvas.getContext("2d");
  const w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  ctx.globalAlpha=.15;
  ctx.strokeStyle="#00e5ff";
  ctx.lineWidth=1;
  for(let x=0;x<w;x+=24){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}
  for(let y=0;y<h;y+=22){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
  if(values.length<2)return;
  ctx.globalAlpha=1;
  const grad=ctx.createLinearGradient(0,0,w,0);
  grad.addColorStop(0,"#00e5ff");
  grad.addColorStop(.5,"#2aa8ff");
  grad.addColorStop(1,"#43ff73");
  ctx.strokeStyle=grad;
  ctx.lineWidth=2.2;
  ctx.shadowColor="#00e5ff";
  ctx.shadowBlur=8;
  ctx.beginPath();
  values.forEach((value,i)=>{
    const x=i/(values.length-1)*w;
    const normalized=(clamp(value,minY,maxY)-minY)/(maxY-minY);
    const y=h-normalized*h;
    if(i===0)ctx.moveTo(x,y);
    else ctx.lineTo(x,y);
  });
  ctx.stroke();
  ctx.shadowBlur=0;
}
function renderCharts(){
  drawLineChart("activityCanvas",activity,0,100);
  drawLineChart("waveCanvas",waveform,0,80);
}
async function loopStats(){
  try{
    const data=await fetchStats();
    renderStats(data);
  }catch(err){
    console.error(err);
    $("statusText").textContent="SIN DATOS";
    const dot=$("statusDot");
    dot.classList.remove("degraded");
    dot.classList.add("error");
  }finally{
    renderCharts();
  }
}
function applyCoordinates(){
  activeLat=$("latInput").value;
  activeLon=$("lonInput").value;
  loopStats();
}
function toggleBurnHud(){
  burnEnabled=!burnEnabled;
  stopVideo();
  startVideo();
  $("toggleBurnBtn").textContent=burnEnabled?"HUD: ON":"HUD: OFF";
}
function pollFrame(){vidImg.src=`/api/frame?burn=${burnEnabled?"true":"false"}&t=${Date.now()}`}
function startVideo(){frameInterval=setInterval(pollFrame,67);pollFrame()}
function stopVideo(){if(frameInterval){clearInterval(frameInterval);frameInterval=null}}
window.addEventListener("load",()=>{startVideo();loopStats()});
$("applyCoordsBtn")?.addEventListener("click",applyCoordinates);
$("toggleBurnBtn")?.addEventListener("click",toggleBurnHud);
setInterval(loopStats,1000);
setInterval(renderCharts,250);
