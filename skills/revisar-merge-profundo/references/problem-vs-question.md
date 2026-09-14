# Problema vs Questionamento

## Marque como Problema quando houver

- risco concreto de bug, regressão, quebra de contrato, falha de segurança ou custo operacional
- violação clara de padrão importante do projeto
- complexidade desnecessária que piora manutenção/teste/clareza de forma objetiva
- ausência de cobertura para cenário de risco real introduzido pelo MR/diff
- evidência suficiente para recomendar correção direta

## Marque como Questionamento quando houver

- mais de uma solução plausível (critério arquitetural)
- suspeita de abstração prematura / fronteira ruim / pattern drift sem dano imediato comprovado
- decisão que pode dificultar extensão futura, sem falha concreta ainda
- dúvida válida sobre ownership ou coerência com o target

## Regras

- Cenário de falha ou custo concreto → tende a **Problema**
- Trade-off → tende a **Questionamento**
- Só preferência pessoal → não levantar
- Risco com evidência fraca → **Questionamento** + o que validar

## Exemplos de Problema

- "O novo fluxo ignora a validação de ownership dos endpoints vizinhos."
- "Consulta extra no loop cria N+1 na listagem."
- "A flag `isComplete` passa a significar duas coisas conforme a origem do dado."

## Exemplos de Questionamento

- "Essa regra deveria viver no service onde as outras regras semelhantes estão?"
- "Essa interface genérica simplifica o domínio ou mascara duas implementações diferentes?"
- "Faz sentido introduzir cache agora sem invalidação clara?"
