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
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(texto);
    u.lang = 'pt-BR';
    if (voz) u.voice = voz;
    u.rate = 0.85;   // um pouco mais devagar que o normal
    if (aoTerminar) u.onend = aoTerminar;
    speechSynthesis.speak(u);
    return true;
  }

  function parar() { if (disponivel()) speechSynthesis.cancel(); }

  return { falar: falar, parar: parar, disponivel: disponivel };
})();
