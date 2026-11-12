"""Generated ambient loop (Web Audio). Needs a click to start."""
AUDIO_HTML = r'''<div style="font:700 10px monospace;color:#6f5bd3;letter-spacing:.1em">TAPE // AMBIENT LOOP<br>
<button id=b style="margin-top:8px;width:40px;height:40px;border-radius:12px;border:2px solid #a79bdc;background:#fff8;color:#6f5bd3;cursor:pointer;font-size:14px">&#9654;</button>
<input id=v type=range min=0 max=100 value=40 style="vertical-align:middle;accent-color:#6f5bd3;width:110px"></div><script>let c,m,on=0,t,s=0,o=[];const CH=[[261.6,329.6,392,493.9],[220,277.2,329.6,415.3],[174.6,220,261.6,329.6],[196,246.9,293.7,392]];
    function hit(k,w){const g=c.createGain();g.connect(m);if(k=='k'){const x=c.createOscillator();x.frequency.setValueAtTime(110,w);x.frequency.exponentialRampToValueAtTime(40,w+.15);g.gain.setValueAtTime(.5,w);g.gain.exponentialRampToValueAtTime(.001,w+.2);x.connect(g);x.start(w);x.stop(w+.22)}
    else{const n=c.createBuffer(1,c.sampleRate*.2,c.sampleRate),d=n.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;const r=c.createBufferSource();r.buffer=n;const f=c.createBiquadFilter();f.type='bandpass';f.frequency.value=k=='s'?1800:7000;g.gain.setValueAtTime(k=='s'?.16:.04,w);g.gain.exponentialRampToValueAtTime(.001,w+(k=='s'?.14:.04));r.connect(f);f.connect(g);r.start(w)}}
    b.onclick=()=>{if(on){clearInterval(t);c.suspend();on=0;b.textContent='▶';return}
    if(!c){c=new AudioContext();m=c.createGain();m.gain.value=v.value/100*.6;m.connect(c.destination);const lp=c.createBiquadFilter();lp.frequency.value=900;lp.connect(m);
    CH[0].forEach((f,i)=>{const x=c.createOscillator(),g=c.createGain();x.type=i%2?'triangle':'sine';x.frequency.value=f;g.gain.value=.12;x.connect(g);g.connect(lp);x.start();o.push(x)})}
    c.resume();on=1;b.textContent='❚❚';t=setInterval(()=>{const w=c.currentTime+.05,q=s%16;if(q==0||q==10)hit('k',w);if(q==4||q==12)hit('s',w);if(q%2==0)hit('h',w);
    if(s%128==0){const h=CH[(s/128)%4];o.forEach((x,i)=>x.frequency.setTargetAtTime(h[i],w,2.5))}s++},93.75)};
    v.oninput=()=>{if(m)m.gain.value=v.value/100*.6}</script>'''