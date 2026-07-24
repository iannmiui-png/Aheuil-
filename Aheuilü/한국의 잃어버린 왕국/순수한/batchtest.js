// Batch differential test: runs each generated PNG through the JS embedded in
// aheui_console.html and compares against the reference Brainfuck output.
const fs = require('fs');

const html = fs.readFileSync('aheui_console.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '';
function mkEl(id) {
  return {
    id, textContent: '', value: '', placeholder: '', disabled: false,
    scrollTop: 0, scrollHeight: 0, className: '', files: [],
    classList: { toggle() {}, add() {}, remove() {} },
    appendChild(n) { if (id === 'term') captured += n.textContent; },
    addEventListener() {}, focus() {},
  };
}
const els = {};
global.document = {
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: () => ({ textContent: '', className: '' }),
};
global.location = { protocol: 'file:' };

const api = new Function(`${script}\nreturn { decodePNG, buildGrid, buildSkip, AheuiVM };`)();

async function runCase(png) {
  const raw = await api.decodePNG(new Uint8Array(fs.readFileSync(png)));
  const g = api.buildGrid(raw);
  const skip = api.buildSkip(g);
  captured = '';
  const vm = new api.AheuiVM(g, skip);
  const t = setTimeout(() => { vm.done = true; }, 20000);
  await vm.run();
  clearTimeout(t);
  return captured;
}

(async () => {
  const cases = JSON.parse(fs.readFileSync('jstest/cases.json', 'utf8'));
  let pass = 0;
  const fails = [];
  for (const c of cases) {
    let got;
    try { got = await runCase(c.png); }
    catch (e) { got = '<ERR ' + e.message + '>'; }
    if (got === c.expect) pass++;
    else fails.push({ bf: c.bf.slice(0, 50), expect: c.expect, got });
  }
  console.log(`JS console: ${pass}/${cases.length} passed`);
  for (const f of fails.slice(0, 4)) {
    console.log('  FAIL', JSON.stringify(f.bf));
    console.log('    expect', JSON.stringify(f.expect));
    console.log('    got   ', JSON.stringify(f.got));
  }
})();
