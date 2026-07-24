// Runs the JS embedded in aheui_console.html under Node with a stub DOM,
// so the shipped browser code is actually exercised rather than assumed.
const fs = require('fs');

const html = fs.readFileSync('aheui_console.html', 'utf8');
const script = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));

let captured = '';
function mkEl(id) {
  return {
    id, textContent: '', value: '', placeholder: '', disabled: false, scrollTop: 0, scrollHeight: 0,
    className: '', files: [],
    classList: { toggle() {}, add() {}, remove() {} },
    appendChild(n) { if (id === 'term') captured += n.textContent; },
    addEventListener() {},
    focus() {},
  };
}
const els = {};
global.document = {
  getElementById: id => (els[id] ||= mkEl(id)),
  createElement: () => ({ textContent: '', className: '' }),
};
global.location = { protocol: 'file:' };
global.setTimeout = setTimeout;

// expose start() by evaluating the script body then grabbing it
const fn = new Function(`${script}\nreturn { start, buildGrid, buildSkip, decodePNG };`);
const api = fn();

(async () => {
  const bytes = new Uint8Array(fs.readFileSync(process.argv[2] || 'test_console.png'));
  const raw = await api.decodePNG(bytes);
  const g = api.buildGrid(raw);
  console.log(`grid: ${g.rows} rows x ${g.W} cols`);
  const skip = api.buildSkip(g);
  console.log(`skip tables: ${skip.filter(Boolean).length}/${g.W} columns`);

  await api.start(bytes);
  // start() kicks off vm.run() without awaiting; poll until it finishes
  for (let i = 0; i < 2000; i++) {
    await new Promise(r => setTimeout(r, 5));
    if (captured.includes('A9') || i === 1999) break;
  }
  const out = captured.replace(/^[\s\S]*?열\n\n/, '');
  console.log('captured output:', JSON.stringify(out));
  console.log(out.includes('A9') ? 'PASS: got A9' : 'FAIL');
})();
