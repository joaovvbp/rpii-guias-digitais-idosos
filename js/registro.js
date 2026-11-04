// Registro de uso para os testes com usuários (issue #14).
// Fica só no aparelho onde o guia foi aberto (localStorage), nada é enviado pela internet.
// A página registro.html mostra o que aconteceu em cada sessão e deixa copiar.

var Registro = (function () {
  'use strict';

  var CHAVE = 'guias-registro-v1';
  var sessao = null;

  function ler() {
    try { return JSON.parse(localStorage.getItem(CHAVE)) || []; } catch (e) { return []; }
  }
  function gravar(lista) {
    try { localStorage.setItem(CHAVE, JSON.stringify(lista.slice(-200))); } catch (e) { /* sem espaço ou bloqueado */ }
  }

  // Começa uma sessão nova cada vez que um guia é aberto.
  function inicia(titulo, totalPassos) {
    sessao = { id: Date.now().toString(36), guia: titulo, passos: totalPassos, inicio: Date.now(), eventos: [] };
    var lista = ler();
    lista.push(sessao);
    gravar(lista);
  }

  // tipo: ver, ouvir, voltar, ajuda, nao-deu, mensagem, fim
  function anota(tipo, passo) {
    if (!sessao) return;
    var lista = ler();
    var s = lista.find(function (x) { return x.id === sessao.id; });
    if (!s) return;
    s.eventos.push({ t: Math.round((Date.now() - s.inicio) / 1000), tipo: tipo, passo: passo });
    gravar(lista);
  }

  function todas() { return ler(); }
  function limpa() { try { localStorage.removeItem(CHAVE); } catch (e) { /* nada */ } }

  return { inicia: inicia, anota: anota, todas: todas, limpa: limpa };
})();
