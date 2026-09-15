---
name: migrar-work
description: >
  Migra artefatos do antigo .scratch/ (na raiz do projeto) para
  ~/.agents/work/<marca>/ sem reescrever o conteúdo. Use /migrar-work
  ou "migra o scratch para work".
disable-model-invocation: true
---

# Migrar `.scratch` → `work`

Move (ou copia) o legado **`.scratch/`** do repositório para **`$WORK`**, preservando nomes e conteúdo. Não reescreve specs, tickets, glossário nem ADRs.

Idioma: **português (Brasil)**, salvo pedido contrário.

Contrato de path: [../work-path.md](../work-path.md).

**Git:** pode inspecionar. **Nunca** `git commit` / `git push` sozinho. Apagar `.scratch/` ou gravar `.scratch-id` só com ok explícito.

---

## Fluxo

### 1. Localizar origem

- Procurar **`.scratch/`** na raiz do git (ou do workspace).
- Se não existir → informar e encerrar (nada a migrar).
- Listar o que há (árvore resumida: `CONTEXT.md`, `specs/`, `issues/`, `docs/adr/`, `forge-defaults.md`, `plano.md`, `review-context.md`, outros).

### 2. Resolver `$WORK` (marca)

Conforme [work-path.md](../work-path.md):

1. `.scratch-id` na raiz → `<marca>`
2. Senão slug do `origin` (`owner-repo`)
3. Senão **perguntar** id curto e **oferecer** criar `.scratch-id` (só grave com ok)

Raiz: `<home>/.agents/work/<marca>/` — path **absoluto**, home do SO atual.

Mostrar ao usuário: origem → destino.

### 3. Plano de migração

Para cada arquivo/pasta sob `.scratch/`:

| Destino relativo | Ação |
|------------------|------|
| Mesmo path relativo em `$WORK` | migrar |

Ex.: `.scratch/CONTEXT.md` → `$WORK/CONTEXT.md`  
`.scratch/issues/01-foo.md` → `$WORK/issues/01-foo.md`

**Conflito** (destino já existe):

- Comparar (tamanho/hash ou diff curto).
- Se idênticos → pular (já migrado).
- Se diferentes → **perguntar**: manter destino, sobrescrever com origem, ou salvar origem como `*.from-scratch` ao lado.

Não inventar merge de Markdown.

### 4. Executar (após ok)

Preferir o script do pacote (path absoluto no SO):

```bash
python <path-da-skill>/scripts/migrate_scratch_to_work.py --repo-root <raiz-do-repo> --marca <marca>
```

Flags úteis:

- `--dry-run` — só listar o que faria (use antes do ok, se quiser)
- `--copy` — copiar em vez de mover
- `--force` — sobrescrever destino sem perguntar (**só** se o usuário pediu)

Se o script não estiver disponível: copiar/mover com tools do agente (`pathlib`/shell), mesma regra de conflitos.

Criar `$WORK` e subpastas conforme precisar.

### 5. Pós-migração

1. Conferir que os arquivos críticos estão em `$WORK` (pelo menos o que existia na origem).
2. Perguntar se apaga **`.scratch/`** no projeto (default sugerido: sim, depois de conferir).
3. Se ainda não houver `.scratch-id` e o usuário topou → gravar a `<marca>` usada.
4. Lembrar: próximas skills usam `$WORK`; `.scratch/` antigo não deve ser recriado.

### 6. Checklist

- [ ] Origem `.scratch/` encontrada (ou early-exit)
- [ ] `$WORK` resolvido (id / origin / pergunta)
- [ ] Conflitos tratados com o usuário
- [ ] Conteúdo em `$WORK` (sem reescrita)
- [ ] Ok antes de apagar `.scratch/` / gravar `.scratch-id`
- [ ] Sem commit/push autônomos
