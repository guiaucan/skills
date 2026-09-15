---
name: revisar-merge-profundo
description: >
  Review profundo do que entra na branch de destino (MR/PR ou branch local vs base):
  sync de ambientes, features dependentes, riscos de arquitetura, regressões e lacunas de teste.
  Use /revisar-merge-profundo, "deep review", ou review de MR/PR/branch vs qas/main.
disable-model-invocation: true
---

# Revisar merge (profundo)

Revisa o **conjunto que entra no target**, não o repositório no abstrato.  
Julgue cada mudança pelo pouso na branch de destino, pelos padrões do projeto e pelo risco no tempo.

Idioma: **português (Brasil)**, salvo pedido contrário.

**Git:** só inspeção e relatório. **Nunca** `git commit` / `git push` / criar MR|PR nesta skill. Correções só com pedido explícito (e commit/push continuam com ok separado).

## Relação com as outras skills

| Skill | Papel |
|-------|--------|
| `/revisar-codigo` | Standards + Spec/ticket (bom em chat limpo pós-implement) |
| `/revisar-merge-profundo` | Risco no **target**, topologia de branches, questionamentos de arquitetura |
| `/abrir-merge` | Abrir MR/PR depois (opcionalmente após este review) |

Podem rodar em sequência; não substituem uma à outra.

## Defaults

Resolver `$WORK` conforme [../work-path.md](../work-path.md): `.scratch-id` → slug `origin` → se sem origin, perguntar e **oferecer** criar `.scratch-id`.

Ler `$WORK/forge-defaults.md` se existir (targets, forge, MCP, promoção sim/não).  
Contexto coletado → preferir gravar em **`$WORK/review-context.md`**.

---

## Fluxo

### 1. Resolver o alvo do review

- URL de **GitLab MR** ou **GitHub PR** → inspecionar esse merge  
- Sem URL → **branch atual vs base** (usuário indica, ou defaults, ou pergunta: `qas`, `main`, …)

### 2. Determinar a branch target

- Preferir `target_branch` / base do MR|PR  
- Local: base pedida ou default do remote (`origin/HEAD`)

### 3. Coletar só o que esse merge/diff introduz

Usar o script (recomendado):

```bash
# MR/PR — --output com path absoluto sob $WORK
python skills/revisar-merge-profundo/scripts/collect_review_context.py --mr-url "<url>" --output "$WORK/review-context.md"

# Branch local vs base
python skills/revisar-merge-profundo/scripts/collect_review_context.py --base-branch qas --output "$WORK/review-context.md"
```

`$WORK` = `~/.agents/work/<marca>/` (path absoluto no SO atual). Se o path da skill no ambiente for outro (`~/.agents/skills/...`), ajuste o caminho do script.

**Preferência de coleta:** MCP da forge (se disponível) **ou** script (`glab`/`gh`/git). Se CLI falhar, cair para git local e declarar a limitação.

Classificar a source: feature canônica cumulativa, feature dependente, promoção (se o projeto usar), ou branch ordinária — **antes** de atribuir commits/escopo.

### 4. Reconstruir contexto local

Ler módulos vizinhos, testes das áreas tocadas, docs/convenções só se relevantes.  
Comparar padrões novos com o que o **target** já faz.

Lentes detalhadas: [references/review-lenses.md](references/review-lenses.md).  
Problema vs questionamento: [references/problem-vs-question.md](references/problem-vs-question.md).

### 5. Duas lentes

- **Local:** nomes, legibilidade, complexidade, bugs, edge cases, perf, segurança, validação, SOLID, coesão  
- **Sistema:** consistência com o target, fronteiras, extensibilidade, ownership, pattern drift, integração, testes  

### 6. Separar

- **Problema** — risco concreto, regressão, inconsistência, custo  
- **Questionamento** — decisão discutível (arquitetura/produto)  
Intuição sem evidência → vira questionamento ou some.

### 7. Follow-ups concretos

Mudanças de código, direção de refactor, padrões, cenários de teste.  
Oportunidades só se melhorarem manutenção/flexibilidade/segurança de forma material.

---

## Sync cumulativo de ambientes

Fluxo típico: `release-candidate → feature`, depois MRs diretos `feature → qas` / `homologacao` / de volta a `release-candidate`.

Se **`$WORK/forge-defaults.md`** disser que o projeto usa **branch de promoção**, revise também a topologia de promoção (ver `/abrir-merge`); não assuma “nunca há promoção”.

Merges `qas|homologacao|release-candidate → feature` = sync/resolução de conflito só quando esse ambiente é o **target do MR atual** — não são a direção de promoção.

Verificar (quando aplicável):

- feature nasceu de `release-candidate` (ou baseline declarado)  
- sync veio do target do MR conflitante  
- direção `target → feature canônica`  
- MR direto permanece `feature → target`  
- resoluções de conflito na feature canônica (ou na promoção, se for o caso)  
- `squash=false` se ancestrais importam entre ambientes  

Classificar escopo efetivo: issue nominal, predecessores declarados, herdado do ambiente, resolução de conflito. Ancestralidade sozinha ≠ equivalência — comparar símbolos, conteúdo final, contratos, migrations, config, testes.

---

## Feature dependente

Quando a task incorpora predecessor explícito ainda fora do baseline:

- baseline correto; só predecessores declarados  
- issue/branch/MR/SHA do predecessor documentados  
- target já contém o predecessor **ou** o MR declara escopo acoplado  
- ordem predecessor-first; `squash=false` se identidade de commit importa  
- bloquear/desacoplar se predecessor rejeitado ou removido  

Atribuir commits: predecessor → predecessor; só target → baseline; delta de conflito → integração; só o delta da task dependente → essa issue.

---

## Contrato de saída (sempre nesta ordem)

### 1. Problemas

Para cada um:

- `Severidade`: `baixa` | `media` | `alta` | `critica`  
- `Categoria`  
- `Titulo`  
- `Evidencia`  
- `Impacto` (no target)  
- `Correcao sugerida`  
- `Discussao`  

### 2. Questionamentos validos

- `Tema` · `Por que vale questionar` · `O que validar` · `Quando manter` · `Quando mudar`

### 3. Cobertura de testes sugerida

Cenários concretos (edge, regressão, contrato, falha, auth, concorrência…).

### 4. Oportunidades de melhoria

Só se houver ganho material (refactor alvo, padrão, simplificação, fronteira).

Guia de severidade: `critica` (outage/exploit/corrupção) → `alta` → `media` → `baixa`.

Preferir poucos achados de alto sinal. Nits de estilo só se afetarem legibilidade/correção/manutenção/consistência.

## Checklist

- [ ] Target definido (MR/PR ou `--base-branch`)
- [ ] Contexto em `$WORK/review-context.md` (ou stdout) + código ao redor lido
- [ ] Relatório: Problemas + Questionamentos + Testes (+ Melhorias se couber)
- [ ] Sem commit/push
