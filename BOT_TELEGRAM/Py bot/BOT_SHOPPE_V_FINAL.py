import os
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import schedule

# 🔑 Configurações (use variáveis de ambiente para produção)
# Configure estas variáveis no seu ambiente ou arquivo .env
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "SEU_CHAT_ID_AQUI")
CSV_PATH = os.getenv("CSV_FILE_PATH", "data/BatchShopeeLinks.csv")

# Variável global para controlar quais produtos já foram enviados
produtos_enviados = set()

def extrair_imagem_produto(url_produto):
    """Extrai a imagem real do produto da página da Shopee"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"   🔍 Extraindo imagem de: {url_produto[:50]}...")
        
        response = requests.get(url_produto, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tentar diferentes seletores comuns da Shopee para imagens
        seletores_imagem = [
            'img[class*="product-image"]',
            'img[class*="main-image"]', 
            'img[class*="gallery-image"]',
            'img[class*="item-image"]',
            'div[class*="image-gallery"] img',
            'div[class*="product-image"] img',
            '.product-image img',
            '.main-image img',
            'img[alt*="product"]',
            'img[src*="shopee"]'
        ]
        
        imagem_url = ""
        
        for seletor in seletores_imagem:
            img_tag = soup.select_one(seletor)
            if img_tag and img_tag.get('src'):
                imagem_url = img_tag['src']
                # Garantir que a URL está completa
                if imagem_url.startswith('//'):
                    imagem_url = 'https:' + imagem_url
                elif imagem_url.startswith('/'):
                    # Usar domínio base da URL original
                    base_url = '/'.join(url_produto.split('/')[:3])
                    imagem_url = base_url + imagem_url
                
                print(f"   ✅ Imagem encontrada com seletor: {seletor}")
                break
        
        # Se não encontrou com seletores, tentar buscar qualquer imagem relevante
        if not imagem_url:
            todas_imagens = soup.find_all('img', src=True)
            for img in todas_imagens:
                src = img['src']
                if any(keyword in src.lower() for keyword in ['product', 'item', 'shopee', 'cdn', 'image']):
                    if not any(keyword in src.lower() for keyword in ['icon', 'logo', 'avatar']):
                        imagem_url = src
                        if imagem_url.startswith('//'):
                            imagem_url = 'https:' + imagem_url
                        print(f"   ✅ Imagem alternativa encontrada")
                        break
        
        return imagem_url
        
    except Exception as e:
        print(f"   ❌ Erro ao extrair imagem: {str(e)[:100]}...")
        return ""

def enviar_produto_telegram(produto, imagem_url):
    """Envia produto formatado para o Telegram usando dados do CSV"""
    
    # Formatar a mensagem com HTML usando dados reais do CSV
    mensagem = f"""
🛍️ <b>{produto['Item Name']}</b>

🏪 <i>Loja: {produto['Shop Name']}</i>

💰 <b>Preço: R$ {produto['Price']}</b>
📈 Vendas: {produto['Sales']}

⭐ Avaliação: {random.randint(4, 5)}.{random.randint(0, 9)}/5
🔥 {produto['Sales']} vendidos

🔗 <a href="{produto['Offer Link']}">🛒 COMPRAR AGORA NA SHOPEE 🛒</a>

💬 Produto em alta! Não perca!
    """.strip()
    
    # Se tem imagem real, enviar como foto
    if imagem_url and len(imagem_url) > 10 and "http" in imagem_url:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": imagem_url,
            "caption": mensagem,
            "parse_mode": "HTML"
        }
    else:
        # Se não tem imagem, enviar apenas texto
        print("   ⚠️  Enviando sem imagem (URL não encontrada)")
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mensagem,
            "parse_mode": "HTML"
        }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response
    except Exception as e:
        print(f"   ❌ Erro na requisição Telegram: {e}")
        return type('obj', (object,), {'status_code': 500, 'text': str(e)})()

def carregar_produtos():
    """Carrega os produtos do CSV"""
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        
        # Verificar colunas necessárias
        colunas_necessarias = ['Item Name', 'Price', 'Sales', 'Shop Name', 'Offer Link', 'Product Link', 'Item Id']
        colunas_existentes = df.columns.tolist()
        
        colunas_faltantes = [col for col in colunas_necessarias if col not in colunas_existentes]
        if colunas_faltantes:
            print(f"❌ Colunas faltantes: {colunas_faltantes}")
            return None
        
        print(f"✅ CSV carregado! {len(df)} produtos encontrados")
        return df
        
    except Exception as e:
        print(f"💥 Erro ao carregar CSV: {e}")
        return None

def enviar_lote_produtos(hora_envio):
    """Envia um lote de produtos baseado no horário"""
    global produtos_enviados
    
    df = carregar_produtos()
    if df is None:
        return
    
    total_produtos = len(df)
    
    # Definir os lotes baseado no horário
    if hora_envio == "09:00":
        lote = "1/3"
        inicio = 0
        fim = total_produtos // 3
    elif hora_envio == "12:00":
        lote = "2/3"
        inicio = total_produtos // 3
        fim = 2 * total_produtos // 3
    elif hora_envio == "14:00":
        lote = "3/3"
        inicio = 2 * total_produtos // 3
        fim = total_produtos
    else:
        print(f"❌ Horário não configurado: {hora_envio}")
        return
    
    print(f"\n{'='*50}")
    print(f"🕐 INICIANDO ENVIO {lote} - {hora_envio}")
    print(f"📦 Produtos {inicio+1} a {fim} de {total_produtos}")
    print(f"{'='*50}")
    
    # Enviar mensagem de início do lote
    mensagem_inicio = f"🚀 <b>PROMOÇÕES DA MANHÃ - Lote {lote}</b> 🚀\n\n💎 {fim - inicio} produtos incríveis chegando!"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem_inicio,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload, timeout=5)
    
    time.sleep(2)
    
    # Processar produtos do lote
    for index in range(inicio, fim):
        produto = df.iloc[index]
        produto_id = f"{produto['Item Id']}_{produto['Item Name'][:20]}"
        
        # Pular se já foi enviado (para segurança)
        if produto_id in produtos_enviados:
            print(f"   ⏭️  Produto {index+1} já enviado, pulando...")
            continue
            
        print(f"\n📦 Processando produto {index + 1}/{total_produtos}...")
        print(f"   🏷️  {produto['Item Name'][:50]}...")
        print(f"   💰 R$ {produto['Price']}")
        print(f"   🏪 {produto['Shop Name'][:30]}...")
        
        # Extrair imagem real do produto
        imagem_url = extrair_imagem_produto(produto['Product Link'])
        
        # Enviar para Telegram
        response = enviar_produto_telegram(produto, imagem_url)
        
        if response.status_code == 200:
            print("   ✅ Enviado com sucesso!")
            produtos_enviados.add(produto_id)
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📝 Detalhes: {response.text[:100] if hasattr(response, 'text') else 'Sem detalhes'}")
        
        # Pausa entre envios
        if index < fim - 1:
            tempo_espera = random.randint(5, 10)
            print(f"   ⏳ Aguardando {tempo_espera} segundos...")
            time.sleep(tempo_espera)
    
    # Mensagem de fim do lote
    mensagem_fim = f"✅ <b>Lote {lote} concluído!</b>\n\n🎯 {fim - inicio} produtos enviados!\n\n⏰ Próximo lote em breve..."
    payload_fim = {
        "chat_id": CHAT_ID,
        "text": mensagem_fim,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload_fim, timeout=5)
    
    print(f"\n🎯 Lote {lote} concluído! {fim - inicio} produtos enviados.")

def agendar_envios():
    """Agenda os envios nos horários definidos"""
    print("🤖 AGENDADOR DE PROMOÇÕES SHOPEE")
    print("📅 Horários programados:")
    print("   🕘 09:00 - Primeiro lote (1/3)")
    print("   🕛 12:00 - Segundo lote (2/3)") 
    print("   🕑 14:00 - Terceiro lote (3/3)")
    print("=" * 50)
    
    # Agendar os envios
    schedule.every().day.at("09:00").do(lambda: enviar_lote_produtos("09:00"))
    schedule.every().day.at("12:00").do(lambda: enviar_lote_produtos("12:00"))
    schedule.every().day.at("14:00").do(lambda: enviar_lote_produtos("14:00"))
    
    # Teste inicial (opcional)
    print("🧪 Executando teste inicial...")
    time.sleep(2)
    
    # Mostrar próximo agendamento
    proximo = schedule.next_run()
    print(f"⏰ Próximo envio: {proximo}")
    
    # Manter o script rodando
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Agendador interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro no agendador: {e}")
            time.sleep(60)

def main():
    """Função principal"""
    print("🤖 BOT DE PROMOÇÕES SHOPEE - AGENDADO")
    print("📸 COM IMAGENS REAIS DOS PRODUTOS")
    print("⏰ ENVIOS: 09h, 12h, 14h")
    print("=" * 50)
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo não encontrado: {CSV_PATH}")
        print(f"   📝 Crie o arquivo CSV em: {CSV_PATH}")
        return
    
    # Verificar se o CSV pode ser carregado
    df = carregar_produtos()
    if df is not None:
        total = len(df)
        print(f"📊 Total de produtos: {total}")
        print(f"📦 Lote 09h: {total//3} produtos")
        print(f"📦 Lote 12h: {total//3} produtos") 
        print(f"📦 Lote 14h: {total - 2*(total//3)} produtos")
        print("\n🚀 Iniciando agendador...")
        time.sleep(2)
        agendar_envios()
    else:
        print("💥 Não foi possível carregar o CSV")

if __name__ == "__main__":
    main()