import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import (
    Color, CellFormat, BooleanCondition, BooleanRule, ConditionalFormatRule, get_conditional_format_rules
)
from datetime import datetime, timedelta

# Configurações de acesso à API do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
client = gspread.authorize(credentials)

# Acessar a planilha e aba
spreadsheet = client.open("ações")
sheet = spreadsheet.worksheet("Página1")

# Lista de ativos
tickers = [
    "PETR4.SA", "ITUB4.SA", "CSNA3.SA", "VALE3.SA", "BBAS3.SA", "SAPR4.SA",
    "BBSE3.SA", "VBBR3.SA", "VIVT3.SA", "SANB4.SA", "UNIP6.SA", "AURE3.SA",
    "VISC11.SA", "XPLG11.SA", "MXRF11.SA", "KLBN4.SA"
]

def calcular_pmax(tickers):
    resultados = []

    for ticker in tickers:
        ativo = yf.Ticker(ticker)
        
        try:
            dividendos = ativo.dividends
            dividendos.index = dividendos.index.tz_convert(None)  # Ajuste do fuso horário
            
            corte = datetime.now() - timedelta(days=5*365)
            dividendos_5_anos = dividendos[dividendos.index > corte]

            soma_dividendos = dividendos_5_anos.sum()
            media = soma_dividendos / 5
            p_max = media / 0.07

            preco_atual = ativo.history(period="1d")["Close"].iloc[-1]

            resultados.append([ticker, round(p_max, 2), round(preco_atual, 2)])
        except Exception as e:
            print(f"Erro ao processar {ticker}: {e}")
            resultados.append([ticker, None, None])

    return resultados

# Calcula os valores
dados = calcular_pmax(tickers)

# Limpa a planilha antes
sheet.clear()

# Escreve cabeçalho
sheet.update(values=[["Ticker", "P_Max", "Preço Atual"]], range_name='A1')

# Escreve dados
for i, linha in enumerate(dados, start=2):
    sheet.update(values=[linha], range_name=f"A{i}:C{i}")

# Formatação condicional
rules = get_conditional_format_rules(sheet)

# Limpa formatações antigas
rules.clear()

sheet_id = sheet._properties['sheetId']

# Verde: Preço Atual < P_Max
rule_verde = ConditionalFormatRule(
    ranges=[{
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "startColumnIndex": 2,
        "endColumnIndex": 3
    }],
    booleanRule=BooleanRule(
        condition=BooleanCondition('CUSTOM_FORMULA', ["=C2<B2"]),
        format=CellFormat(backgroundColor=Color(0.8, 1, 0.8))
    )
)

# Amarelo: Preço Atual == P_Max
rule_amarelo = ConditionalFormatRule(
    ranges=[{
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "startColumnIndex": 2,
        "endColumnIndex": 3
    }],
    booleanRule=BooleanRule(
        condition=BooleanCondition('CUSTOM_FORMULA', ["=C2=B2"]),
        format=CellFormat(backgroundColor=Color(1, 1, 0.6))
    )
)

# Vermelho: Preço Atual > P_Max
rule_vermelho = ConditionalFormatRule(
    ranges=[{
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "startColumnIndex": 2,
        "endColumnIndex": 3
    }],
    booleanRule=BooleanRule(
        condition=BooleanCondition('CUSTOM_FORMULA', ["=C2>B2"]),
        format=CellFormat(backgroundColor=Color(1, 0.8, 0.8))
    )
)

# Adiciona e salva regras
rules.append(rule_verde)
rules.append(rule_amarelo)
rules.append(rule_vermelho)
rules.save()

print("Planilha atualizada com sucesso!")
