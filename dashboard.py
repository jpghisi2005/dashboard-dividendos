import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Preço Justo", layout="wide")

# Título e subtítulo
st.markdown("# 📈 Dashboard Interativo de Preço por Dividendos")
st.markdown("### _Veja o preço atual e o preço máximo sugerido com base nos dividendos de pelo menos 7%_")
st.markdown("---")

# Botão para atualizar dados
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# Função para calcular o preço máximo sugerido
def calcular_preco_maximo(ticker):
    ativo = yf.Ticker(ticker)
    try:
        divs = ativo.dividends.tz_convert(None)
        por_ano = divs.groupby(divs.index.year).sum()
        ult5 = sorted(por_ano.index, reverse=True)[:5]
        media = por_ano.loc[ult5].mean()
        return media / 0.07
    except:
        return None

# Lista de ativos
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
    p_max = calcular_preco_maximo(t)
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
    st.dataframe(styled, use_container_width=True, height=600)  # Ajustado aqui

with col2:
    st.markdown("### 📝 Legenda")
    st.markdown("- 🟩 **Verde:** Comprar (Preço Atual ≤ Máximo)")
    st.markdown("- 🟥 **Vermelho:** Esperar (Preço Atual > Máximo)")

st.markdown("---")

# Gráfico de barras
fig = px.bar(
    df,
    x="Ticker",
    y=["Preço Atual (R$)", "Preço Máximo (R$)"],
    barmode="group",
    title="Comparativo de Preço Atual vs Máximo",
    color_discrete_sequence=["#0052cc", "#cc0000"]
)
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### 📚 Fontes de Dados")
st.markdown("- Preços e dividendos via [Yahoo Finance](https://finance.yahoo.com/)")
st.markdown("- Cálculo baseado em retorno de dividendos mínimos de 7% ao ano em uma média dos últimos 5 anos.")
