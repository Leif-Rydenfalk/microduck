/* Photograph the microduck bench, in a browser that HAS WebGL.
 *
 * WHY THIS EXISTS AND cecad.shots DOES NOT DO IT: the shared prober holds one
 * headless Chrome started with `--disable-gpu` (ce-cad/web/shotd.mjs:185), and
 * that browser hands out no WebGL context at all. MEASURED 2026-09-02, same
 * page, same port: under shotd `ready` never went true (`ready_ms` 45232, the
 * whole budget); in a Chrome launched without that flag the page was ready in
 * 9 s and drew 817,902 triangles. So this reuses ce-cad's own CDP driver
 * (web/_cdp.mjs) and only drops the one flag.
 *
 * It refuses to save a picture the page has not finished drawing: it polls the
 * page's own `window.__mdReady` handshake, and a shot whose PNG comes back
 * under 20 kB is reported as a FAILURE rather than filed as evidence.
 *
 *   node tools/shoot_viewer.mjs [outDir]
 */
import { launchBrowser, attach, sleep } from '/Users/leifrydenfalk/dev/ce-workshop/ce-cad/web/_cdp.mjs';
import { writeFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const OUT = process.argv[2] ||
  '/Users/leifrydenfalk/dev/ce-workshop/ce-designs/microduck/out/viewer-proof';
const BASE = 'http://localhost:8765/web/microduck.html';
const W = 1600, H = 1000;

const SHOTS = [
  ['01-assembly-stand.png', '?pose=STAND', 'the whole robot in the STAND pose'],
  ['02-parts-exploded.png', '?pose=STAND&explode=90', 'every placed part, pulled apart'],
  ['03-hinge-axes.png', '?pose=SIT&axes=1', 'SIT, with all 14 hinge axes drawn'],
  ['04-joint-clamped.png', '?pose=STAND&joint=left_hip_yaw:88&joint=head_roll:-60&joint=left_knee:-95',
   'three sliders driven past their limits — the pose clamps and the panel says so'],
  ['05-walk-frame.png', '?traj=walk_ours&frame=170', 'frame 170 of the recorded walk'],
  ['06-part-picked.png', '?pose=STAND&part=microduck-hip-bracket&isolate=1',
   'one part isolated, with its card and its links'],
  ['07-xray.png', '?pose=STAND&xray=1', 'shells made transparent — the servos and the boards'],
  ['08-sitstand-frame.png', '?traj=sitstand_ours&frame=250', 'the sit/stand policy mid-rise'],
];

mkdirSync(OUT, { recursive: true });
const br = await launchBrowser({
  port: 9461, windowSize: `${W},${H}`,
  // The one difference from shotd: no --disable-gpu, so WebGL exists.
  args: ['--headless=new', '--no-sandbox', '--hide-scrollbars'],
});
let fails = 0;
try {
  for (const [name, qs, why] of SHOTS) {
    const page = await attach({ url: 'about:blank', port: 9461, host: br.host });
    try {
      await page.send('Emulation.setDeviceMetricsOverride',
        { width: W, height: H, deviceScaleFactor: 1, mobile: false });
      await page.send('Page.navigate', { url: BASE + qs });
      let ready = null;
      for (let i = 0; i < 120; i++) {
        // attach().evaluate returns the VALUE, not a CDP result envelope
        // (ce-cad/web/_cdp.mjs:151). Reading r.result.value here cost an hour.
        const v = await page.evaluate('JSON.stringify(window.__mdReady || null)');
        if (v && v !== 'null') { ready = JSON.parse(v); break; }
        await sleep(500);
      }
      if (!ready) { console.log(`FAIL  ${name}  page never reported ready`); fails++; continue; }
      if (!ready.webgl) { console.log(`FAIL  ${name}  no WebGL: ${ready.webgl_reason}`); fails++; continue; }
      await sleep(1400);                       // let the damped camera settle
      const shot = await page.send('Page.captureScreenshot', { format: 'png' });
      const buf = Buffer.from(shot.data, 'base64');
      const p = join(OUT, name);
      writeFileSync(p, buf);
      const bytes = statSync(p).size;
      const ok = bytes > 20000;
      if (!ok) fails++;
      console.log(`${ok ? 'PASS' : 'FAIL'}  ${name}  ${bytes.toLocaleString()} B  ` +
                  `${ready.geoms} parts, ${ready.tris.toLocaleString()} tris, traj ${ready.traj}  — ${why}`);
    } finally { try { await page.closePage(); } catch (_) {} }
  }
} finally { await br.kill(); }
console.log(fails ? `\n${fails} SHOT(S) FAILED` : '\nall shots drew');
process.exit(fails ? 1 : 0);
