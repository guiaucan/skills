# Harness

Contexto do produto: um harness de agentes e skills, inicialmente voltado a trabalho de software (programar, revisar, commitar). O Operador dispara Agents um a um sobre Workspaces locais (N Workspaces; no máximo um Run por Workspace). Expansão para outros fins fica adiada até esse núcleo estabilizar. Push fica fora do Harness. Decisões de implementação (stack, CLI, formato de arquivo de Skill) ficam fora deste glossário.

## Language

**Harness**:
O sistema que orquestra e isola runs de agentes de IA, detém o conjunto de Skills e a Denylist, e mantém o Histórico. Não encadeia Agents por conta própria; não julga a qualidade do trabalho dos Agents. Isolar significa: um Run não vê nem altera estado de outro Run em andamento, e um Run não vaza efeitos para fora do Workspace declarado. No máximo um Run por Workspace.
_Avoid_: framework, plataforma, runtime (como sinônimos do produto); avaliar/avaliação (como capacidade do Harness)

**Agent**:
Um papel com mandato fixo (o que pode e deve fazer). Cada invocação é um Run de um único Agent. O mandato — não o catálogo de Skills — é o que impede um Agent de exercer efeitos de outro papel (ex.: Coder não executa `git commit`).
_Avoid_: bot, assistente, persona (como sinônimos)

**Skill**:
Um procedimento reutilizável pertencente ao Harness; qualquer Agent pode carregá-la num Run. Carregar uma Skill não concede efeito proibido pelo mandato (ex.: Coder pode usar Skill de mensagem de commit só como conselho em texto).
_Avoid_: prompt, playbook, recipe (como sinônimos)

**Run**:
Uma invocação de um único Agent, do disparo pelo Operador até conclusão, cancelamento pelo Operador, ou falha. Cancelar não altera o Workspace. No Committer, inclui o ciclo de propor mensagem até o Operador confirmar ou cancelar.
_Avoid_: sessão, pedido, workflow, pipeline

**Histórico**:
O registro mantido pelo Harness de Runs e Pareceres (por Workspace). Não vive no Workspace.
_Avoid_: log, diário, audit trail (como sinônimos)

**Workspace**:
A pasta/repositório git local no disco do Operador sobre o qual Coder, Reviewer e Committer operam. O Operador pode ter vários Workspaces; a regra de um Run aplica-se por Workspace.
_Avoid_: projeto, repo (como sinônimos soltos), remote

**Denylist**:
Paths/padrões definidos no Harness que o Committer nunca inclui num commit, além do que o ignore do git do Workspace já exclui.
_Avoid_: blocklist, deny list, proteção de commit (como sinônimos)

**Coder**:
O Agent cujo mandato é implementar mudanças no código do Workspace. Não cria commits. Se Skills carregadas exigem checks, o Run conclui quando esses checks passam; se nenhuma exige check, o Run conclui quando não há mais edições planejadas.
_Avoid_: programmer, developer-agent, implementer

**Reviewer**:
O Agent cujo mandato é revisar um alvo no Workspace e emitir um Parecer. O alvo default é o diff entre a branch atual (commits + working tree) e o upstream de tracking (`@{upstream}`); o Operador pode definir outro alvo no disparo. Se não houver upstream, não há default — o Operador deve definir o alvo. Não autoriza nem bloqueia commit; o Parecer não entra no fluxo de commit.
_Avoid_: critic, auditor, gate, approver (como papel de bloqueio)

**Parecer**:
O julgamento persistente deixado por um Run do Reviewer (aprovado, com ressalvas ou rejeitado, mais notas). Vive no Histórico. É conselho ao Operador, não pré-requisito de commit.
_Avoid_: approval, review report, veredito (como gate)

**Committer**:
O Agent cujo mandato é propor mensagens e, após confirmação do Operador, criar um commit com tudo que estiver modificado no working tree do Workspace, exceto paths cobertos pela união de ignore do git e Denylist. Se o Operador rejeita a mensagem, o mesmo Run segue propondo até confirmar ou cancelar. Não faz push; não lê nem exige Parecer.
_Avoid_: git-agent, pusher

**Operador**:
A pessoa que dispara o Harness sob demanda (no início: desenvolvedor solo, via IDE/CLI), escolhe Workspace e Agent, confirma ou rejeita mensagens do Committer, cancela Runs, e é responsável pelo push fora do Harness.
_Avoid_: user, cliente, account
