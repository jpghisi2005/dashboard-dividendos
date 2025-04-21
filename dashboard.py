import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Dashboard Preço Justo", layout="wide")

# Título e subtítulo
st.markdown("# 📈 Dashboard Interativo de Preço por Dividendos")
st.markdown("### _Veja o preço atual e o preço máximo sugerido com base nos dividendos de pelo menos 6% a 9%_")
st.markdown("---")

# Botão para atualizar dados
if st.button("🔄 Atualizar Dados"):
    st.cache_data.clear()  # limpa o cache para buscar novos dados
    st.rerun()

# Seletor de DY mínimo
dy_opcoes = [6, 7, 8, 9]
dy_minimo = st.selectbox("Selecione o DY mínimo desejado (%):", dy_opcoes)
dy_minimo_decimal = dy_minimo / 100

# Função ajustada para usar 5 anos corridos
def calcular_preco_teto(ticker, dy_minimo_decimal):
    ativo = yf.Ticker(ticker)
    try:
        # captura a série de dividendos e remove timezone
        dividends = ativo.dividends.tz_convert(None)
        # define corte para 5 anos corridos
        corte = datetime.now() - pd.DateOffset(years=5)
        # filtra apenas os dividendos após esse corte
        dividends_5anos = dividends[dividends.index > corte]
        # soma total dos dividendos nesse período
        total_5anos = dividends_5anos.sum()
        # média anual: soma / 5
        media_5anos = total_5anos / 5
        # preço-teto = média anual / DY
        return media_5anos / dy_minimo_decimal
    except Exception as e:
        print(f"Erro para {ticker}: {e}")
        return None

# Lista de ativos sólidos em dividendos
tickers = [
    "PETR4.SA", "ITUB4.SA", "CSNA3.SA", "VALE3.SA", "BBAS3.SA", "SAPR4.SA",
    "BBSE3.SA", "VBBR3.SA", "VIVT3.SA", "SANB4.SA", "UNIP6.SA", "AURE3.SA",
    "VISC11.SA", "XPLG11.SA", "MXRF11.SA", "KLBN4.SA"
]

# Coleta de dados
dados = []
for t in tickers:
    ac = yf.Ticker(t)
    try:
        p_at = ac.history(period="1d")['Close'].iloc[-1]
    except:
        p_at = None
    p_max = calcular_preco_teto(t, dy_minimo_decimal)
    if p_at is not None and p_max is not None:
        dados.append({
            "Ticker": t,
            "Preço Atual (R$)": p_at,
            "Preço Máximo (R$)": p_max
        })

df = pd.DataFrame(dados)

# Ordena pela diferença (Preço Máximo - Preço Atual)
df["Diferença"] = df["Preço Máximo (R$)"] - df["Preço Atual (R$)"]
df = df.sort_values("Diferença", ascending=False).drop(columns="Diferença")

# Campo de busca
filtro = st.text_input("🔎 Buscar ação (ex: PETR4)", "").upper().strip()
if filtro:
    df = df[df["Ticker"].str.contains(filtro)]

# Função para colorir as linhas
def colorir_linhas(row):
    if row["Preço Atual (R$)"] <= row["Preço Máximo (R$)"]:
        return ['background-color: green; color: white'] * len(row)
    else:
        return ['background-color: red; color: white'] * len(row)

# Estilização da tabela
styled = (
    df
    .style
    .apply(colorir_linhas, axis=1)
    .format({
        "Preço Atual (R$)": "R$ {:,.2f}",
        "Preço Máximo (R$)": "R$ {:,.2f}"
    })
    .hide(axis="index")
)

# Layout - Centralizando e ajustando a altura da tabela
col1, col2 = st.columns([2, 1])

with col1:
    st.dataframe(styled, use_container_width=True, height=600)

with col2:
    st.markdown("### 📝 Legenda")
    st.markdown("- 🟩 **Verde:** Comprar (Preço Atual ≤ Máximo)")
    st.markdown("- 🟥 **Vermelho:** Esperar (Preço Atual > Máximo)")
    st.markdown("---")
    st.markdown(f"### 📢 DY Mínimo Selecionado: **{dy_minimo}%**")

st.markdown("---")

# Gráfico de barras
fig = px.bar(
    df,
    x="Ticker",
    y=["Preço Atual (R$)", "Preço Máximo (R$)"],
    barmode="group",
    title="Comparativo de Preço Atual vs Preço Máximo (Preço-Teto)",
    color_discrete_sequence=["#0052cc", "#cc0000"]
)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 📚 Fontes de Dados")
st.markdown("- Preços e dividendos via [Yahoo Finance](https://finance.yahoo.com/)")
st.markdown("- 📖 **Cálculo inspirado no método do maior investidor pessoa física do Brasil, Luiz Barsi.**")
st.markdown("- 🏛️ **As ações apresentadas são consideradas entre as principais ações sólidas para recebimento de dividendos na bolsa brasileira.**")
