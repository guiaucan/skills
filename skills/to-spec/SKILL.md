---
name: to-spec
description: >
  Transforma a conversa atual em uma spec e grava em .scratch/specs/.
  Sem entrevista — só síntese do que já foi discutido. Use /to-spec.
disable-model-invocation: true
---

# Para spec

Sintetiza o contexto da conversa (e do código, se já explorado) numa **spec**. **Não** entreviste o usuário; sintetize o que já sabe.

Idioma: **português (Brasil)**, salvo pedido contrário.

## Onde gravar

| Artefato | Path |
|----------|------|
| Spec | `.scratch/specs/<slug>.md` |
| Glossário (ler) | `.scratch/CONTEXT.md` |
| ADRs (respeitar) | `.scratch/docs/adr/` |

Garanta que `.scratch/` está no `.gitignore` do projeto.

**Git:** **nunca** execute `git commit` nem `git push` sozinho. **Nunca** `git add`/commit de `.scratch/` (nem de outros artefatos locais) sem o usuário pedir explicitamente.

Se o usuário pedir publicação num tracker (GitHub/Linear), use o tracker; senão o padrão é **arquivo local** acima.

## Processo

1. **Explorar o repo** (se ainda não fez). Use o vocabulário do glossário (`.scratch/CONTEXT.md`) e respeite ADRs em `.scratch/docs/adr/`.

2. **Esboçar as seams de teste** da feature. Prefira seams existentes. Use a seam mais alta possível. Ideal: poucas seams (no limite, uma).  
   Confirme com o usuário se essas seams batem com a expectativa dele.

3. **Escrever a spec** com o template abaixo e gravar em `.scratch/specs/<slug>.md` (slug curto em kebab-case). Marque status mental `ready-for-agent`.

## Template da spec

```md
# <Título curto>

**Status:** ready-for-agent

## Problema

O problema do ponto de vista do usuário.

## Solução

A solução do ponto de vista do usuário.

## User stories

Lista LONGA e numerada. Formato:

1. Como <ator>, quero <capacidade>, para <benefício>

Cubra todos os aspectos relevantes da feature.

## Decisões de implementação

Lista do que foi decidido, por exemplo:

- Módulos a criar/alterar
- Interfaces desses módulos
- Esclarecimentos técnicos
- Decisões arquiteturais
- Mudanças de schema
- Contratos de API
- Interações específicas

**Não** inclua paths de arquivo nem snippets de código (envelhecem rápido).

Exceção: se um protótipo gerou um trecho que captura a decisão melhor que prosa (state machine, reducer, schema, shape de tipo), inclua só a parte rica em decisão e note que veio de protótipo.

## Decisões de teste

- O que é um bom teste (comportamento externo, não detalhes internos)
- Quais módulos serão testados
- Prior art no repo (tipos de teste parecidos)

## Fora de escopo

O que esta spec **não** cobre.

## Notas

Qualquer nota adicional.
```

## Checklist

- [ ] Spec em `.scratch/specs/`
- [ ] Vocabulário do glossário
- [ ] Seams confirmadas com o usuário
- [ ] Sem `git commit` / `git push` autônomos; sem versionar `.scratch/` sem pedido
