import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração da página do Streamlit
st.set_page_config(page_title="Apresentação de Serviços Operacionais", layout="wide")
st.title("🛢️ Visualização de Serviços Operacionais")
st.caption("Exibição isolada com filtros e gráficos dinâmicos para análise operacional.")

# Abas para separar os microsserviços
tab_operacoes, tab_interacoes, tab_inteligencia = st.tabs([
    "🛒 Microsserviço de Operações (API)", 
    "🖱️ Microsserviço de Interações (API)", 
    "🧠 Matriz de Afinidade (API)"
])

# =========================================================================
# 1. MICROSSERVIÇO DE OPERAÇÕES (Com Filtros e Gráficos)
# =========================================================================
with tab_operacoes:
    st.header("Serviço de Operações")
    st.info("Dados e análises dinâmicas da rota de pedidos do microsserviço relacional.")

    # URL da sua API de Operações
    URL_API_OPERACOES = "https://back-operacoes.vercel.app/pedido"

    try:
        with st.spinner("Buscando dados de operações..."):
            resposta_op = requests.get(URL_API_OPERACOES, timeout=10)
        
        if resposta_op.status_code == 200:
            df_op = pd.DataFrame(resposta_op.json())
            
            # Garante que as colunas numéricas sejam tratadas como números para os gráficos
            if 'quantidade' in df_op.columns:
                df_op['quantidade'] = pd.to_numeric(df_op['quantidade'], errors='coerce')
            if 'preco_unitario' in df_op.columns:
                df_op['preco_unitario'] = pd.to_numeric(df_op['preco_unitario'], errors='coerce')
            if 'subtotal_item' in df_op.columns:
                df_op['subtotal_item'] = pd.to_numeric(df_op['subtotal_item'], errors='coerce')
            
            # --- SEÇÃO DE FILTROS (Criada na Barra Lateral / Sidebar) ---
            st.sidebar.header("🎯 Filtros de Operações")
            
            col_cliente = 'nome_cliente' if 'nome_cliente' in df_op.columns else ('id_cliente' if 'id_cliente' in df_op.columns else None)
            col_categoria = 'nome_categoria' if 'nome_categoria' in df_op.columns else ('id_categoria' if 'id_categoria' in df_op.columns else None)
            
            # Filtro de Clientes
            if col_cliente:
                lista_clientes = ["Todos"] + sorted(df_op[col_cliente].dropna().unique().tolist())
                cliente_selecionado = st.sidebar.selectbox("Filtrar por Cliente:", lista_clientes)
            
            # Filtro de Categorias
            if col_categoria:
                lista_categorias = ["Todas"] + sorted(df_op[col_categoria].dropna().unique().tolist())
                categoria_selecionada = st.sidebar.selectbox("Filtrar por Categoria:", lista_categorias)
            
            # Aplicando os filtros no DataFrame
            df_filtrado = df_op.copy()
            if col_cliente and cliente_selecionado != "Todos":
                df_filtrado = df_filtrado[df_filtrado[col_cliente] == cliente_selecionado]
            if col_categoria and categoria_selecionada != "Todas":
                df_filtrado = df_filtrado[df_filtrado[col_categoria] == categoria_selecionada]
                
            # --- EXIBIÇÃO DE MÉTRICAS RÁPIDAS ---
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Qtd. de Itens Filtrados", len(df_filtrado))
            with col2:
                if 'subtotal_item' in df_filtrado.columns:
                    st.metric("Valor Total Filtrado", f"R$ {df_filtrado['subtotal_item'].sum():,.2f}")
                elif 'preco_unitario' in df_filtrado.columns and 'quantidade' in df_filtrado.columns:
                    df_filtrado['subtotal_calculado'] = df_filtrado['preco_unitario'] * df_filtrado['quantidade']
                    st.metric("Valor Total Filtrado", f"R$ {df_filtrado['subtotal_calculado'].sum():,.2f}")

            # --- SEÇÃO DE GRÁFICOS VISUAIS ---
            st.subheader("📊 Análise Visual (Gráficos)")
            graf_col1, graf_col2 = st.columns(2)
            
            with graf_col1:
                st.write("**Quantidade de Itens por Produto**")
                if 'nome_produto' in df_filtrado.columns and 'quantidade' in df_filtrado.columns:
                    df_prod_qtd = df_filtrado.groupby('nome_produto')['quantidade'].sum().reset_index()
                    st.bar_chart(data=df_prod_qtd, x='nome_produto', y='quantidade', color="#2ca02c")
                else:
                    st.warning("Dados insuficientes para gerar gráfico de produtos.")
                    
            with graf_col2:
                st.write("**Faturamento por Cliente (Subtotal)**")
                col_subtotal = 'subtotal_item' if 'subtotal_item' in df_filtrado.columns else ('subtotal_calculado' if 'subtotal_calculado' in df_filtrado.columns else None)
                
                if col_subtotal and col_cliente and col_cliente in df_filtrado.columns:
                    df_cli_fat = df_filtrado.groupby(col_cliente)[col_subtotal].sum().reset_index()
                    st.bar_chart(data=df_cli_fat, x=col_cliente, y=col_subtotal, color="#1f77b4")
                else:
                    st.warning("Dados insuficientes para gráfico de faturamento.")

            # --- TABELA DE DADOS FILTRADOS ---
            st.subheader("📋 Dados Detalhados")
            st.dataframe(df_filtrado, use_container_width=True)
            
        else:
            st.error(f"Erro na API de Operações: Status {resposta_op.status_code}")
    except Exception as e:
        st.error(f"Não foi possível conectar à API de Operações: {e}")


# =========================================================================
# 2. MICROSSERVIÇO DE INTERAÇÕES (MongoDB)
# =========================================================================
with tab_interacoes:
    st.header("Serviço de Interações")
    st.info("Dados consumidos da rota de logs do microsserviço NoSQL.")

    URL_API_INTERACOES = "https://microservico-interacoes.vercel.app/interacoes"

    try:
        with st.spinner("Buscando dados de interações..."):
            resposta_int = requests.get(URL_API_INTERACOES, timeout=10)
            
        if resposta_int.status_code == 200:
            df_interacoes = pd.DataFrame(resposta_int.json())
            st.dataframe(df_interacoes, use_container_width=True)
            st.success(f"Dados carregados: {len(df_interacoes)} documentos encontrados.")
        else:
            st.error(f"Erro na API de Interações: Status {resposta_int.status_code}")
    except Exception as e:
        st.error(f"Não foi possível conectar à API de Interações: {e}")


# =========================================================================
# 3. MATRIZ DE AFINIDADE (Correção do Heatmap Visual)
# =========================================================================
with tab_inteligencia:
    st.header("Matriz de Afinidade")
    st.info("Visualização analítica da correlação entre Anúncios (Logs) e Produtos.")

    URL_API_MATRIZ = "https://matriz-correlacao.vercel.app/"

    try:
        with st.spinner("Buscando dados da matriz de afinidade..."):
            resposta_matriz = requests.get(URL_API_MATRIZ, timeout=10)
            
        if resposta_matriz.status_code == 200:
            dados_json = resposta_matriz.json()
            
            # Se a API te devolver uma lista cujo primeiro elemento é a chave "dados", resolvemos assim:
            if isinstance(dados_json, dict) and "dados" in dados_json:
                df_matriz = pd.DataFrame(dados_json["dados"])
            else:
                df_matriz = pd.DataFrame(dados_json)
            
            # --- CORREÇÃO CRUCIAL DA ESTRUTURA DA MATRIZ ---
            # Identifica qual coluna guarda os IDs dos anúncios (L1, L2...)
            col_anuncio = 'Unnamed: 0' if 'Unnamed: 0' in df_matriz.columns else df_matriz.columns[0]
            
            # Definimos os Anúncios como o índice real do Pandas para limpar o lado esquerdo do gráfico
            df_matriz = df_matriz.set_index(col_anuncio)
            
            # Garante que todas as colunas de produtos (C1 a C10) sejam estritamente numéricas (float)
            df_matriz = df_matriz.apply(pd.to_numeric, errors='coerce')
            
            # Ordena as colunas de C1 a C10 para o gráfico não ficar bagunçado
            colunas_ordenadas = sorted(df_matriz.columns, key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
            df_matriz = df_matriz[colunas_ordenadas]

            # --- RENDERIZAÇÃO DO HEATMAP CORRETO ---
            st.subheader("🔥 Mapa de Calor (Anúncios vs Produtos)")
            

            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # O 'vmin=0' e 'vmax=1' ajustam o indicador da direita para a escala real de probabilidade (0% a 100%)
            sns.heatmap(
                df_matriz, 
                annot=True,      # Coloca os números limpos dentro das células
                cmap="YlOrRd",   # Paleta de cor indo do amarelo ao vermelho escuro
                fmt=".2f",       # Limita a duas casas decimais dentro dos quadrados
                linewidths=.8,   # Separação elegante entre os blocos
                vmin=0.0,        
                vmax=1.0,        
                ax=ax
            )
            
            plt.title("Afinidade de Conversão: Cruzamento Relacional", fontsize=12, pad=15)
            plt.xlabel("Produtos (Operações)", fontsize=10, labelpad=10)
            plt.ylabel("Anúncios (Interações)", fontsize=10, labelpad=10)
            plt.xticks(rotation=0) # Mantém C1, C2... retos na horizontal para facilitar a leitura
            plt.yticks(rotation=0) # Mantém L1, L2... retos na vertical
            
            st.pyplot(fig)
            
            # Exibição da tabela pura tratada logo abaixo do gráfico
            st.subheader("📋 Dados Estruturados de Apoio")
            st.dataframe(df_matriz, use_container_width=True)
            
        else:
            st.error(f"Erro na API da Matriz: Status {resposta_matriz.status_code}")
    except Exception as e:
        st.error(f"Não foi possível estruturar a Matriz de Afinidade: {e}")