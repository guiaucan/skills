---
name: revisar-codigo
description: >
  Revisa mudanças desde um ponto fixo (commit, branch, tag ou merge-base) em dois eixos:
  Standards (padrões do repo) e Spec (fidelidade à issue/spec/ticket). Use /revisar-codigo
  ou "revisa desde X".
---

# Revisar código

Revisão em **dois eixos** do diff entre `HEAD` e um ponto fixo:

- **Standards:** o código segue os padrões documentados do repo?
- **Spec:** o código implementa o que a issue/spec/ticket pediu?

Os dois eixos rodam em **subagentes em paralelo** (contextos separados); depois você agrega lado a lado.

Idioma do relatório: **português (Brasil)**, salvo pedido contrário. Nomes dos smells de Fowler podem ficar em inglês (canônicos).

**Git:** esta skill **só revisa**. **Nunca** execute `git commit` nem `git push` (nem “corrigir e commitar”). Se o usuário quiser aplicar sugestões, espere pedido explícito; commit/push continuam proibidos sem novo ok.

Para review de MR/PR/topologia de ambientes (qas/homolog/RC, dependentes), preferir também ou em seguida `/revisar-merge-profundo`.

## Processo

### 1. Fixar o ponto de comparação

O usuário indica o ponto (`main`, `qas`, SHA, tag, `HEAD~5`, …). Se não indicar, **pergunte**.

Capture uma vez:

- Diff: `git diff <ponto>...HEAD` (três pontos = vs merge-base)
- Commits: `git log <ponto>..HEAD --oneline`

Confirme que o ref resolve (`git rev-parse <ponto>`) e que o diff **não** está vazio. Ref inválido ou diff vazio → pare aqui (não dispare subagentes).

### 2. Achar a fonte da Spec

Nesta ordem:

1. Referências a issue nas mensagens de commit (`#123`, `Closes #45`, chave Jira, etc.) — buscar no tracker se configurado
2. Path que o usuário passou
3. Arquivo em `.scratch/specs/`, `.scratch/issues/`, `docs/`, `specs/` que case com a branch/feature
4. Se nada achar → pergunte. Se o usuário disser que não há spec → eixo Spec **pula** e reporta “sem spec disponível”

Use também `.scratch/CONTEXT.md` / ADRs em `.scratch/docs/adr/` para vocabulário, quando existirem.

### 3. Achar fontes de Standards

Tudo no repo que documente como escrever código (`CODING_STANDARDS.md`, `CONTRIBUTING.md`, rules em `.cursor/rules/`, etc.).

Além disso, o eixo Standards **sempre** carrega a **baseline de smells** abaixo (Fowler, _Refactoring_, cap. 3), mesmo sem docs no repo:

- **O repo manda.** Padrão documentado do projeto ganha; se o doc endossa o que a baseline flagraria, suprima o smell.
- **Sempre julgamento.** Smell = heurística (“possível Feature Envy”), nunca violação dura só por baseline. Ignore o que o tooling já enforce (linter/formatter).

Smells (*o que é* → *como corrigir*):

- **Mysterious Name** — nome que não revela o que faz/guarda → renomear; se não houver nome honesto, o desenho está turvo
- **Duplicated Code** — mesma forma de lógica em mais de um hunk/arquivo → extrair e reutilizar
- **Feature Envy** — método usa mais dados de outro objeto que os próprios → mover para perto dos dados
- **Data Clumps** — mesmos campos/params viajam juntos → virar um tipo
- **Primitive Obsession** — primitivo no lugar de conceito de domínio → tipo pequeno próprio
- **Repeated Switches** — mesmo `switch`/`if` no mesmo tipo em vários sítios → polimorfismo ou um mapa compartilhado
- **Shotgun Surgery** — uma mudança lógica espalha edits em muitos arquivos → reunir no mesmo módulo
- **Divergent Change** — um módulo muda por motivos não relacionados → dividir
- **Speculative Generality** — abstração/hooks sem pedido da spec → remover até haver necessidade real
- **Message Chains** — `a.b().c().d()` demais → esconder atrás de um método
- **Middle Man** — classe/função só delega → cortar e chamar o alvo
- **Refused Bequest** — subtipo ignora quase tudo que herda → composição em vez de herança

Extras da baseline (também julgamento; tooling/linter do repo manda se já cobrir):

- **Hardcoded / Magic Value** — literal opaco no meio da lógica (número/string/URL/timeout/path) cujo significado não é óbvio no contexto → extrair constante nomeada, config ou tipo de domínio. **Não** flagar literais triviais óbvios (`0`, `1`, `-1`, `true`/`false`, `""`, `[]` vazios) nem o que já é dado de teste/fixture claramente local.
- **Missing Const** — valor que não muda após atribuição mas não está imutável/`const`/`final`/`readonly` (conforme o idioma e o estilo do repo) → tornar imutável. Só reportar se o projeto/linguagem usa essa convenção de forma clara; não inventar regra onde o código base não a segue.

### 4. Disparar os dois subagentes em paralelo

**Prompt Standards** deve incluir:

- Comando do diff + lista de commits
- Lista de arquivos de padrão achados no passo 3, **mais a baseline de smells colada por completo** (o subagente não tem outra fonte)
- Brief: “Reporte, por arquivo/hunk quando couber, cada achado no formato: **Problema** (1 frase) + **Sugestão** (próximo passo concreto). Cubra (a) violações de padrão documentado: cite arquivo + regra; (b) smells da baseline (incl. Hardcoded/Magic Value e Missing Const): nome + cite o hunk. Separar violações duras de julgamentos (smells). Padrão do repo sobrescreve baseline. Ignorar o que tooling já cobre e literais triviais. Menos de 400 palavras. Em português.”

**Prompt Spec** deve incluir:

- Comando do diff + lista de commits
- Path ou conteúdo da spec/ticket
- Brief: “Reporte cada achado no formato: **Problema** (1 frase) + **Sugestão** (próximo passo concreto). Cubra (a) requisitos faltando ou parciais; (b) scope creep; (c) implementado mas errado. Cite a linha da spec em cada achado. Menos de 400 palavras. Em português.”

Se não houver spec, pule o subagente Spec e anote no relatório final.

### 5. Agregar

Mostre sob `## Standards` e `## Spec`, quase literal. **Não** misture nem ranqueie achados entre eixos.

Cada finding no relatório final deve permanecer como **Problema** + **Sugestão** (não só o diagnóstico).

Feche com **uma linha** de resumo: total de achados por eixo e o pior de *cada* eixo (se houver). Não escolha um “vencedor” entre eixos.

## Por que dois eixos

- Segue todos os padrões mas implementa a coisa errada → Standards ok, Spec falha  
- Faz exatamente o pedido mas quebra convenções → Spec ok, Standards falha  

Separar evita um eixo mascarar o outro.

## Checklist

- [ ] Ponto fixo válido e diff não vazio
- [ ] Spec/ticket localizados (ou Spec pulado com aviso)
- [ ] Standards + Spec em paralelo
- [ ] Relatório em dois eixos; cada finding com **Problema** + **Sugestão**; resumo de uma linha
- [ ] Sem `git commit` / `git push` (review não versiona)
