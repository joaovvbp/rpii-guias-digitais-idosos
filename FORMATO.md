# Formato de um guia

Issue #3. A pagina do guia (`guia.html`) e a tela do cuidador (`index.html`) usam a mesma estrutura, em JSON.

```json
{
  "id": "golpe",
  "titulo": "Isto é golpe?",
  "categoria": "Dinheiro com segurança",
  "resumo": "Uma frase sobre o guia.",
  "revisado": "quando e como o guia foi conferido",
  "fontes": ["de onde veio o conteudo"],
  "passos": [
    { "frase": "Recebeu uma mensagem estranha? Pare.", "emoji": "✋" },
    {
      "frase": "No alto da tela, toque no desenho da câmera.",
      "fala": "texto do audio, se for diferente da frase (opcional)",
      "audio": "audio/video-3.mp3",
      "imagem": "img/video-conversa.svg",
      "descricao": "texto alternativo da imagem",
      "marca": { "x": 73, "y": 1, "l": 15, "a": 14 }
    }
  ]
}
```

- `titulo` e `passos` sao obrigatorios. Cada passo precisa de `frase`; o resto e opcional. No maximo 12 passos.
- `fala` e o texto lido em voz alta. Sem ela, a voz le a `frase`.
- `audio` e o arquivo MP3 do passo em `audio/`, gerado por `ferramentas/gerar_audio.py`. Quando existe, a pagina toca o arquivo; quando nao existe (guia editado pelo cuidador) ou nao carrega, usa a voz do aparelho. Editar a frase de um passo descarta o `audio` dele.
- `{contato}` em qualquer frase vira o nome de quem mandou o guia (ou "alguém de confiança").
- `imagem` e um arquivo em `img/`. `marca` e o retangulo vermelho que mostra onde tocar, em porcentagem da imagem: `x` e `y` sao o canto de cima a esquerda, `l` a largura, `a` a altura. Serve tanto para os desenhos atuais quanto para prints reais da tela (issue #12).
- Sem imagem, o passo pode ter um `emoji` grande.

## Onde ficam

- `guias/index.json`: a lista da biblioteca, com as `palavras` usadas para achar o guia a partir do pedido em texto livre.
- `guias/<id>.json`: cada guia.

## Como o guia vai no link

Tudo vai depois do `#`, que o navegador nao envia para o servidor:

- guia da biblioteca sem mudancas: `guia.html#g=golpe`
- guia montado ou editado pelo cuidador: `guia.html#d=<guia em base64>`, so com `titulo` e `passos`
- quem ajuda: `c=<nome>` e `t=<whatsapp com DDI e DDD>`, para o botao "Não consegui. Pedir ajuda"

Exemplo: `guia.html#g=golpe&c=Marina&t=5511912345678`
