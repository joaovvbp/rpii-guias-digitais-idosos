// Desenha os quadros do vídeo de um guia a partir de video.html, no Chrome sem janela.
// Uso: node ferramentas/quadros.js <url base> <id do guia> <pasta de saída> [android|iphone]
// Grava <pasta>/<tela>-<nnn>.png e <pasta>/telas.json com a lista de telas e quantos quadros
// cada uma tem. Passo com toque ganha a animação do dedo; os outros, um quadro só.
const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const [base, id, saida, cel = 'android'] = process.argv.slice(2);
const QPS = 25, ANIM_TOQUE = 1.6, ANIM_OLHE = 1.0;

(async () => {
  const guia = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'guias', id + '.json'), 'utf8'));
  const chrome = process.env.CHROME || '/usr/bin/google-chrome';
  const b = await puppeteer.launch({ executablePath: chrome, headless: 'new', args: ['--no-first-run', '--hide-scrollbars'] });
  const p = await b.newPage();
  await p.setViewport({ width: 720, height: 1280, deviceScaleFactor: 1 });
  fs.mkdirSync(saida, { recursive: true });
  const telas = [{ tela: 'capa' }]
    .concat(guia.passos.map((ps, i) => ({ tela: String(i + 1), anim: ps.marca && ps.imagem ? (ps.acao === 'olhe' ? ANIM_OLHE : ANIM_TOQUE) : 0, audio: ps.audio || null })))
    .concat([{ tela: 'fim' }]);
  for (const t of telas) {
    const n = t.anim ? Math.round(t.anim * QPS) : 1;
    for (let k = 0; k < n; k++) {
      const tt = n === 1 ? 1 : k / (n - 1);
      await p.goto('about:blank');
      await p.goto(`${base}video.html#g=${id}&tela=${t.tela}&t=${tt.toFixed(3)}&cel=${cel}`, { waitUntil: 'load' });
      await p.waitForSelector('body[data-pronto]', { timeout: 10000 });
      await p.screenshot({ path: path.join(saida, `${t.tela}-${String(k).padStart(3, '0')}.png`) });
    }
    t.quadros = n;
  }
  fs.writeFileSync(path.join(saida, 'telas.json'), JSON.stringify(telas, null, 1));
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
