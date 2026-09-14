---
name: implement
description: >
  Implementa o trabalho descrito numa spec ou ticket. Use /implement.
  TDD só se o projeto/usuário pedirem e seams forem confirmadas; sem commit autônomo.
disable-model-invocation: true
---

# Implementar

Implemente o trabalho da **spec** ou do **ticket** indicado pelo usuário.

Idioma: **português (Brasil)**, salvo pedido contrário.

## Entradas (ler)

| Fonte | Path típico |
|-------|-------------|
| Ticket | `.scratch/issues/<NN>-….md` |
| Spec | `.scratch/specs/<slug>.md` |
| Glossário | `.scratch/CONTEXT.md` |
| ADRs | `.scratch/docs/adr/` |

Use o vocabulário do glossário. Não invente escopo fora da spec/ticket.

## Processo

1. **Plano curto** em bullets (o que vai fazer).
2. **Branch (antes de codar)** — sugerir criar branch de trabalho; **não** criar sem ok do usuário. Ver seção abaixo.
3. **Repo-first:** mimetize o estilo do projeto; mude só o necessário.
4. **Testes / TDD**
   - Se o projeto **não** tem cultura/suite de testes → **não** force TDD; use as checagens que o repo já tiver (lint, build, smoke).
   - Se tem testes / o usuário quer TDD → combine **seams** antes; nenhum teste em seam não confirmada; ciclo vermelho → verde, uma fatia por vez.
5. Rode typecheck/lint e testes relevantes no caminho; suite completa (ou o equivalente do repo) no fim.
6. **Self-review** (e `/revisar-codigo` e/ou `/revisar-merge-profundo` se existirem e o usuário quiser).
7. **No final da sessão:** bloco **Sugestão de commit** (ver formato abaixo).  

**Git (regra absoluta):** **nunca** execute `git commit` nem `git push` sozinho — só sugira a mensagem e espere ok explícito do usuário. **Nunca** incluir `.scratch/` (nem `git add` dele) sem pedido explícito. Criar branch só depois do ok (ver seção Branch).

### Branch — o que perguntar / inferir

Antes de escrever código, apresente uma **Sugestão de branch** com: origem, nome proposto (padrão do repo + ID se aplicável) e o comando equivalente.

Depois pergunte explicitamente:

> Quer que eu crie a branch com esse nome a partir de `<origem>`?

- **Sim** → criar a branch (ou orientar o comando se o usuário preferir rodar).
- **Não / outro nome** → peça o nome desejado (ou aceite o que ele mandar), ajuste e confirme de novo antes de criar.
- **Já estou na branch certa** → pule a criação e siga.

Como montar a sugestão inicial:

1. **Origem (base)** — inferir de branches/`docs`; se dúbio, perguntar (`main`, `qas`, …).
2. **Padrão de nome** — docs → `git branch -a` → se não houver padrão, perguntar.
3. **ID** — da issue/ticket/spec; se o padrão exigir e não estiver claro, perguntar.

Não criar branch sem o ok explícito do usuário (nem com o nome sugerido, nem com o nome alternativo).

### Como escolher o formato da mensagem de commit

Nesta ordem:

1. Docs do projeto (`CONTRIBUTING`, commitlint, `.commitlintrc*`, README)
2. Estilo dos commits recentes (`git log --oneline -10`)
3. Fallback: **Conventional Commits** (`feat(scope): …`, `fix(scope): …`, …)

## Diretrizes

- Menos é mais; sem over-engineering; sem antecipar o futuro.
- Sem alucinação: falta info → pare e pergunte.
- Código limpo, nomes claros, sem comentários redundantes.
- Erros: só onde o risco for real; guard clauses simples.

## Checklist

- [ ] Spec/ticket + glossário lidos
- [ ] Plano curto mostrado
- [ ] Branch sugerida + pergunta “criar com esse nome?”; se outro nome, usar o do usuário; criar só com ok — ou “já na branch certa”
- [ ] Seams confirmadas **se** houver TDD
- [ ] Validação do repo passou
- [ ] **Sugestão de commit** no final; **nenhum** `git commit`/`git push` sem ok explícito do usuário
