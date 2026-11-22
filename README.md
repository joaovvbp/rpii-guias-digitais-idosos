# RPII, guias digitais para idosos

Repositorio de acompanhamento do projeto da disciplina ACH0042, Resolucao de Problemas II, EACH-USP, 2 semestre de 2026, professora Luciane Meneguin Ortega. Aluno Joao Vitor Verissimo Barbosa de Paiva, no USP 11837272. Grupo individual.

## O problema

Uma grande parte das pessoas idosas no Brasil nao tem autonomia para usar a internet com seguranca, nao consegue fazer tarefas digitais basicas sozinha nem reconhecer golpes comuns. Isso exclui essas pessoas de servicos essenciais cada vez mais digitalizados (banco, INSS, gov.br) e faz delas alvo de fraude.

## A solucao em desenvolvimento

Um aplicativo que gera guias ilustrados e com audio, passo a passo, compartilhaveis por link. A ideia veio de uma situacao bem comum: um filho ou neto precisa ensinar a mae ou o avo a fazer algo simples no celular, tipo baixar o app do INSS ou mandar um email com anexo, e acaba repetindo a mesma explicacao por telefone toda vez.

Usuario primario, quem monta e compartilha o guia: o cuidador ou familiar.
Usuario final, quem segue o guia: a pessoa idosa.
IA entra como assistente na redacao do guia a partir de uma biblioteca de tarefas ja revisadas (Meu INSS, email com anexo, Pix seguro, imprimir arquivo, entre outras), nunca como gerador cego sem revisao.

## O MVP

> **Versao intermediaria.** O que esta aqui nao e o resultado final esperado, e sim um passo do desenvolvimento para testar o pivo (o idoso recebe so um video). Os videos ainda usam telas desenhadas, o visual e provisorio e o tamanho da letra ainda nao foi adequado para pessoas idosas. O objetivo e usar gravacoes reais da tela do celular da pessoa, com toque visivel e narracao (#23, #25, #26).

Site estatico, sem servidor e sem login, publicado pelo GitHub Pages.

A pessoa idosa nao usa nenhuma interface nova: recebe so um video no WhatsApp, que imita uma gravacao da tela do celular dela, com o toque visivel e a narracao de cada passo. O site e a ferramenta do cuidador para gerar esse video.

- `index.html`: lado do cuidador, em quatro etapas: o que explicar (guia pronto ou pedido em texto livre, com sugestoes quando nada combina), qual e o celular da pessoa (Android ou iPhone, marca e modelo), conferir um passo por tela e o video. Guia pronto ja tem video para mandar; guia editado ou escrito do zero vem com o roteiro e as instrucoes para gravar a tela com os toques visiveis.
- `video.html` e `ferramentas/quadros.js`: desenham cada quadro do video (celular, legenda, dedo, circulo do toque). `ferramentas/gerar_video.py` junta os quadros com a narracao em `videos/<id>.mp4` e `videos/<id>-iphone.mp4`. Para gerar de novo: `npm install` em `ferramentas/` e `python3 ferramentas/gerar_video.py --piper <piper> --voz <pt_BR-faber-medium.onnx> [--cel iphone]`.
- `guia.html`: a interface passo a passo da primeira versao do MVP, mantida so para os links ja compartilhados. Saiu do fluxo depois dos testes.
- `registro.html`: registro de uso dos testes, guardado so no aparelho onde o guia foi aberto.
- `guias/`: a biblioteca (Isto é golpe?, Pix com segurança, chamada de video, mandar foto, aumentar a letra). `img/`: as ilustracoes de cada passo, com a marcacao do toque.
- `FORMATO.md`: o formato de um guia e como ele vai no link.
- `audio/`: um MP3 por passo dos guias da biblioteca, com voz neural (Piper, voz pt_BR faber). Para gerar de novo depois de mudar um guia: `python3 ferramentas/gerar_audio.py --piper <piper> --voz <pt_BR-faber-medium.onnx>`.

Para rodar no computador: `python3 -m http.server` nesta pasta e abrir `http://localhost:8000`.

Ainda falta: o rascunho gerado por IA para pedidos fora da biblioteca (#8), os prints reais das telas no lugar dos desenhos (#12) e video tambem para os guias editados pelo cuidador. Os guias da biblioteca sao rascunhos e ainda precisam ser testados passo a passo no aplicativo real.

## Backlog do projeto

Entrega transversal da disciplina. O backlog fica no projeto do GitHub vinculado a este repositorio, em formato de quadro Kanban, e vai sendo atualizado ao longo do semestre conforme o ciclo de Sprints (PBL, Lean Startup e Scrum/Kanban).

**Quadro Kanban: [RPII, Backlog do Projeto](https://github.com/users/joaovvbp/projects/5/views/1)**

O link abre direto no quadro, sem precisar de login. Outro caminho para chegar nele:

1. Abrir a aba [Projects](https://github.com/joaovvbp/rpii-guias-digitais-idosos/projects) no topo deste repositorio.
2. Clicar em "RPII, Backlog do Projeto".
3. Escolher a aba "Kanban", que e a primeira.

Como ler o quadro:

| Coluna | Significado |
| --- | --- |
| Planned | Backlog, o que ainda nao comecou |
| In progress | Em andamento |
| Done | Concluido |

Cada cartao e uma [issue](https://github.com/joaovvbp/rpii-guias-digitais-idosos/issues) deste repositorio e mostra o marco a que pertence, a estimativa em pontos e a area do produto (Idoso, Cuidador, Biblioteca ou Infra). Os [marcos](https://github.com/joaovvbp/rpii-guias-digitais-idosos/milestones) agrupam as issues por etapa do MVP. A aba [Tabela](https://github.com/users/joaovvbp/projects/5/views/2) do mesmo projeto mostra os mesmos itens em lista.

## Por que escolhi o GitHub em vez de Trello, Miro ou Notion

Ja tenho familiaridade com o GitHub e a ferramenta se integra melhor com o processo de desenvolvimento do meu caso de uso, ja que o produto final e um software e faz sentido manter o backlog junto do lugar onde o codigo do projeto vai ficar.

## Sobre este repositorio estar publico

Este repositorio comecou privado. Deixei publico por enquanto so pra garantir que a professora consiga acompanhar o andamento do backlog sem depender de convite ou de eu ter o e-mail dela cadastrado a tempo da entrega. Nao ha nada sensivel aqui, e um projeto academico. A ideia e voltar pra privado assim que o acesso dela estiver garantido de outra forma, entao se voce estiver vendo isso mais pra frente no semestre e o repositorio ja estiver privado de novo, e por isso.
