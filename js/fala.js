// Leitura em voz alta com a voz do próprio celular (Web Speech API), em português do Brasil.
// Não precisa de internet nem de arquivo de áudio: funciona igual para guias da biblioteca
// e para guias que o cuidador acabou de escrever.

var Fala = (function () {
  'use strict';

  var voz = null;

  function escolheVoz() {
    if (!('speechSynthesis' in window)) return;
    var vozes = speechSynthesis.getVoices();
    voz = vozes.find(function (v) { return v.lang === 'pt-BR'; }) ||
          vozes.find(function (v) { return /^pt/i.test(v.lang); }) || null;
  }
  if ('speechSynthesis' in window) {
    escolheVoz();
    speechSynthesis.onvoiceschanged = escolheVoz;
  }

  function disponivel() { return 'speechSynthesis' in window; }

  function falar(texto, aoTerminar) {
    if (!disponivel()) return false;
    if (tocando) { tocando.pause(); tocando = null; }
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(texto);
    u.lang = 'pt-BR';
    if (voz) u.voice = voz;
    u.rate = 0.85;   // um pouco mais devagar que o normal
    if (aoTerminar) u.onend = aoTerminar;
    speechSynthesis.speak(u);
    return true;
  }

  // Áudio pré-gerado do passo (guias da biblioteca). Se o arquivo não carregar,
  // cai para a voz do aparelho.
  var tocando = null;
  function tocar(arquivo, texto, aoTerminar) {
    parar();
    var a = new Audio(arquivo);
    tocando = a;
    if (aoTerminar) a.onended = aoTerminar;
    var reserva = function () { if (tocando === a) { tocando = null; falar(texto, aoTerminar); } };
    a.onerror = reserva;
    var p = a.play();
    if (p && p.catch) p.catch(reserva);
    return true;
  }

  // Toca o arquivo do passo quando existe; senão, lê com a voz do aparelho.
  function passo(p, texto, aoTerminar) {
    return p.audio ? tocar(p.audio, texto, aoTerminar) : falar(texto, aoTerminar);
  }

  function parar() {
    if (tocando) { tocando.onended = null; tocando.onerror = null; tocando.pause(); tocando = null; }
    if (disponivel()) speechSynthesis.cancel();
  }

  return { falar: falar, passo: passo, parar: parar, disponivel: disponivel };
})();
