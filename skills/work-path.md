# Artefatos locais (`work`)

Contrato compartilhado por todas as skills deste pacote.

## Raiz

Artefatos **não** ficam no repositório do projeto.

```
<home>/.agents/work/<marca>/
```

| SO | `<home>` |
|----|----------|
| Windows | `%USERPROFILE%` (ex. `C:\Users\<user>`) |
| macOS / Linux | `$HOME` |

Use path **absoluto** depois de resolver (evita erro de navegação entre SOs). Em scripts: `pathlib.Path.home() / ".agents" / "work" / marca`.

Crie a pasta se não existir.

## Marca do projeto

Ordem **somente**:

1. Arquivo **`.scratch-id`** na raiz do repo (primeiro linha, trim). Se existir → use como `<marca>` (sanitizar).
2. Senão → slug do **`origin`**: `owner/repo` → `owner-repo` (trocar `/` por `-`; remover `.git`; sanitizar caracteres inválidos em nome de pasta).
3. Se **não houver** `origin` utilizável → **pergunte** um id curto ao usuário e **ofereça gravar** `.scratch-id` na raiz do repo com esse valor (só grave com ok explícito). Não invente `default` / `_unnamed`.

`.scratch-id` pode ser versionado (só o id; sem artefatos). Não confundir com a pasta antiga `.scratch/` no projeto.

## Layout sob `$WORK`

`$WORK` = `<home>/.agents/work/<marca>/`

| Artefato | Path |
|----------|------|
| Glossário | `$WORK/CONTEXT.md` |
| Mapa | `$WORK/CONTEXT-MAP.md` |
| ADRs | `$WORK/docs/adr/` |
| Specs | `$WORK/specs/` |
| Tickets | `$WORK/issues/` |
| Plano / grill | `$WORK/plano.md` |
| Forge defaults | `$WORK/forge-defaults.md` |
| Review context | `$WORK/review-context.md` |

## Legado

Se existir **`.scratch/`** dentro do projeto com artefatos antigos → avise e ofereça **`/migrar-work`** (migra para `$WORK` sem reescrever o conteúdo; não apague sozinho).

## Git

Não versionar o conteúdo de `$WORK`. Não `git add` de artefatos locais sem pedido. Commit/push só com ok explícito.
