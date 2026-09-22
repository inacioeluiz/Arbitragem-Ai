# ==============================================
# 📊 SCANNER DE ARBITRAGEM ENTRE BOLSAS
# ==============================================

def buscar_preco_bolsa(simbolo, corretora):
    """Busca preço atual de uma moeda em uma corretora"""
    import requests
    par = simbolo.upper() + "USDT"
    urls = {
        "Binance": f"https://api.binance.com/api/v3/ticker/price?symbol={par}",
        "Bybit": f"https://api.bybit.com/v2/public/tickers?symbol={par}",
        "KuCoin": f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={par}",
        "Gate.io": f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={simbolo.upper()}_USDT",
        "OKX": f"https://www.okx.com/api/v5/market/ticker?instId={simbolo.upper()}-USDT"
    }
    
    if corretora not in urls:
        return None
    
    try:
        resp = requests.get(urls[corretora], timeout=8)
        dados = resp.json()
        
        if corretora == "Binance" and "price" in dados:
            return float(dados["price"])
        elif corretora == "Bybit" and "result" in dados and dados["result"]:
            return float(dados["result"][0]["last_price"])
        elif corretora == "KuCoin" and dados.get("code") == "200000" and "data" in dados:
            return float(dados["data"]["price"])
        elif corretora == "Gate.io" and len(dados) > 0:
            return float(dados[0]["last"])
        elif corretora == "OKX" and dados.get("code") == "0" and "data" in dados:
            return float(dados["data"][0]["last"])
    except Exception as e:
        pass
    return None


def escanear_oportunidades(lista_moedas=["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC"]):
    """Compara preços entre todas as bolsas e retorna oportunidades de arbitragem"""
    corretoras_ativas = list(CORRETORAS.keys())
    oportunidades = []
    
    for moeda in lista_moedas:
        precos = {}
        for bolsa in corretoras_ativas:
            preco = buscar_preco_bolsa(moeda, bolsa)
            if preco and preco > 0:
                precos[bolsa] = preco
        
        if len(precos) >= 2:
            mais_barata = min(precos.items(), key=lambda x: x[1])
            mais_cara = max(precos.items(), key=lambda x: x[1])
            preco_compra = mais_barata[1]
            preco_venda = mais_cara[1]
            spread_pct = ((preco_venda - preco_compra) / preco_compra) * 100
            
            if spread_pct >= 0.3:  # Mostra só oportunidades com ≥ 0,3% de lucro
                oportunidades.append({
                    "moeda": moeda,
                    "comprar_bolsa": mais_barata[0],
                    "comprar_preco": preco_compra,
                    "vender_bolsa": mais_cara[0],
                    "vender_preco": preco_venda,
                    "lucro_pct": round(spread_pct, 2)
                })
    
    # Ordena do maior lucro para o menor
    return sorted(oportunidades, key=lambda x: x["lucro_pct"], reverse=True)


def exibir_scanner_arbitragem():
    """Exibe o scanner na tela para o usuário"""
    st.title("🔍 Scanner de Arbitragem")
    st.markdown("Compara preços em tempo real entre bolsas e mostra onde comprar e vender!")
    
    st.info("🔒 **Modo Sinais — Seguro!** Não precisamos de suas chaves. Você executa as operações manualmente nas bolsas.")
    
    moedas = st.multiselect("Escolha as moedas para escanear", 
                            ["BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "AVAX", "MATIC"],
                            default=["BTC", "ETH", "SOL", "XRP"])
    
    if st.button("🔍 ESCANEAR OPORTUNIDADES", type="primary", use_container_width=True):
        with st.spinner("Buscando preços em todas as bolsas..."):
            ops = escanear_oportunidades(moedas)
        
        if not ops:
            st.success("✅ Sem oportunidades no momento. Os preços estão alinhados entre as bolsas.")
            return
        
        st.subheader(f"✅ {len(ops)} Oportunidades Encontradas!")
        st.markdown("---")
        
        for op in ops:
            cor_lucro = "#22c55e" if op["lucro_pct"] >= 1 else "#f59e0b"
            st.markdown(f"""
            <div style='background:rgba(30,41,59,0.7);border-left:4px solid {cor_lucro};border-radius:12px;padding:16px;margin:12px 0;'>
                <h3 style='margin:0 0 10px 0;color:white;'>🪙 {op['moeda']} — Lucro: <span style='color:{cor_lucro};'>{op['lucro_pct']}%</span></h3>
                <p style='margin:4px 0;'>✅ <strong>COMPRAR:</strong> {op['comprar_bolsa']} → US$ {op['comprar_preco']:.4f}</p>
                <p style='margin:4px 0;'>📤 <strong>VENDER:</strong> {op['vender_bolsa']} → US$ {op['vender_preco']:.4f}</p>
                <p style='margin:8px 0 0 0;color:#94a3b8;font-size:13px;'>💡 Compre na bolsa mais barata → transfira → venda na mais cara! Lucro de {op['lucro_pct']}% antes de taxas.</p>
            </div>
            """, unsafe_allow_html=True)
