# Exportação CSV dos resultados de PageRank

## Visão geral

Esta feature adiciona uma flag simples na linha de comandos para exportar para CSV os resultados de PageRank por Amostragem e por Iteração. Foi pensada para ser mínima, útil e segura em várias plataformas (compatível com Windows: newlines e codificação UTF‑8).

- Flag: `--csv <ficheiro>`
- Colunas: `page, sampling_rank, iterate_rank`
- Ordem: linhas ordenadas pelo nome da página (determinismo)
- Formato numérico: 6 casas decimais (ex.: `0.219777`)
- Codificação: UTF‑8, com `newline=""` (modo texto) para newlines corretos no Windows

## Arranque rápido

```powershell
# Correr o PageRank num corpus e exportar para CSV
python pagerank.py corpus0 --csv ranks.csv

# (Opcional) abrir o CSV no Excel
start-process excel .\ranks.csv
```

## Exemplo de saída

```csv
page,sampling_rank,iterate_rank
1.html,0.217900,0.219777
2.html,0.432200,0.429358
3.html,0.216500,0.219777
4.html,0.133400,0.131088
```

Notas:
- Os valores são probabilidades e cada coluna soma ~1 ao longo de todas as páginas.
- Os resultados por Amostragem variam ligeiramente entre execuções; os de Iteração são determinísticos para o mesmo corpus e fator de amortecimento.

## Dicas para Excel (Windows)

Se o duplo clique não separar as colunas corretamente, importa via separador Dados do Excel:

1. Excel → Dados → Obter Dados → De Ficheiro → De Texto/CSV.
2. Escolhe o ficheiro CSV.
3. Define Origem do ficheiro = UTF‑8 e Delimitador = Vírgula (Comma).
4. Carregar.

Se o teu locale usa vírgula decimal e separador de lista ponto‑e‑vírgula (;), tens duas opções: forçar delimitador = vírgula na importação, ou criar uma variante com ponto‑e‑vírgula:

```powershell
# Conversão rápida para ponto-e-vírgula (seguro aqui: os campos não têm vírgulas)
( Get-Content .\ranks.csv -Raw ) -replace ',', ';' | Set-Content .\ranks_semicolon.csv -Encoding utf8
```

Se vires caracteres estranhos, experimenta uma versão CSV com BOM UTF‑8 (o Excel por vezes prefere):

```powershell
# Adicionar BOM UTF-8 para ajudar o Excel a detetar a codificação
$file = 'ranks.csv'
$out  = 'ranks_with_bom.csv'
[byte[]] $bom = [System.Text.Encoding]::UTF8.GetPreamble()
[byte[]] $bytes = [System.Text.Encoding]::UTF8.GetBytes((Get-Content $file -Raw))
[System.IO.File]::WriteAllBytes($out, $bom + $bytes)
```

## Como funciona

- Usa apenas a biblioteca padrão do Python (`argparse`, `csv`).
- Quando `--csv` é passado:
  - Calcula os ranks por amostragem (n = 10000) e por iteração (d = 0.85), como já fazia.
  - Escreve o cabeçalho do CSV e uma linha por página (ordenadas).
  - Formata valores numéricos com 6 casas decimais.
  - Trata erros de I/O de ficheiro com mensagem clara e saída do programa.

## Validação e testes rápidos

- Corre com um corpus pequeno e verifica que o ficheiro é criado e legível.
- Ao importar com delimitador vírgula, as colunas devem surgir separadas no Excel.
- Para cada método, a soma dos ranks por todas as páginas deve ser ~1.0.

Checks opcionais em PowerShell:

```powershell
# Ver primeiras linhas
Get-Content .\ranks.csv -TotalCount 10

# Soma simples (PowerShell)
$rows = Import-Csv .\ranks.csv
($rows | Measure-Object -Property sampling_rank -Sum).Sum
($rows | Measure-Object -Property iterate_rank  -Sum).Sum
```

## Melhorias futuras

- `--top K` e `--by (sampling|iterate)` para exportar só as páginas mais importantes.
- `--sep (comma|semicolon)` e `--precision N` para controlo de locale/formato.
- `--seed` e `--runs M` para repetição de amostragem com export de média/variância.
- Uma vista `--compare` que exporta também a diferença absoluta entre métodos.
