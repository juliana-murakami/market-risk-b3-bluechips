"""
app.py - Dashboard de Risco de Mercado
Análise de Risco de Mercado nas Maiores Blue Chips da B3 (2018-2025)

"""

import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm, kurtosis, skew

st.set_page_config(
    page_title="Risco de Mercado - Top 5 B3",
    page_icon="📈",
    layout="wide",
)

ATIVOS    = ["PETR4.SA", "ITUB4.SA", "VALE3.SA", "ABEV3.SA", "BPAC11.SA"]
NOMES     = ["Petrobras", "Itaú", "Vale", "Ambev", "BTG"]
BENCHMARK = "^BVSP"
START     = "2018-01-01"
END       = "2025-12-31"
CONF      = 0.95
WINDOW    = 252

CORES = {
    "PETR4.SA": "#1f77b4",
    "ITUB4.SA": "#2ca02c",
    "VALE3.SA": "#d62728",
    "ABEV3.SA": "#ff7f0e",
    "BPAC11.SA": "#9467bd",
    "IBOV":     "#aaaaaa",
}

CRISES = {
    "Covid (mar/20)":           "2020-03-23",
    "Crise Eleitoral (out/22)": "2022-10-30",
}

@st.cache_data
def carregar_dados():
    tickers = ATIVOS + [BENCHMARK]
    raw = yf.download(tickers, start=START, end=END,
                      auto_adjust=True, progress=False)
    prices = raw["Close"].copy()
    prices.index = pd.to_datetime(prices.index)
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)
    prices = prices.loc[START:END].ffill(limit=1).dropna()
    prices = prices.rename(columns={"^BVSP": "IBOV"})
    returns = np.log(prices / prices.shift(1)).dropna()
    returns = returns.loc[START:END]
    # sem filtro de outliers — eventos extremos são relevantes para análise de risco
    port_returns = (returns[ATIVOS] * 0.20).sum(axis=1)
    return returns, port_returns

with st.spinner("Carregando dados..."):
    returns, port_returns = carregar_dados()

mu    = port_returns.mean()
sigma = port_returns.std()
z     = norm.ppf(CONF)
var_hist   = -port_returns.quantile(1 - CONF)
var_param  = -(mu - z * sigma)
tail       = port_returns[port_returns <= -var_hist]
cvar_hist  = -tail.mean()
cvar_param = -(mu - sigma * norm.pdf(z) / (1 - CONF))
sk         = skew(port_returns)
ku         = kurtosis(port_returns)
cum_port   = np.exp(port_returns.cumsum())
cum_ibov   = np.exp(returns["IBOV"].cumsum())
max_dd     = ((cum_port - cum_port.cummax()) / cum_port.cummax()).min()
retorno_total = cum_port.iloc[-1] - 1
vol_anual  = sigma * np.sqrt(252)
sharpe     = (mu * 252) / vol_anual
var_rolling = -port_returns.rolling(WINDOW).quantile(1 - CONF).shift(1)
bt = pd.DataFrame({"retorno": port_returns, "var": var_rolling}).dropna()
bt["excecao"] = bt["retorno"] < -bt["var"]
n_total    = len(bt)
n_excecoes = int(bt["excecao"].sum())
taxa_obs   = n_excecoes / n_total
taxa_esp   = 1 - CONF

# título
st.title("Análise de Risco de Mercado nas Maiores Blue Chips da B3")
st.caption("PETR4 · ITUB4 · VALE3 · ABEV3 · BPAC11  |  Pesos iguais (20%)  |  2018–2025")
st.divider()

# KPI cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Retorno Total",      "{:.1%}".format(retorno_total))
c2.metric("Volatilidade Anual", "{:.1%}".format(vol_anual))
c3.metric("Sharpe Ratio",       "{:.2f}".format(sharpe))
c4.metric("VaR 95%",            "{:.2%}".format(var_hist))
c5.metric("CVaR 95%",           "{:.2%}".format(cvar_hist))
c6.metric("Máx. Drawdown",      "{:.1%}".format(max_dd))
st.divider()

# gráfico 1: distribuição
st.subheader("1. Distribuição de Retornos e Métricas de Risco")
ret_plot = port_returns[(port_returns >= mu-4*sigma) & (port_returns <= mu+4*sigma)]
x   = np.linspace(mu - 4*sigma, mu + 4*sigma, 300)
pdf = norm.pdf(x * 100, mu * 100, sigma * 100) / 100

fig1 = go.Figure()
fig1.add_trace(go.Histogram(
    x=ret_plot*100, nbinsx=70, histnorm="probability density",
    name="Retornos diários", marker_color="#5b9bd5", opacity=0.8,
    showlegend=False))

for val, label, cor, y_pos in [
    (cvar_hist, "CVaR ({:.2%})".format(cvar_hist),       "#ff6bff", 0.92),
    (var_hist,  "VaR Hist. ({:.2%})".format(var_hist),   "#ffd700", 0.75),
    (var_param, "VaR Param. ({:.2%})".format(var_param), "#ff8c00", 0.58),
]:
    fig1.add_vline(x=-val*100, line_dash="dash", line_color=cor, line_width=1.8)
    fig1.add_annotation(
        x=-val*100, y=y_pos, yref="paper",
        text=label, showarrow=False,
        font=dict(size=10, color=cor),
        xanchor="left", xshift=6)

fig1.add_annotation(
    x=0.98, y=0.95, xref="paper", yref="paper",
    text="Skewness: {:.2f}<br>Kurtosis: {:.2f}".format(sk, ku),
    showarrow=False, align="right",
    bgcolor="rgba(50,50,50,0.8)", bordercolor="#888888", borderwidth=1,
    font=dict(size=11, color="white"), xanchor="right")

fig1.update_layout(
    xaxis_title="Retorno Diário (%)",
    yaxis_title="Densidade de Probabilidade",
    height=420, showlegend=False)

st.plotly_chart(fig1, use_container_width=True)
st.divider()

# gráfico 2: retorno acumulado
st.subheader("2. Retorno Acumulado por Ativo vs IBOV")
fig2 = go.Figure()
for ativo, nome in zip(ATIVOS, NOMES):
    cum = np.exp(returns[ativo].cumsum())
    fig2.add_trace(go.Scatter(
        x=cum.index, y=cum.values,
        name=ativo.replace(".SA", ""),
        line=dict(color=CORES[ativo], width=1.8)))
fig2.add_trace(go.Scatter(
    x=cum_ibov.index, y=cum_ibov.values, name="IBOV",
    line=dict(color=CORES["IBOV"], width=2.5, dash="dash")))
for label, data in CRISES.items():
    fig2.add_vline(x=data, line_dash="dot", line_color="#999999",
                   opacity=0.8, annotation_text=label,
                   annotation_position="top", annotation_font_size=10)
fig2.add_hline(y=1, line_dash="dot", line_color="#555555")
fig2.update_layout(height=420,
                   yaxis_title="Retorno (base 1,0)",
                   legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig2, use_container_width=True)
st.divider()

# gráfico 3: drawdown
st.subheader("3. Drawdown Histórico — Carteira vs IBOV")
dd_port = (cum_port - cum_port.cummax()) / cum_port.cummax() * 100
dd_ibov = (cum_ibov - cum_ibov.cummax()) / cum_ibov.cummax() * 100

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=dd_port.index, y=dd_port.values, name="Carteira",
    fill="tozeroy", fillcolor="rgba(91,155,213,0.15)",
    line=dict(color="#5b9bd5", width=2)))
fig3.add_trace(go.Scatter(
    x=dd_ibov.index, y=dd_ibov.values, name="IBOV",
    line=dict(color="#aaaaaa", width=2, dash="dash")))
for label, data in CRISES.items():
    fig3.add_vline(x=data, line_dash="dot", line_color="#999999",
                   opacity=0.8, annotation_text=label,
                   annotation_position="top", annotation_font_size=10)
fig3.add_hline(y=0, line_color="#555555", line_width=1)
fig3.update_layout(height=380,
                   yaxis_title="Drawdown (%)",
                   legend=dict(orientation="h", y=-0.15))
st.plotly_chart(fig3, use_container_width=True)
st.divider()

# gráficos 4 e 5 lado a lado
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("4. Comparação de Métodos VaR")
    metodos   = ["VaR Param.", "VaR Hist.", "CVaR Hist.", "CVaR Param."]
    valores   = [var_param*100, var_hist*100, cvar_hist*100, cvar_param*100]
    cores_bar = ["#ff8c00", "#ffd700", "#ff6bff", "#cc44cc"]
    fig4 = go.Figure(go.Bar(
        x=metodos, y=valores, marker_color=cores_bar,
        text=["{:.2f}%".format(v) for v in valores],
        textposition="outside", width=0.5))
    fig4.update_layout(height=380,
                       yaxis_title="Perda Esperada (%)",
                       yaxis=dict(range=[0, max(valores)*1.3]),
                       showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

with col_r:
    st.subheader("5. Backtesting do VaR")
    excecoes_acum = bt["excecao"].cumsum()
    esperado_acum = pd.Series(
        np.arange(1, len(bt)+1) * taxa_esp, index=bt.index)
    avaliacao = "Modelo bem calibrado" if taxa_obs/taxa_esp <= 1.2 else "Revisar modelo"
    cor_av = "#2ca02c" if taxa_obs/taxa_esp <= 1.2 else "#d62728"

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(
        x=bt.index, y=excecoes_acum,
        name="Observado ({:.1%})".format(taxa_obs),
        line=dict(color="#d62728", width=1.8)))
    fig5.add_trace(go.Scatter(
        x=bt.index, y=esperado_acum, name="Esperado (5%)",
        line=dict(color="#5b9bd5", width=1.5, dash="dash")))
    fig5.add_annotation(
        x=0.98, y=0.05, xref="paper", yref="paper",
        text=avaliacao, showarrow=False,
        font=dict(size=11, color=cor_av), xanchor="right")
    fig5.update_layout(height=380,
                       yaxis_title="Exceções Acumuladas",
                       legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# conclusões
st.subheader("Principais Conclusões")

retornos_totais = {
    a.replace(".SA",""): np.exp(returns[a].cumsum()).iloc[-1]-1 for a in ATIVOS}
ranking = sorted(retornos_totais.items(), key=lambda x: x[1], reverse=True)
melhor, pior = ranking[0], ranking[-1]
mais_arriscado = max(
    {a.replace(".SA",""): -returns[a].quantile(1-CONF) for a in ATIVOS},
    key=lambda k: -returns[k+".SA"].quantile(1-CONF))
drawdowns_crise = {}
for nome_c, data_c in CRISES.items():
    r = port_returns.loc[:data_c].iloc[-21:]
    drawdowns_crise[nome_c] = r.sum()
maior_choque = min(drawdowns_crise, key=drawdowns_crise.get)
avaliacao_bt = "bem calibrado" if taxa_obs/taxa_esp <= 1.2 else "requer revisão"

st.markdown("""
**Desempenho**
- **{}** teve o maior retorno acumulado ({:.0%}).
- **{}** teve o pior desempenho ({:.0%}).

**Risco**
- VaR da carteira: **{:.2%}** | CVaR: **{:.2%}** | Máx. Drawdown: **{:.1%}**

**Choques**
- **{}** representou o maior choque do período analisado.

**Validação do modelo**
- Backtesting: **{:.1%}** de exceções vs **5%** esperado — modelo **{}**.
""".format(
    melhor[0], melhor[1], pior[0], pior[1],
    var_hist, cvar_hist, max_dd,
    maior_choque, taxa_obs, avaliacao_bt))

st.caption("Dados: Yahoo Finance | 2018–2025 | Pesos iguais (20% por ativo)")
