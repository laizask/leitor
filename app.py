from flask import Flask, request, render_template, redirect, url_for, session
import pdfplumber
import pandas as pd
import os
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)
app.secret_key = 'SUA_CHAVE_SECRETA'  # Use uma chave secreta para a sessão

# Configurações do OAuth 2.0
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Para desenvolvimento local
CLIENT_SECRETS_FILE = "credentials.json"  # Caminho para o seu arquivo de credenciais

SCOPES = ['https://www.googleapis.com/auth/drive.file']

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
                            codigo_barras = linhas[i + 1].strip()[:55]
                            dados_inss.append({
                                "Razão Social": razao_social,
                                "Valor Total do Documento": valor_total,
                                "Código de Barras": codigo_barras
                            })
    return dados_inss

def exportar_para_planilhas(dados_fgts, dados_inss):
    df_fgts = pd.DataFrame(dados_fgts)
    df_fgts.to_excel("dados_fgts.xlsx", index=False)

    df_inss = pd.DataFrame(dados_inss)
    df_inss.to_excel("dados_inss.xlsx", index=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=session['state'],
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    # Agora você pode usar as credenciais para acessar a API
    return 'Autenticação bem-sucedida!'

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        arquivos_pdf1 = request.files.getlist("pdf1")
        arquivos_pdf2 = request.files.getlist("pdf2")

        todos_dados_fgts = []
        todos_dados_inss = []

        for arquivo_pdf in arquivos_pdf1:
            dados_extraidos = extrair_dados_fgts(arquivo_pdf)
            todos_dados_fgts.extend(dados_extraidos)

        for arquivo_pdf in arquivos_pdf2:
            dados_extraidos = extrair_dados_inss(arquivo_pdf)
            todos_dados_inss.extend(dados_extraidos)

        exportar_para_planilhas(todos_dados_fgts, todos_dados_inss)

        return "Dados prontos para visualização nas planilhas!"

if __name__ == '__main__':
    app.run(debug=True)
