const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage(); p.on('pageerror', e => console.log(e.message));
  await p.goto('http://localhost:8776/index.html');
  await p.waitForFunction(() => window.__sh, null, { timeout: 300000 });
  const L = JSON.parse(require('fs').readFileSync('t2.json'))[1];
  console.log(await p.evaluate(async s => { window.__sh.LOOKS[s.look] = s.lookDef; const S = window.__sh.state; S.mode='one'; S.gw=s.gw; S.cw={}; S.over={}; S.look=s.look; window.__keepX = true; await window.__sh.refresh();
    const sg = window.__weld, X = window.__lastX, V = sg.V, T = sg.tris, ec = new Map(); for (let t = 0; t < T.length; t += 3) for (let e = 0; e < 3; e++) { const a = T[t+e], c = T[t+(e+1)%3], k = a < c ? a*V+c : c*V+a; ec.set(k,(ec.get(k)||0)+1); }
    const adj = new Map(); for (const [k, v] of ec) if (v === 1) { const a = Math.floor(k / V), c = k % V; (adj.get(a) || adj.set(a, []).get(a)).push(c); (adj.get(c) || adj.set(c, []).get(c)).push(a); }
    const seen = new Set(), loops = []; for (const s0 of adj.keys()) { if (seen.has(s0)) continue; const L = []; let st = [s0]; seen.add(s0); while (st.length) { const u = st.pop(); L.push(u); for (const w of adj.get(u)) if (!seen.has(w)) { seen.add(w); st.push(w); } } loops.push(L); }
    return JSON.stringify(loops.map(L => { let mn=[9,9,9], mx=[-9,-9,-9]; for (const i of L) for (let q=0;q<3;q++){ mn[q]=Math.min(mn[q],X[i*3+q]); mx[q]=Math.max(mx[q],X[i*3+q]); } return { n: L.length, mn: mn.map(v=>+v.toFixed(2)), mx: mx.map(v=>+v.toFixed(2)) }; })); }, L));
  await b.close();
})();
