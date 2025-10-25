# Comparação entre métodos de PageRank (Sampling vs Iteration)

## Objetivo

Adicionar uma vista simples de comparação entre os resultados do PageRank obtidos por Amostragem (Sampling) e por Iteração (Iteration), para perceber rapidamente onde divergem e em que magnitude.

## Como usar

```powershell
# Mostrar a tabela de comparação e um resumo
python pagerank.py <pasta_do_corpus> --compare

# Opcional: filtrar por diferença mínima absoluta
python pagerank.py <pasta_do_corpus> --compare --diff-threshold 0.002
```

- `--compare`: ativa a vista de comparação.
- `--diff-threshold <valor>`: mostra apenas as páginas cuja diferença absoluta |sampling - iterate| é maior ou igual ao valor indicado. Útil para focar onde há divergência relevante.

## O que é mostrado

- Uma tabela ordenada por diferença absoluta (descendente) com as colunas:
  - `page`: nome da página
  - `sampling`: PageRank por amostragem
  - `iterate`: PageRank por iteração
  - `abs_diff`: |sampling − iterate|
- Um resumo no final com:
  - `max_diff`: maior diferença absoluta
  - `mean_diff`: média das diferenças absolutas

Se for usado `--diff-threshold`, o cabeçalho indica o threshold aplicado e a razão `mostradas/total`.

## Exemplo (corpus0)

```text
Comparison: Sampling vs Iteration
page      sampling     iterate    abs_diff (threshold: 0.002000; shown 4/4)
----------------------------------------------------------------------
2.html    0.434000    0.429358    0.004642
4.html    0.127000    0.131088    0.004088
3.html    0.217000    0.219777    0.002777
1.html    0.222000    0.219777    0.002223

Summary: max_diff = 0.004642, mean_diff = 0.003433
```

Notas:
- Os valores por amostragem variam ligeiramente entre execuções (processo estocástico). Os valores por iteração são determinísticos para o mesmo corpus e damping.
- A soma dos ranks de cada método é ~1 (pequenas variações numéricas são normais).

## Validação rápida

- Confirmar visualmente que as colunas `sampling` e `iterate` coincidem com as listagens anteriores do próprio programa.
- Verificar que a tabela está ordenada por `abs_diff` desc.
- Se usar `--diff-threshold`, confirmar que só aparecem linhas com diferença ≥ ao valor indicado.

## Melhorias futuras

- Permitir ordenar por colunas alternativas (ex.: por `sampling` ou `iterate`).
- Exportar a tabela de comparação para CSV (ex.: `--compare-csv <ficheiro>`).
- Mostrar apenas as `top K` maiores diferenças (ex.: `--top 10`).
