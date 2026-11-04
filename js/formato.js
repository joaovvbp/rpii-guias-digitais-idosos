// Formato de um guia (ver FORMATO.md) e o jeito de levá-lo dentro de um link.
// Tudo o que identifica a família (nome e telefone de quem ajuda) vai depois do "#",
// que o navegador não envia para nenhum servidor.

var Guias = (function () {
  'use strict';

  var LIMITE_PASSOS = 12;

  // Lista dos guias da biblioteca, de guias/index.json.
  function biblioteca() {
    return fetch('guias/index.json', { cache: 'no-cache' }).then(function (r) {
      if (!r.ok) throw new Error('não achei a biblioteca de guias');
      return r.json();
    });
  }

  function daBiblioteca(id) {
    if (!/^[a-z0-9-]+$/.test(id)) return Promise.reject(new Error('guia inválido'));
    return fetch('guias/' + id + '.json', { cache: 'no-cache' }).then(function (r) {
      if (!r.ok) throw new Error('não achei o guia "' + id + '"');
      return r.json();
    }).then(valida);
  }

  // Confere o mínimo para a página do guia funcionar e descarta o resto.
  function valida(g) {
    if (!g || typeof g.titulo !== 'string' || !Array.isArray(g.passos) || g.passos.length === 0) {
      throw new Error('guia sem título ou sem passos');
    }
    var passos = g.passos.slice(0, LIMITE_PASSOS).map(function (p) {
      if (!p || typeof p.frase !== 'string' || !p.frase.trim()) throw new Error('passo sem frase');
      var limpo = { frase: p.frase.trim().slice(0, 300) };
      if (typeof p.fala === 'string' && p.fala.trim()) limpo.fala = p.fala.trim().slice(0, 500);
      if (typeof p.emoji === 'string' && p.emoji) limpo.emoji = p.emoji.slice(0, 8);
      if (typeof p.imagem === 'string' && /^img\/[a-z0-9-]+\.(svg|png|jpg|webp)$/.test(p.imagem)) {
        limpo.imagem = p.imagem;
        if (p.descricao) limpo.descricao = String(p.descricao).slice(0, 200);
        if (p.marca && ['x', 'y', 'l', 'a'].every(function (k) { return typeof p.marca[k] === 'number'; })) {
          limpo.marca = { x: p.marca.x, y: p.marca.y, l: p.marca.l, a: p.marca.a };
        }
      }
      return limpo;
    });
    var saida = { titulo: g.titulo.trim().slice(0, 80), passos: passos };
    if (g.id) saida.id = String(g.id);
    if (g.resumo) saida.resumo = String(g.resumo).slice(0, 200);
    return saida;
  }

  // Texto (UTF-8) <-> base64 que pode ir num link.
  function paraBase64(texto) {
    var bytes = new TextEncoder().encode(texto);
    var bin = '';
    bytes.forEach(function (b) { bin += String.fromCharCode(b); });
    return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function deBase64(b64) {
    var bin = atob(b64.replace(/-/g, '+').replace(/_/g, '/'));
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  // Monta o link que vai para o idoso.
  // Guia da biblioteca: guia.html#g=<id>. Guia montado ou editado: guia.html#d=<guia em base64>.
  function link(guia, contato, editado) {
    var p = new URLSearchParams();
    if (guia.id && !editado) {
      p.set('g', guia.id);
    } else {
      var copia = { titulo: guia.titulo, passos: guia.passos };
      p.set('d', paraBase64(JSON.stringify(copia)));
    }
    if (contato && contato.nome) p.set('c', contato.nome.trim().slice(0, 40));
    if (contato && contato.tel) p.set('t', soDigitos(contato.tel));
    var base = location.href.replace(/[^/]*([?#].*)?$/, '');
    return base + 'guia.html#' + p.toString();
  }

  // Lê o guia a partir do "#" do endereço atual.
  function doLink(hash) {
    var p = new URLSearchParams((hash || location.hash).replace(/^#/, ''));
    var contato = { nome: p.get('c') || '', tel: soDigitos(p.get('t') || '') };
    var promessa;
    if (p.get('d')) {
      promessa = new Promise(function (ok) { ok(valida(JSON.parse(deBase64(p.get('d'))))); });
    } else if (p.get('g')) {
      promessa = daBiblioteca(p.get('g'));
    } else {
      promessa = Promise.reject(new Error('este link não tem guia'));
    }
    return promessa.then(function (g) { return { guia: g, contato: contato }; });
  }

  function soDigitos(t) { return String(t).replace(/\D/g, '').slice(0, 15); }

  // Troca {contato} pelo nome de quem ajuda.
  function comContato(texto, contato) {
    var nome = contato && contato.nome ? contato.nome : 'alguém de confiança';
    return texto.replace(/\{contato\}/g, nome);
  }

  // Escolhe o guia da biblioteca que mais combina com o pedido em texto livre.
  function semAcento(t) { return t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function combina(pedido, lista) {
    var texto = semAcento(pedido);
    var melhor = null, pontos = 0;
    lista.forEach(function (g) {
      var n = 0;
      (g.palavras || []).forEach(function (w) { if (texto.indexOf(semAcento(w)) >= 0) n++; });
      if (n > pontos) { pontos = n; melhor = g; }
    });
    return melhor;
  }

  return {
    biblioteca: biblioteca, daBiblioteca: daBiblioteca, valida: valida,
    link: link, doLink: doLink, comContato: comContato, combina: combina,
    soDigitos: soDigitos, LIMITE_PASSOS: LIMITE_PASSOS
  };
})();
