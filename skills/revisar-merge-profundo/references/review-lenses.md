# Lentes de review

Use depois de coletar o diff e ler o contexto do projeto. Não despeje a lista mecanicamente — pressione a mudança que entra.

## 1. Encaixe no target

- Segue convenções do target para fluxos parecidos?
- Introduz padrão paralelo onde o projeto já tem um estabelecido?
- Aumenta fragmentação entre módulos/camadas?
- Quem vier depois saberá onde esse comportamento vive?

## 2. Legibilidade e nomes

- Nomes revelam intenção, escopo e tempo de vida?
- Booleanos/helpers precisos ou vagos?
- Obriga a simular execução mentalmente?
- Side effects ocultos, acoplamento temporal, abstrações enganosas?

## 3. Complexidade e smells

- Condicionais/flags/camadas desproporcionais?
- Orquestração + validação + persistência + formatação no mesmo lugar?
- Helper/service virou catch-all?
- Duplicação que o MR tocou dos dois lados?
- Generalização especulativa sem call sites?

## 4. Correção, bugs e edge cases

- null, vazio, malformado, parcial, duplicado, stale?
- Dependências externas falhando lento/parcial/surpreendente?
- Paginação, datas, retries, idempotência, concorrência?
- Quebra de contrato/compatibilidade?
- Defaults explícitos e seguros?

Prefira raciocínio por **cenário de falha** nomeado.

## 5. Performance e escala

- N+1, loops quentes, processamento grande em memória, re-fetch desnecessário?
- Caminho realista de disparo (não micro-otimismo teórico)?

## 6. Segurança e exposição de dados

- AuthZ/AuthN em todos os caminhos relevantes?
- Input cruzando trust boundary sem validação?
- Secrets/PII em log ou resposta?
- Fronteiras de tenancy/ownership enfraquecidas?
- Falhas vazando estrutura interna?

## 7. Arquitetura e desenho

- Cada camada ainda dona de um tipo de responsabilidade?
- Lógica de negócio vazando para controller/view/hook/repo?
- Interfaces largas/vazadas?
- Novo acoplamento que espalha mudança futura?

## 8. Testes e verificação

- Qual comportamento mudou e ficou desprotegido?
- Caminho de regressão importante sem teste?
- Precisa unitário, integração, contrato, e2e?
- Paths negativos, permissão, fronteiras de dado?

## 9. Questionar decisões

Questionamento quando há alternativa plausível com melhores fronteiras, abstração prematura, correto mas inconsistente com a arquitetura local, ou custo futuro sem falha imediata. Compare trade-offs; não implique que o autor “está errado”.
