from flask import Flask, request, render_template
import pdfplumber
import pandas as pd

app = Flask(__name__)

def extrair_dados(arquivo_pdf):
    dados_extraidos = []
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
                            dados_extraidos.append({
                                "Nome/Razão Social do Empregador": nome_empregador,
                                "Valor a recolher": valor_recolher
                            })

    return dados_extraidos

def exportar_para_planilha(todos_dados):
    # Cria um DataFrame a partir da lista de dados extraídos
    df = pd.DataFrame(todos_dados)
    df.to_excel("dados_extraidos.xlsx", index=False)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        arquivos_pdf1 = request.files.getlist("pdf1")  # Obtém uma lista de arquivos do tipo 1
        arquivos_pdf2 = request.files.getlist("pdf2")  # Obtém uma lista de arquivos do tipo 2

        todos_dados = []  # Lista para todos os dados

        # Extrai dados do primeiro tipo de arquivo
        for arquivo_pdf in arquivos_pdf1:
            dados_extraidos = extrair_dados(arquivo_pdf)
            todos_dados.extend(dados_extraidos)  # Adiciona os dados extraídos

        # Extrai dados do segundo tipo de arquivo
        for arquivo_pdf in arquivos_pdf2:
            dados_extraidos = extrair_dados(arquivo_pdf)
            todos_dados.extend(dados_extraidos)  # Adiciona os dados extraídos

        exportar_para_planilha(todos_dados)

        return "Dados prontos para visualização na planilha!"
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
