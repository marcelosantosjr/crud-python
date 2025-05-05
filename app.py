# Requisitos: pip install streamlit pyodbc azure-storage-blob pandas python-dotenv

import streamlit as st
import pyodbc
import pandas as pd
from azure.storage.blob import BlobServiceClient
import uuid
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

# Configurações da Azure SQL
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# Configurações do Blob Storage
BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")

# Inicializar sessão
if "pagina" not in st.session_state:
    st.session_state.pagina = "produtos"
if "produto_checkout" not in st.session_state:
    st.session_state.produto_checkout = None

# Função para conectar ao banco
@st.cache_resource
def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
    )
    return conn

# Função para upload da imagem
@st.cache_resource
def get_blob_client():
    return BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

def upload_image(file):
    if file is None:
        return None
    blob_service_client = get_blob_client()
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=str(uuid.uuid4()) + os.path.splitext(file.name)[1])
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url

# Função para inserir produto
def inserir_produto(nome, descricao, preco, imagem_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Produtos (nome, descicao, preco, imagem_url) VALUES (?, ?, ?, ?)",
                   (nome, descricao, preco, imagem_url))
    conn.commit()

# Função para listar produtos
def listar_produtos():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Produtos", conn)
    return df

# Função para deletar produto
def deletar_produto(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Produtos WHERE id = ?", (produto_id,))
    conn.commit()

# Função para atualizar produto
def atualizar_produto(produto_id, nome, descricao, preco, imagem_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    if imagem_url:
        cursor.execute("UPDATE Produtos SET nome = ?, descicao = ?, preco = ?, imagem_url = ? WHERE id = ?",
                       (nome, descricao, preco, imagem_url, produto_id))
    else:
        cursor.execute("UPDATE Produtos SET nome = ?, descicao = ?, preco = ? WHERE id = ?",
                       (nome, descricao, preco, produto_id))
    conn.commit()

# Página de checkout
def pagina_checkout():
    produto = st.session_state.produto_checkout
    if produto is None or produto.get("id") is None:
        st.warning("Nenhum produto selecionado.")
        return

    st.title("Checkout")
    st.image(produto['imagem_url'], width=300)
    st.markdown(f"### {produto['nome']}")
    st.write(f"**Descrição:** {produto['descicao']}")
    st.write(f"**Preço:** R$ {produto['preco']:.2f}")

    if st.button("Finalizar Compra"):
        st.success("Compra finalizada com sucesso! Obrigado pela preferência.")

    if st.button("Voltar"):
        st.session_state.pagina = "produtos"
        st.rerun()

# Página de produtos
def pagina_produtos():
    st.title("Cadastro de Produtos")

    with st.form("form_produto"):
        nome = st.text_input("Nome do produto")
        descricao = st.text_area("Descrição")
        preco = st.number_input("Preço", step=0.01)
        imagem = st.file_uploader("Imagem", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("Cadastrar")

        if submitted:
            if not nome or not descricao or preco <= 0 or not imagem:
                st.warning("Todos os campos devem ser preenchidos corretamente para cadastrar um produto.")
            else:
                url_imagem = upload_image(imagem)
                inserir_produto(nome, descricao, preco, url_imagem)
                st.success("Produto cadastrado com sucesso!")
                st.rerun()

    st.subheader("Lista de Produtos")
    df = listar_produtos()

    for i, row in df.iterrows():
        st.markdown(f"### {row['nome']}")
        st.image(row['imagem_url'], width=200)
        st.write(f"**Descrição:** {row['descicao']}")
        st.write(f"**Preço:** R$ {row['preco']:.2f}")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"Deletar {row['id']}"):
                deletar_produto(row['id'])
                st.rerun()

        with col2:
            with st.expander(f"Atualizar {row['id']}"):
                with st.form(f"update_form_{row['id']}"):
                    novo_nome = st.text_input("Nome", value=row['nome'], key=f"nome_{row['id']}")
                    nova_desc = st.text_area("Descrição", value=row['descicao'], key=f"desc_{row['id']}")
                    novo_preco = st.number_input("Preço", value=float(row['preco']), step=0.01, key=f"preco_{row['id']}")
                    nova_img = st.file_uploader("Nova imagem", type=["jpg", "jpeg", "png"], key=f"img_{row['id']}")
                    atualizar_btn = st.form_submit_button("Salvar")
                    if atualizar_btn:
                        nova_url = upload_image(nova_img) if nova_img else None
                        atualizar_produto(row['id'], novo_nome, nova_desc, novo_preco, nova_url)
                        st.success("Produto atualizado!")
                        st.rerun()

        with col3:
            if st.button(f"Comprar {row['id']}"):
                st.session_state.produto_checkout = row
                st.session_state.pagina = "checkout"
                st.rerun()

# Navegação entre páginas
if st.session_state.pagina == "produtos":
    pagina_produtos()
elif st.session_state.pagina == "checkout":
    pagina_checkout()