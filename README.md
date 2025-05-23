Cadastro e Gerenciamento de Produtos - Web App com Python

Este projeto é uma aplicação web desenvolvida em Python com Streamlit, que permite cadastrar, listar, atualizar e deletar produtos com integração a serviços da Azure:

## Azure SQL Database: Armazena os dados dos produtos (nome, descrição, preço e URL da imagem).

## Azure Blob Storage: Armazena as imagens dos produtos de forma segura e acessível por URL.

Funcionalidades:

- Formulário para cadastrar produtos com imagem.
- Validação para impedir cadastros incompletos.
- Listagem em tempo real dos produtos cadastrados.
- Edição e atualização de produtos diretamente pela interface.
- Exclusão de produtos com um clique.

Uso de boas práticas com variáveis de ambiente (.env) para proteger credenciais.

Tecnologias utilizadas:
Python
Streamlit
pyodbc
pandas
azure-storage-blob
python-dotenv

