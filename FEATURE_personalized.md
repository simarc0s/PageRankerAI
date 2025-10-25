# PageRank Personalizado (teleporte enviesado)

## Objetivo

Introduzir um modo de PageRank "personalizado" que favorece páginas de um tópico de interesse. 
Com a flag `--topic-prefix`, o vetor de teleporte (probabilidade de salto) deixa de ser uniforme e passa a 
concentrar probabilidade nas páginas cujos nomes contêm os prefixos fornecidos.

Use isto quando quer dar mais peso a um conjunto de páginas (por tema, palavra‑chave, pasta, etc.).

## Como funciona (intuição)

No PageRank clássico, em cada passo:
- Com probabilidade `d` (damping), segue-se um link a partir da página corrente.
- Com probabilidade `1 - d`, "teleporta-se" para uma página escolhida ao acaso (uniforme sobre todas as páginas).

No modo personalizado, esse teleporte deixa de ser uniforme: passa a usar um vetor `t(p)` que concentra massa nas
páginas cujo nome contém algum dos prefixos dados em `--topic-prefix`. Se nenhuma página corresponder, 
recorre-se a teleporte uniforme para manter o algoritmo bem definido.

## Fórmula

Seja:
- `N` o número de páginas,
- `d` o damping (tipicamente `0.85`),
- `In(p)` o conjunto de páginas que apontam para `p`,
- `L(q)` o número de links de saída da página `q`,
- `Dang` o conjunto de páginas sem links de saída (dangling),
- `S = \sum_{q \in Dang} PR(q)` a massa de PageRank acumulada nos dangling,
- `t(p)` o vetor de teleporte (distribuição de probabilidade, `\sum_p t(p)=1`).

PageRank clássico (teleporte uniforme `t(p)=1/N`):

$$
PR_{new}(p) = \frac{1-d}{N} + d \cdot \sum_{q \in In(p)} \frac{PR(q)}{L(q)} + d \cdot \frac{S}{N}
$$

PageRank personalizado (teleporte enviesado `t(p)`):

$$
PR_{new}(p) = d \cdot \sum_{q \to p} \frac{PR(q)}{L(q)} \;\; + \;\; \big((1-d) + d\,S\big)\, t(p)
$$

Equivalente a redistribuir a massa dos dangling e o teleporte base segundo `t(p)`.

## Construção do vetor de teleporte `t(p)`

- Lê-se `--topic-prefix` como uma lista separada por vírgulas (por exemplo: `ai,logic`).
- Para cada página do corpus, se o nome do ficheiro (ex.: `search.html`) contiver algum dos prefixos (comparação sem distinção
  entre maiúsculas/minúsculas), essa página é marcada como "relevante".
- Se existir pelo menos uma página relevante, `t(p)` é uniforme sobre as relevantes (todas com o mesmo peso e soma 1).
- Se não existir nenhuma relevante, `t(p)` volta a ser uniforme sobre todas as páginas.

Nota: a correspondência é feita apenas sobre o nome do ficheiro, não sobre o conteúdo HTML.

## Utilização

- Teleporte enviesado para um único tópico:

```powershell
python pagerank.py corpus1 --topic-prefix search
```

- Teleporte enviesado para vários tópicos (separados por vírgulas):

```powershell
python pagerank.py corpus2 --topic-prefix ai,logic
```

- Combinar com comparação dos métodos base (amostragem vs. iteração):

```powershell
python pagerank.py corpus1 --topic-prefix search --compare
```

A secção "Personalized PageRank" é impressa adicionalmente; a tabela de `--compare` resume apenas os métodos base.

## Exemplo do que esperar

- As páginas cujo nome combina com os prefixos dados tendem a subir no ranking.
- Páginas não relacionadas podem descer ligeiramente, mas a soma total mantém-se ≈ 1.
- Resultados podem variar conforme o corpus e o damping `d` (por defeito 0.85).

## Validação rápida

- Verificar que a soma das probabilidades é 1 (à 3.ª casa decimal deverá bater certo; tolerância ~1e-6 internamente).
- Comparar com o PageRank padrão (sem `--topic-prefix`): páginas do tópico devem aumentar a sua quota.
- Testes sugeridos:
  - `corpus1` com `--topic-prefix search` (página `search.html` deve ganhar peso).
  - `corpus2` com `--topic-prefix ai,logic` (páginas `ai.html` e `logic.html` favorecidas).
  - Caso sem correspondências (e.g., `--topic-prefix xyz`): deve reproduzir o comportamento padrão (teleporte uniforme).

## Notas, limitações e boas práticas

- Prefixos: separe por vírgulas (recomenda-se sem espaços). A correspondência é uma pesquisa por substring no nome do ficheiro.
- Conteúdo vs. nome: atualmente a seleção baseia-se apenas no nome do ficheiro, não no conteúdo HTML.
- Dangling pages: a massa de dangling é redistribuída segundo o mesmo vetor `t(p)` (personalizado), garantindo convergência.
- Convergência: critério de paragem `max |PR_{new}-PR_{old}| < 0.001`. Pode ajustar no código se precisar de mais rigor.
- Damping `d`: valores mais baixos convergem mais depressa mas reduzem a influência de cadeias de links longas; `0.85` é um padrão robusto.
- Desempenho: para estes corpora académicos é imediato; em grafos muito maiores, considere caches de `In(p)` e estruturas esparsas.
- CSV: a exportação `--csv` contempla os resultados base (amostragem/iteração). O PageRank personalizado ainda não é exportado em CSV.

## Melhorias futuras (ideias)

- Permitir pesos diferentes por tópico (por exemplo, `ai:2,logic:1`).
- Suportar padrões/regex ou listas de páginas a partir de ficheiro externo.
- Incluir o vetor personalizado no método por amostragem (random walk com teleporte enviesado) para comparar abordagens.
- Exportar também o ranking personalizado em CSV.
