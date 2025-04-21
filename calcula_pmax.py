import yfinance as yf
import pandas as pd
from datetime import datetime

def calcular_pmax(tickers):
    resultados = []

    for ticker in tickers:
        acao = yf.Ticker(ticker)

        # Histórico de dividendos
        dividendos = acao.dividends

        if dividendos.empty:
            soma_dividendos = 0
        else:
            corte = pd.Timestamp(datetime.now()) - pd.DateOffset(years=5)
            # Remover timezone para comparação correta
            dividendos.index = dividendos.index.tz_convert(None)
            dividendos_5_anos = dividendos[dividendos.index > corte]
            soma_dividendos = dividendos_5_anos.sum()

        media_dividendos = soma_dividendos / 5
        pmax = media_dividendos / 0.07

        # Preço atual
        preco_atual = acao.history(period="1d")["Close"].iloc[-1]

        resultados.append([ticker, round(preco_atual, 2), round(pmax, 2)])

    return resultados
