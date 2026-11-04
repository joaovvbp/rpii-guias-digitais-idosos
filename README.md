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

Site estatico, sem servidor e sem login, publicado pelo GitHub Pages.

- `index.html`: lado do cuidador. Descreve o pedido em texto livre ou escolhe um guia pronto, confere e edita os passos, ouve como vai ficar e manda o link pelo WhatsApp.
- `guia.html`: lado da pessoa idosa. Um passo por tela, letra grande, botao para ouvir o passo (voz do proprio celular), voltar e avancar, e "Não consegui. Pedir ajuda", que abre o WhatsApp de quem mandou o guia ja dizendo em que passo travou.
- `registro.html`: registro de uso dos testes, guardado so no aparelho onde o guia foi aberto.
- `guias/`: a biblioteca (Isto é golpe?, Pix com segurança, chamada de video, mandar foto, aumentar a letra). `img/`: as ilustracoes de cada passo, com a marcacao do toque.
- `FORMATO.md`: o formato de um guia e como ele vai no link.

Para rodar no computador: `python3 -m http.server` nesta pasta e abrir `http://localhost:8000`.

Ainda falta: o rascunho gerado por IA para pedidos fora da biblioteca (#8) e os prints reais das telas no lugar dos desenhos (#12). Os guias da biblioteca sao rascunhos e ainda precisam ser testados passo a passo no aplicativo real.

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
