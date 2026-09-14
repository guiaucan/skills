---
name: to-tickets
description: >
  Quebra plano, spec ou conversa em tickets tracer-bullet com arestas de bloqueio,
  gravados em .scratch/issues/. Use /to-tickets.
disable-model-invocation: true
---

# Para tickets

Quebre o trabalho em **tickets**: fatias verticais (tracer bullets), cada uma declarando o que a **bloqueia**.

Idioma: **português (Brasil)**, salvo pedido contrário.

## Onde gravar

| Artefato | Path |
|----------|------|
| Tickets | `.scratch/issues/<NN>-<slug>.md` (a partir de `01`, blockers primeiro) |
| Spec de origem (ler) | `.scratch/specs/` ou path que o usuário passar |
| Glossário (ler) | `.scratch/CONTEXT.md` |
| ADRs (respeitar) | `.scratch/docs/adr/` |

`.scratch/` no `.gitignore`.

**Git:** **nunca** execute `git commit` nem `git push` sozinho. **Nunca** `git add`/commit de `.scratch/` (nem de outros artefatos locais) sem o usuário pedir explicitamente.

Padrão = **arquivos locais**. Tracker real (GitHub/Linear) só se o usuário pedir.

## Processo

### 1. Reunir contexto

Use a conversa. Se o usuário passar spec/path/issue, leia o corpo completo.

### 2. Explorar o código (opcional)

Se ainda não explorou, explore. Títulos/descrições no vocabulário do glossário; respeite ADRs.

Procure chance de **prefactor** que facilite a mudança. “Deixe a mudança fácil, depois faça a mudança fácil.”

### 3. Esboçar fatias verticais

Regras:

- Cada fatia corta um caminho **estreito mas completo** por todas as camadas necessárias (não fatia horizontal de uma camada só)
- Fatia concluída é demonstrável/verificável sozinha
- Cabe em **uma** janela de contexto fresca
- Prefactors primeiro

Cada ticket declara **Blocked by**. Sem blockers → pode começar já.

**Exceção — refactor largo:** mudança mecânica com blast radius enorme. Não force tracer bullet; use **expand–contract**: expandir (forma nova ao lado da velha) → migrar em lotes (cada lote um ticket bloqueado pelo expand) → contract (apagar a forma velha, bloqueado por todos os lotes).

### 4. Quiz com o usuário

Lista numerada. Para cada ticket:

- **Título**
- **Blocked by**
- **O que entrega** (comportamento ponta a ponta)

Pergunte: granularidade ok? arestas corretas? fundir/fatiar?

Itere até aprovar.

### 5. Publicar

Só depois da aprovação:

- **Local:** um arquivo por ticket em `.scratch/issues/<NN>-<slug>.md`
- **Tracker:** só se pedido; label `ready-for-agent` se existir

Trabalhe a **fronteira**: tickets cujos blockers já estão feitos.

Não feche/altere issue-pai no tracker sem pedido.

## Template local (um arquivo por ticket)

```md
# <NN>: <Título>

**O que construir:** comportamento ponta a ponta do ponto de vista do usuário (não lista camada a camada).

**Blocked by:** números/títulos que bloqueiam, ou "Nenhum (pode começar já)".

**Status:** ready-for-agent

- [ ] Critério de aceite 1
- [ ] Critério de aceite 2
```

Evite paths de arquivo e snippets (envelhecem). Exceção: trecho de protótipo rico em decisão (state machine, schema, etc.), só o essencial.

## Checklist

- [ ] Breakdown aprovado pelo usuário
- [ ] Arquivos em `.scratch/issues/`
- [ ] Vocabulário do glossário
- [ ] Sem `git commit` / `git push` autônomos; sem versionar `.scratch/` sem pedido
