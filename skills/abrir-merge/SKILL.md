---
name: abrir-merge
description: >
  Abre ou atualiza Merge Request / Pull Request (GitLab, GitHub, Azure DevOps, etc.)
  a partir do estado real do git: target, descrição Markdown, promoção, predecessores.
  Pergunta o necessário; grava padrões do projeto em .scratch/forge-defaults.md.
  Preferir MCP da forge; CLI (glab/gh/az) só como fallback. Use /abrir-merge.
disable-model-invocation: true
---

# Abrir merge (MR / PR)

Cria ou atualiza um pedido de merge a partir do **estado real do repositório**.

Idioma: **português (Brasil)**, salvo pedido contrário.

**Nome do artefato:** no GitLab = **Merge Request (MR)**; no GitHub = **Pull Request (PR)**; no Azure DevOps = **Pull Request**. Use o termo da forge ativa.

Opcional antes de abrir: `/revisar-merge-profundo` (branch ou URL do MR|PR) para review profundo no target.

## Git e permissões

- **Nunca** `git commit` / `git push` / criar MR|PR **sem ok explícito** do usuário nestes passos.
- Pode **inspecionar** git (status, diff, log, remotes) sem pedir.
- Antes de push ou create: mostrar resumo (source, target, título) e perguntar.

## Defaults do projeto (não perguntar de novo)

Arquivo: **`.scratch/forge-defaults.md`**

No **início** da skill:

1. Se o arquivo existir → ler e aplicar (forge, MCP, targets usuais, padrão de título, promoção, etc.).
2. O que **não** estiver no arquivo e for necessário → **perguntar**.
3. Ao fim (ou quando o usuário confirmar um padrão novo) → **atualizar** `.scratch/forge-defaults.md` com o que ficou decidido.

Não versionar `.scratch/` sem pedido explícito.

### Template sugerido de `.scratch/forge-defaults.md`

```md
# Forge defaults (local)

**Forge:** gitlab | github | azure | outro
**MCP preferido:** <nome do namespace MCP, ex. user-gitlab-mcp-server>
**CLI fallback:** glab | gh | az | nenhum
**Projeto:** <group/project ou owner/repo>
**Targets usuais:** main, qas, homolog, …
**Padrão de título:** tipo(#ISSUE): descricao
**Promoção:** perguntar sempre | raro | nunca neste repo
**Fechar issue no merge:** nao (citar só Issue #N)
**MRs de referencia:** <IID ou URL, opcional — exemplos de boa descrição>
**Notas:** …
```

---

## Fluxo

### 1. Inspecionar git

- `git status --short`
- `git branch --show-current`
- `git rev-parse --abbrev-ref --symbolic-full-name @{u}` (se houver)
- `git remote get-url origin`

### 2. Resolver forge + transporte

Ordem:

1. `.scratch/forge-defaults.md`
2. Inferir pelo `origin` (`gitlab.com` / `github.com` / `dev.azure.com` / host self-hosted)
3. Se ainda dúbio → **perguntar**: GitLab, GitHub, Azure ou outro?

**Transporte (prioridade):**

1. **MCP** da forge (namespace em defaults ou o disponível no Cursor)
2. **CLI** autenticada: `glab` (GitLab), `gh` (GitHub), `az repos pr` (Azure)
3. Não bloquear só porque a CLI falta se o MCP funciona

Se vários MCPs plausíveis → **perguntar qual usar** e gravar em defaults.

### 3. Source e target

- **Source:** branch atual (ou a que o usuário indicar)
- **Target:**  
  - preferir o que o usuário / defaults / MR|PR existente disserem  
  - **não** confundir upstream da source com target do merge  
  - candidatas comuns: `main`, `master`, `homolog`, `homologacao`, `qas`, `release-candidate`, …  
  - se mais de uma for plausível → **parar e perguntar**

### 4. Tipo de fluxo — perguntar se não estiver nos defaults

1. **Task canônica** — branch de feature/fix direto para o target  
2. **Promoção** — branch temporária a partir do target + merge da task (conflito / “up to date”)  
3. **Task dependente** — incorpora predecessor ainda não no baseline  

Pergunta padrão (se `Promoção: perguntar sempre` ou ausente):

> Precisa de **branch de promoção** (temporária a partir do target), ou o MR|PR sai da branch da task direto?

Só criar branch de promoção / push / MR após oks explícitos.

### 5. Coletar evidência

- `git diff --stat <target>...HEAD`
- `git diff --name-status <target>...HEAD`
- `git log --oneline <target>..HEAD`
- Diffs-chave se necessário

Identificar: objetivo funcional, escopo técnico, riscos, evidência de testes, tipo de branch (canônica / promoção / dependente).

### 6. Issue no título

Se o padrão de título exige `#ISSUE` e não houver evidência confiável → **perguntar** antes de criar.

### 7. Descrição Markdown (obrigatório)

A descrição **deve** seguir o [template padrão](#template-de-descrição) (seções na ordem: Visao Geral, Alteracoes Realizadas, Testes, Issues Relacionadas, Notas Adicionais). Não inventar seções extras no lugar dessas; complementar só dentro de **Notas Adicionais** se preciso.

**Antes de redigir**, buscar MR|PR de referência no mesmo projeto (MCP ou CLI):

1. Listar recentes (merged/opened) no projeto — de preferência para o **mesmo target**, senão qualquer target recente
2. Abrir **2–3** descrições completas (corpo Markdown)
3. Espelhar **tom, densidade e convenções locais** (bullets vs prosa, como citam issue, como falam de testes)
4. O **esqueleto das seções** continua sendo o template padrão desta skill — referências ajustam o *estilo*, não substituem o template
5. Se defaults apontarem IIDs/URLs de exemplos (`MRs de referencia:`), preferir esses

Só afirmar o que a evidência do diff/log ou o usuário sustentam. Declarar incerteza. Não copiar texto de outro MR|PR que não se aplique a este diff.

**Nunca** usar palavras que fecham issue no merge (`Closes`, `Fixes`, `Resolves`, `Implements`, …). Citar só `Issue #N` / `#N`.

### 8. Antes de criar

Listar MR|PR abertos com mesmo source/target (MCP ou CLI) para evitar duplicata e achar o que substituir.

Mostrar ao usuário: forge, source → target, título, se é promoção, se fecha/substitui outro. Pedir ok.

### 9. Criar / atualizar

Via MCP da forge (preferido) ou CLI. Devolver **URL** ao usuário.

Atualizar `.scratch/forge-defaults.md` com o que foi aprendido nesta sessão (forge, MCP, targets, padrão de título, hábito de promoção).

---

## Fluxo de promoção

Quando source for branch temporária baseada no target (sem contaminar a task canônica):

Antes de abrir:

1. Confirmar que a promoção nasceu do remote target certo  
2. Identificar a task canônica mergeada nela  
3. Achar MR|PR direto aberto da task → mesmo target  
4. Comparar task e promoção vs target  
5. Inspecionar merge/resolução de conflito — merge commit ≠ equivalência funcional  
6. Diff = escopo da task + compatibilidade justificada (sem trabalho estranho)

A descrição deve trazer: task + issue, target de ambiente, motivo da promoção, IID/URL substituído, resumo da resolução, evidência de validação, aviso de branch **temporária** (apagar após merge).

Fechar ou marcar o MR|PR direto como substituído para não ficarem duas rotas.

Padrão ilustrativo de criação (só após oks; push só com ok):

```bash
git fetch origin
git switch -c <id>-chore_promocao-<target>-<slug> origin/<target>
git merge --no-ff origin/<branch-task-canonica>
# resolver conflitos + validar
# commit / push / abrir merge — cada um com ok do usuário
```

---

## Task dependente

Se a branch incorpora predecessor ainda não no baseline (`release-candidate` / target):

Incluir na descrição: predecessor (issue, branch, MR|PR, SHA), `blocked by`, ordem de promoção, confirmação de que o target já tem a versão necessária, `squash=false` se identidade de commit importa.

Não apresentar commits do predecessor como escopo da issue dependente se o target já os tem. Se predecessor ausente/desatualizado no target → manter bloqueado e declarar o mismatch.

---

## Sincronização com release-candidate

Merge deliberado de RC na task **não** é contaminação automática. Documentar: origem na RC, baseline atualizado, range de commits, se o target já contém o equivalente, riscos (hotfix, migration, config).

Para targets `qas` / `homologacao`: se a feature carrega conteúdo de RC que o target não tem, não descrever como escopo da task nem incluir em silêncio — bloquear ou seguir estratégia de promoção confirmada. Registrar em **Notas Adicionais**.

---

## Regras de escrita

- Basear claims em evidência do repo ou contexto explícito do usuário  
- Não inventar issues, testes ou breaking changes  
- Declarar incerteza  
- Clareza para o revisor; conciso e técnico  

## Template de descrição (obrigatório)

Todas as seções abaixo devem aparecer, nesta ordem. Preencher com evidência; se não houver dado, declarar explicitamente (não omitir a seção).

```markdown
## Visao Geral

[objetivo funcional + impacto, 2–4 linhas]

## Alteracoes Realizadas

- [mudança relevante]
- Breaking changes identificadas: nenhuma

## Testes

- [evidência real ou "Nenhuma evidencia de execucao de testes encontrada nesta analise."]

## Issues Relacionadas

[Issue #N — nunca Closes/Fixes/Resolves]
[MR|PR substituido / predecessor, se houver]
[ou: Nenhuma issue relacionada identificada nesta analise.]

## Notas Adicionais

- [deploy, migração, riscos, follow-ups, assunções]
- [promoção / RC sync, se aplicável]
```

## Título

Formato (se defaults não disserem outro):

```text
tipo(#ISSUE): descricao
```

Exemplos: `feat(#123): adiciona cadastro de imovel` · `fix(#456): corrige refresh de token`

Sem issue confiável → perguntar antes de criar.

## Erros comuns

- Não criar o MR|PR de fato após o ok  
- Bloquear só porque a CLI falta enquanto o MCP funciona  
- Descrição sem o template padrão; inventar testes; copiar corpo de outro MR|PR sem caber no diff
- Título fora do padrão; inventar número de issue  
- Usar `Closes`/`Fixes`/`Resolves`  
- Feature → `qas`/`homologacao` carregando pacote RC ausente no target  
- Confundir upstream da source com target  
- Push/create sem ok do usuário  

## Checklist final

- [ ] Defaults lidos/atualizados em `.scratch/forge-defaults.md`
- [ ] Forge + MCP/CLI definidos
- [ ] Target claro; promoção perguntada/resolvida
- [ ] 2–3 MR|PR de referência lidos (estilo); descrição no **template padrão** + evidência do diff
- [ ] Título + descrição ok; sem keywords de fechar issue
- [ ] Ok do usuário para push (se preciso) e para create
- [ ] URL devolvida ao usuário
