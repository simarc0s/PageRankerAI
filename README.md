# PageRankerAI (CS50 PageRank)

## Introdução
Este projeto implementa o algoritmo PageRank sobre pequenos conjuntos (corpora) de páginas HTML (fornecidos pela CS50), com duas abordagens: por amostragem (random walk) e por iteração (equações de ponto fixo). Foi desenvolvido como trabalho académico para a unidade curricular de Inteligência Artificial, cobrindo técnicas de modelação de grafos, probabilidades e convergência numérica.

O projeto inclui funcionalidades extra que facilitam análise e apresentação de resultados:
1. Destaque simples: exportação para CSV (`--csv`)
2. Comparação regular: tabela de diferenças entre amostragem e iteração (`--compare`, `--diff-threshold`)
3. PageRank Personalizado: teleporte enviesado por tópico (`--topic-prefix`)

## Descrição
O PageRank atribui a cada página uma probabilidade de estar a ser visitada por um "surfer" de links. Existem dois métodos implementados:

- Amostragem: simula um passeio aleatório por `n` passos (a partir de uma página aleatória), seguindo a distribuição de transição com damping `d`.
- Iteração: resolve iterativamente o sistema até convergência, combinando contributos de links de entrada e massa de páginas sem saída (dangling), mais teleporte uniforme `1-d`.

Características principais:
- Implementação clara das funções `crawl`, `transition_model`, `sample_pagerank` e `iterate_pagerank`
- Tratamento correto de páginas sem links (dangling)
- Convergência por iteração com critério `max |Δ| < 0.001`
- Exportação para CSV e comparação entre métodos

## Como correr
### Requisitos
- Python 3.8 ou superior (stdlib apenas)

### Execução básica
```powershell
# Amostragem e iteração no corpus0 (mostra resultados de ambos)
python pagerank.py corpus0
```

### Exportar resultados para CSV
```powershell
# Guarda um CSV com colunas: page, sampling_rank, iterate_rank
python pagerank.py corpus1 --csv ranks_corpus1.csv
```

### Comparar amostragem vs. iteração
```powershell
# Mostra tabela ordenada por diferença absoluta
python pagerank.py corpus2 --compare

# Filtrar para diferenças significativas (≥ 0.002)
python pagerank.py corpus2 --compare --diff-threshold 0.002
```

### PageRank Personalizado
Para usar o teleporte enviesado por tópico:
```powershell
# Exemplo: favorecer páginas cujo nome contenha "search"
python pagerank.py corpus1 --topic-prefix search
```
Consulte `FEATURE_personalized.md` para detalhes, fórmulas e exemplos adicionais.

## Flags principais
- `--csv <ficheiro>`: exporta resultados base (amostragem e iteração)
- `--compare`: imprime tabela com diferenças entre métodos
- `--diff-threshold <float>`: quando usado com `--compare`, filtra por diferença mínima
- `--topic-prefix <lista>`: teleporte enviesado por substrings (separadas por vírgulas) no nome das páginas

## Estrutura do projeto
```
pagerank/
├── pagerank.py                 # Script principal: crawl, transition_model, sample, iterate, CLI
├── corpus0/                    # Corpus de teste (pequeno)
├── corpus1/                    # Corpus de teste (médio)
├── corpus2/                    # Corpus de teste (médio)
├── FEATURE_export_csv.md       # Doc. da feature CSV (simples)
├── FEATURE_compare.md          # Doc. da feature Compare (regular)
└── FEATURE_personalized.md     # Doc. da feature Personalized (branch de feature)
```

### Ficheiro principal
- `pagerank.py`
  - `crawl(directory)`: lê HTMLs, extrai links internos e constrói o grafo
  - `transition_model(corpus, page, d)`: distribuição de transição com damping e tratamento de dangling
  - `sample_pagerank(corpus, d, n)`: random walk de `n` passos; devolve distribuição normalizada
  - `iterate_pagerank(corpus, d)`: iteração até convergência com dangling e teleporte uniforme
  - CLI com `argparse` e flags `--csv`, `--compare`, `--diff-threshold`

## Ferramentas de IA utilizadas
Projeto desenvolvido com assistência pontual do GitHub Copilot como par de programação.
Contribuiu sobretudo para decompor tarefas, sugerir snippets e rever documentação.
As decisões de arquitetura, implementação final e validação foram realizadas manualmente.

## Exemplos de prompts e outputs

### Exemplo 1: Exportação CSV (feature simples)
Prompt:
> "Adicionar flag --csv que exporta page,sampling_rank,iterate_rank em UTF‑8, com 6 casas decimais."

Output (resumo):
- Flag `--csv` no CLI e escrita via `csv.writer`
- Ficheiro `ranks_corpus1.csv` com cabeçalho e valores normalizados

### Exemplo 2: Comparação (feature regular)
Prompt:
> "Criar --compare que imprime tabela ordenada por diferença absoluta; incluir --diff-threshold para filtrar."

Output ilustrativo:
```
Comparison: Sampling vs Iteration
page        	  sampling    	   iterate   	  abs_diff
bfs.html    	   0.152300   	   0.150900   	   0.001400
...
Summary: max_diff = 0.003200, mean_diff = 0.001100
```
(Valores meramente exemplificativos; a forma e a ordenação correspondem ao comportamento real.)

### Exemplo 3: Personalized PageRank (feature complexa, em branch)
Prompt:
> "Adicionar --topic-prefix que constrói vetor de teleporte enviesado a partir de substrings do nome dos ficheiros."

Output (resumo):
- CLI com `--topic-prefix` e cálculo iterativo com `t(p)` (ver `FEATURE_personalized.md`)
- Páginas com nomes relevantes aumentam a sua probabilidade; soma total ≈ 1

### Exemplo 4: Explicação do código
Prompt:
> "Explicar linha a linha as funções main e crawl, incluindo regex e filtragem de links internos."

Output (resumo):
- Comentários e explicações sobre extração com regex e normalização do grafo

## Controlo de versão e organização
Exemplo de workflow (PowerShell):
```powershell
# Branches de features
git checkout -b feature/export_csv
# ... commits ...
git checkout -b feature/compare
# ... commits ...
git checkout -b feature/personalized_pagerank

# Commits convencionais
git commit -m "feat(csv): adicionar flag --csv e escrita de ficheiro"
git commit -m "feat(compare): imprimir tabela e resumo de diferenças"
```

## Notas técnicas
- Convergência: critério `max |PR_new - PR_old| < 0.001`; ajustável no código
- Aleatoriedade: amostragem depende de `random`; para reprodutibilidade pode definir seed no topo do script
- Dangling: massa redistribuída uniformemente (main); na feature Personalized é redistribuída por `t(p)`
- CSV: exporta apenas resultados base (amostragem/iteração) na branch main
- Windows PowerShell: os comandos acima estão prontos a usar (sem redirecionadores tipo heredoc)

## Futuras melhorias
- Exportar também o ranking personalizado para CSV
- Permitir personalização na amostragem (teleporte enviesado no random walk)
- Otimizações de iteração (estruturas esparsas e caches de `In(p)`)
- Testes automatizados e relatório de cobertura

## Autores
**Simão Marcos**, **Abel Dias**

Projeto académico desenvolvido com assistência de GitHub Copilot como ferramenta de pair programming.

## Licença
Projeto académico — uso educacional.
