from flask import Flask, request, render_template
import pdfplumber
import pandas as pd

app = Flask(__name__)

def extrair_dados_fgts(arquivo_pdf):
    dados_fgts = []
    with pdfplumber.open(arquivo_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas = texto.split('\n')
                for i in range(len(linhas)):
                    if "Nome/Razão Social do Empregador" in linhas[i]:
                        if i + 1 < len(linhas):
                            nome_empregador = linhas[i + 1].strip()
                    if "Valor a recolher" in linhas[i]:
                        if i + 1 < len(linhas):
                            valor_recolher = linhas[i + 1].strip()
                            # Adiciona um dicionário com os dados extraídos
                            dados_fgts.append({
                                "Nome/Razão Social do Empregador": nome_empregador,
                                "Valor a recolher": valor_recolher
                            })
    return dados_fgts

def extrair_dados_inss(arquivo_pdf):
    dados_inss = []
    with pdfplumber.open(arquivo_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                linhas = texto.split('\n')
                razao_social = ""
                valor_total = ""
                codigo_barras = ""

                for i in range(len(linhas)):
                    if "Razão Social" in linhas[i]:
                        if i + 1 < len(linhas):
                            razao_social = linhas[i + 1].strip()
                    if "Valor Total do Documento" in linhas[i]:
                        if i + 1 < len(linhas):
                            valor_total = linhas[i + 1].strip()
                    if "Documento de Arrecadação de Receitas Federais" in linhas[i]:
                        if i + 1 < len(linhas):
                            # Extraí o código de barras na linha abaixo
                            codigo_barras = linhas[i + 1].strip()[:55]  # Limita a 55 caracteres
                            # Adiciona um dicionário com os dados extraídos
                            dados_inss.append({
                                "Razão Social": razao_social,
                                "Valor Total do Documento": valor_total,
                                "Código de Barras": codigo_barras
                            })
    
    return dados_inss

def exportar_para_planilhas(dados_fgts, dados_inss):
    # Cria um DataFrame para FGTS e exporta para uma planilha
    df_fgts = pd.DataFrame(dados_fgts)
    df_fgts.to_excel("dados_fgts.xlsx", index=False)

    # Cria um DataFrame para INSS e exporta para outra planilha
    df_inss = pd.DataFrame(dados_inss)
    df_inss.to_excel("dados_inss.xlsx", index=False)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        arquivos_pdf1 = request.files.getlist("pdf1")  # Obtém uma lista de arquivos do tipo 1 (FGTS)
        arquivos_pdf2 = request.files.getlist("pdf2")  # Obtém uma lista de arquivos do tipo 2 (INSS)

        todos_dados_fgts = []  # Lista para dados FGTS
        todos_dados_inss = []  # Lista para dados INSS

        # Extrai dados do primeiro tipo de arquivo (FGTS)
        for arquivo_pdf in arquivos_pdf1:
            dados_extraidos = extrair_dados_fgts(arquivo_pdf)
            todos_dados_fgts.extend(dados_extraidos)  # Adiciona os dados extraídos

        # Extrai dados do segundo tipo de arquivo (INSS)
        for arquivo_pdf in arquivos_pdf2:
            dados_extraidos = extrair_dados_inss(arquivo_pdf)
            todos_dados_inss.extend(dados_extraidos)  # Adiciona os dados extraídos

        exportar_para_planilhas(todos_dados_fgts, todos_dados_inss)

        return "Dados prontos para visualização nas planilhas!"
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
