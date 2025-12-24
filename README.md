# 🤖 Bot Shopee Afiliados → Telegram

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Shopee-EE4D2D?style=for-the-badge&logo=shopee&logoColor=white" alt="Shopee">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License">
</p>

---

## 📌 Sobre o Projeto

Este projeto consiste em um **bot desenvolvido em Python** que automatiza o envio de **produtos afiliados da Shopee** para um **canal ou grupo no Telegram**.

Os produtos são **extraídos a partir de um arquivo CSV**, gerado diretamente na **aba de Afiliados da Shopee**, permitindo a automação de divulgação de links de forma simples, rápida e escalável.

---

## ✨ Funcionalidades

* 📥 **Leitura automática de arquivo CSV** exportado da Shopee Afiliados
* 📤 **Envio automático de produtos para o Telegram**
* 🛒 Envio de **nome do produto, preço e link afiliado**
* 🔄 Processamento contínuo ou por execução
* ⚙️ Código simples e fácil de adaptar para novos layouts de CSV

---

## 📂 Estrutura do CSV (exemplo)

O bot espera um arquivo `.csv` com colunas semelhantes a:

* `nome_produto`
* `preco`
* `link_afiliado`

> ⚠️ Os nomes das colunas podem ser ajustados diretamente no código, conforme o layout exportado pela Shopee.

---

## 🚀 Começando

### 📋 Pré-requisitos

* Python **3.8 ou superior**
* Conta no **Telegram**
* Token de Bot (criado via [@BotFather](https://t.me/botfather))
* Canal ou grupo no Telegram com o bot como administrador
* Arquivo CSV exportado da **Shopee Afiliados**

---

## 🔧 Instalação

1. **Clone o repositório**

```bash
git clone https://github.com/Mateus-Caique-Py/BOT_SHOPPE.git
cd BOT_SHOPPE
```

2. **Crie um ambiente virtual (opcional, recomendado)**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

1. Configure no código:

   * Token do Bot do Telegram
   * ID do canal ou grupo
   * Caminho do arquivo CSV

2. Exemplo de variáveis:

```python
TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID"
CSV_PATH = "produtos_shopee.csv"
```

---

## ▶️ Execução

Execute o bot com:

```bash
python main.py
```

O bot irá:

* Ler o arquivo CSV
* Processar os produtos
* Enviar automaticamente as informações para o Telegram

---

## 🧠 Possíveis Evoluções

* 🔁 Evitar envio de produtos duplicados
* ⏰ Agendamento automático (cron / schedule)
* 🖼️ Envio de imagens dos produtos
* 📊 Log de produtos enviados
* 🧩 Integração direta com API ou scraping

---

## 📄 Licença

Este projeto está sob a licença **MIT**.
Sinta-se livre para usar, modificar e distribuir.

---

## 👨‍💻 Autor

Desenvolvido por **Mateus Kaique**
🔗 GitHub: [https://github.com/Mateus-Caique-Py](https://github.com/Mateus-Caique-Py)
