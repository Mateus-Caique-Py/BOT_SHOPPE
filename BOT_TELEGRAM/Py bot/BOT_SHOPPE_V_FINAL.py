import os
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
from typing import Optional, Set, Any

# =============================================================================
# 🔑 CONFIGURAÇÕES GERAIS
# =============================================================================

TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")
CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID_AQUI")
CSV_PATH: str = os.getenv("CSV_FILE_PATH", "data/BatchShopeeLinks.csv")

# Armazena os IDs dos produtos já enviados para evitar duplicidade
produtos_enviados: Set[str] = set()


def extrair_imagem_produto(url_produto: str) -> str:
    """
    Extrai a URL da imagem principal do produto diretamente da página da Shopee.

    Args:
        url_produto (str): URL da página do produto na Shopee.

    Returns:
        str: URL completa da imagem do produto ou string vazia se não encontrada.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }

        print(f"🔍 Extraindo imagem de: {url_produto[:60]}")

        response = requests.get(url_produto, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, "html.parser")

        seletores_imagem = [
            'img[class*="product-image"]',
            'img[class*="main-image"]',
            'img[class*="gallery-image"]',
            'img[src*="shopee"]'
        ]

        for seletor in seletores_imagem:
            img = soup.select_one(seletor)
            if img and img.get("src"):
                imagem_url = img["src"]

                if imagem_url.startswith("//"):
                    imagem_url = "https:" + imagem_url
                elif imagem_url.startswith("/"):
                    base_url = "/".join(url_produto.split("/")[:3])
                    imagem_url = base_url + imagem_url

                return imagem_url

        return ""

    except Exception as exc:
        print(f"❌ Erro ao extrair imagem: {exc}")
        return ""


def enviar_produto_telegram(produto: pd.Series, imagem_url: str) -> requests.Response:
    """
    Envia um produto formatado para o Telegram.

    Args:
        produto (pd.Series): Linha do DataFrame contendo os dados do produto.
        imagem_url (str): URL da imagem do produto.

    Returns:
        requests.Response: Resposta da API do Telegram.
    """
    mensagem = f"""
🛍️ <b>{produto['Item Name']}</b>

🏪 <i>Loja: {produto['Shop Name']}</i>

💰 <b>Preço: R$ {produto['Price']}</b>
📈 Vendas: {produto['Sales']}

⭐ Avaliação: {random.randint(4, 5)}.{random.randint(0, 9)}/5
🔥 {produto['Sales']} vendidos

🔗 <a href="{produto['Offer Link']}">🛒 COMPRAR AGORA NA SHOPEE 🛒</a>
""".strip()

    if imagem_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": imagem_url,
            "caption": mensagem,
            "parse_mode": "HTML",
        }
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mensagem,
            "parse_mode": "HTML",
        }

    return requests.post(url, json=payload, timeout=10)


def carregar_produtos() -> Optional[pd.DataFrame]:
    """
    Carrega o arquivo CSV contendo os produtos da Shopee Afiliados.

    Returns:
        Optional[pd.DataFrame]: DataFrame com os produtos ou None em caso de erro.
    """
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")

        colunas_necessarias = [
            "Item Name",
            "Price",
            "Sales",
            "Shop Name",
            "Offer Link",
            "Product Link",
            "Item Id",
        ]

        if not all(col in df.columns for col in colunas_necessarias):
            print("❌ O CSV não possui todas as colunas necessárias.")
            return None

        return df

    except Exception as exc:
        print(f"💥 Erro ao carregar CSV: {exc}")
        return None


def enviar_lote_produtos(hora_envio: str) -> None:
    """
    Envia um lote de produtos de acordo com o horário configurado.

    Args:
        hora_envio (str): Horário do envio no formato HH:MM.
    """
    global produtos_enviados

    df = carregar_produtos()
    if df is None:
        return

    total = len(df)

    if hora_envio == "09:00":
        inicio, fim = 0, total // 3
        lote = "1/3"
    elif hora_envio == "12:00":
        inicio, fim = total // 3, 2 * total // 3
        lote = "2/3"
    elif hora_envio == "14:00":
        inicio, fim = 2 * total // 3, total
        lote = "3/3"
    else:
        print("❌ Horário inválido.")
        return

    print(f"🚀 Enviando lote {lote} ({hora_envio})")

    for index in range(inicio, fim):
        produto = df.iloc[index]
        produto_id = f"{produto['Item Id']}"

        if produto_id in produtos_enviados:
            continue

        imagem_url = extrair_imagem_produto(produto["Product Link"])
        response = enviar_produto_telegram(produto, imagem_url)

        if response.status_code == 200:
            produtos_enviados.add(produto_id)

        time.sleep(random.randint(5, 10))


def agendar_envios() -> None:
    """
    Agenda os envios automáticos dos produtos nos horários definidos.
    """
    schedule.every().day.at("09:00").do(lambda: enviar_lote_produtos("09:00"))
    schedule.every().day.at("12:00").do(lambda: enviar_lote_produtos("12:00"))
    schedule.every().day.at("14:00").do(lambda: enviar_lote_produtos("14:00"))

    while True:
        schedule.run_pending()
        time.sleep(1)


def main() -> None:
    """
    Função principal de inicialização do bot.
    """
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV não encontrado em: {CSV_PATH}")
        return

    agendar_envios()


if __name__ == "__main__":
    main()
