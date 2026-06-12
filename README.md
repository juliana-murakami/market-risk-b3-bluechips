# Análise de Risco de Mercado nas Maiores Blue Chips da B3

**Dashboard Interativo**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://market-risk-b3.streamlit.app/)

[![Dashboard Preview](dashboard-b3.GIF)](https://market-risk-b3.streamlit.app/)

---

## Resumo dos Resultados

| Métrica | Valor |
|---|---|
| Retorno Total | 276% |
| Volatilidade Anual | 25.8% |
| Sharpe Ratio | 0.65 |
| VaR Histórico (95%) | 2.25% |
| CVaR (95%) | 3.72% |
| Máximo Drawdown | −51.4% |
| Backtesting (Kupiec) | Bem calibrado (p=0.76) |

---

## Principais Insights

- **BPAC11** apresentou o melhor desempenho anualizado: **33.8% a.a.**, mas também o **maior VaR individual entre os ativos (3.80%)** — ilustrando o clássico trade-off risco-retorno.

- **ABEV3** foi o único ativo com retorno anualizado negativo (**−1.3% a.a.**), indicando exposição desfavorável ao contexto macroeconômico do período.

- A carteira apresentou **drawdown máximo de 51.4%**, ocorrido em 23 de março de 2020, no auge da crise da COVID-19 — evidenciando vulnerabilidade significativa a choques sistêmicos globais.

- **CVaR (3.72%) foi significativamente superior a VaR (2.25%)**, indicando que em cenários de crise, as perdas são substancialmente maiores que o percentil de risco sugere. Isso destaca a importância de usar CVaR como métrica primária de risco.

- O **teste de Kupiec confirmou boa calibração do modelo**: 4.84% de exceções observadas vs 5% esperadas (p=0.76). O modelo de VaR histórico não necessita de ajustes.

- A **COVID-19 foi o maior choque do período** para esta carteira (−47.9% em 21 dias), superando até a crise eleitoral de 2022, que registrou retorno positivo de +5.5% no mesmo recorte — mostrando que choques políticos domésticos não impactaram igualmente todos os ativos da carteira.

---

## Metodologia

### Dados e Período

Análise de 2018 a 2025 (1.987 dias úteis) com foco nas cinco maiores ações da B3 por valor de mercado em carteira de pesos iguais (20% cada):

- **PETR4** (Petrobras): +24.7% a.a.
- **ITUB4** (Itaú): +11.7% a.a.
- **VALE3** (Vale): +15.2% a.a.
- **ABEV3** (Ambev): −1.3% a.a.
- **BPAC11** (BTG Pactual): +33.8% a.a.

Benchmark: IBOV

### Retornos

Log-retornos diários para manter propriedades aditivas:

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

Retorno acumulado: $R_{acum} = e^{\sum r_t}$

### Métricas de Risco Implementadas

**VaR Histórico (95%)**: Percentil 5% dos dados observados. Robusto em ambientes com caudas pesadas; não assume distribuição. **Valor: 2.25%**

**VaR Paramétrico (95%)**: Calcula analiticamente assumindo normalidade. Tende a subestimar risco em crises. **Valor: 2.61%**

**CVaR / Expected Tail Loss (95%)**: Perda média nos 5% piores dias. Sempre ≥ VaR. Preferido por reguladores (Basileia III). **Valor: 3.72%**

**Volatilidade Anual**: $\sigma_{anual} = \sigma_{diária} \times \sqrt{252}$ **Valor: 25.8%**

**Sharpe Ratio**: Retorno por unidade de risco. $\text{Sharpe} = \frac{\mu_{anual}}{\sigma_{anual}}$ **Valor: 0.65** *(calculado com taxa livre de risco = 0, como simplificação)*

**Máximo Drawdown**: Queda máxima do pico histórico. **Valor: −51.4%** (23 de março de 2020, durante a crise da COVID-19)

**Validação**: Backtesting de Kupiec compara exceções observadas (4.84%) com esperadas (5%). p-valor = 0.76 indica modelo bem calibrado.

### Cenários de Crise

- **COVID-19 (mar/2020)**: Maior choque do período para esta carteira, com perda de 47.9% em 21 dias. Coincide com o máximo drawdown da carteira (−51.4%, registrado em 23/03/2020), refletindo o pânico global e a incerteza sobre a duração da pandemia.
- **Crise Eleitoral (out/2022)**: Surpreendentemente, a carteira registrou retorno positivo de +5.5% no mesmo recorte de 21 dias, indicando que a composição setorial (forte presença de commodities e setor financeiro) amorteceu o impacto da incerteza política doméstica.

---

## Estrutura do Projeto

```
market-risk-b3-bluechips/
├── README.md
├── requirements.txt
├── analise_risco_bluechips_b3.ipynb    # Notebook com análise completa
├── app.py                              # Dashboard Streamlit interativo
├── dashboard-b3-GIF                      
├── data/
│   ├── raw/
│   └── processed/
└── outputs/
```

---

## Como Executar Localmente

```bash
git clone https://github.com/juliana-murakami/market-risk-b3-bluechips.git
cd market-risk-b3-bluechips
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m streamlit run app.py
```

**Dependências**: yfinance, pandas, numpy, scipy, plotly, streamlit

### Ou explore o notebook Jupyter

```bash
jupyter notebook analise_risco_bluechips_b3.ipynb
```

---

## Dashboard Interativo

O Streamlit oferece:

1. **KPI Cards**: Retorno total, volatilidade, Sharpe, VaR, CVaR, drawdown máximo
2. **Distribuição de Retornos**: Histograma com VaR (histórico e paramétrico) e CVaR
3. **Retorno Acumulado**: Série temporal de cada ativo vs IBOV com marcadores de crises
4. **Drawdown Histórico**: Evolução temporal com períodos de estresse destacados
5. **Comparação de Métodos VaR**: Gráfico de barras dos quatro métodos
6. **Backtesting do VaR**: Exceções acumuladas vs esperadas com resultado de Kupiec
7. **Conclusões Automáticas**: Resumo dinâmico dos principais insights

---

## Competências Demonstradas

- Gestão de risco de mercado
- Estatística aplicada (distribuições, testes de hipótese)
- Value at Risk (VaR) — histórico e paramétrico
- Expected Shortfall / CVaR
- Backtesting de modelos (teste de Kupiec)
- Python para finanças
- Visualização de dados (Plotly)
- Streamlit (dashboard interativo)
- ETL de dados financeiros (yfinance, pandas)
- Análise de séries temporais
- Comunicação de resultados técnicos

---

## Referências

- Basel Committee on Banking Supervision. Fundamental Review of the Trading Book (2019)
- Jorion, P. Value at Risk: The New Benchmark for Managing Financial Risk (2006)
- McNeil, A., Frey, R., Embrechts, P. Quantitative Risk Management (2015)
- Kupiec, P. Techniques for Verifying the Accuracy of Risk Measurement Models (1995)

---

*Últimas atualizações: junho de 2026. Dados históricos de janeiro de 2018 até 30 de dezembro de 2025.*
