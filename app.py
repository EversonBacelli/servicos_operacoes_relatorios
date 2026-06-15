import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Configuração da página do Streamlit
st.set_page_config(page_title="Apresentação de Serviços Operacionais", layout="wide")
st.title("🛢️ Visualização de Serviços Operacionais")
st.caption("Exibição isolada com filtros e gráficos dinâmicos para análise operacional.")

# Abas para separar os microsserviços
tab_operacoes, tab_interacoes, tab_inteligencia, tab_recomendacao = st.tabs([
    "🛒 Microsserviço de Operações (API)", 
    "🖱️ Microsserviço de Interações (API)", 
    "🧠 Matriz de Afinidade (API)",
    "🧠 Sistema de Recomendação"
])

# URLs dos Endpoints das APIs
URL_API_OPERACOES = "https://back-operacoes.vercel.app/pedido"
URL_API_INTERACOES = "https://microservico-interacoes.vercel.app/interacoes"
URL_API_MATRIZ = "https://matriz-correlacao.vercel.app/"

# Inicialização dos DataFrames globais
df_op = pd.DataFrame()
df_int = pd.DataFrame()
df_matriz = pd.DataFrame()

# =========================================================================
# CARREGAMENTO CENTRALIZADO DE DADOS (Garante persistência entre as abas)
# =========================================================================
with st.spinner("Sincronizando ecossistema de microsserviços..."):
    # Carga: Operações
    try:
        res = requests.get(URL_API_OPERACOES, timeout=10)
        if res.status_code == 200:
            df_op = pd.DataFrame(res.json())
            if 'quantidade' in df_op.columns:
                df_op['quantidade'] = pd.to_numeric(df_op['quantidade'], errors='coerce')
            if 'preco_unitario' in df_op.columns:
                df_op['preco_unitario'] = pd.to_numeric(df_op['preco_unitario'], errors='coerce')
            if 'subtotal_item' in df_op.columns:
                df_op['subtotal_item'] = pd.to_numeric(df_op['subtotal_item'], errors='coerce')
    except Exception as e:
        st.error(f"Falha ao reter dados de Operações: {e}")

    # Carga: Interações
    try:
        res = requests.get(URL_API_INTERACOES, timeout=10)
        if res.status_code == 200:
            json_completo = res.json()
            lista_docs = json_completo["dados"] if isinstance(json_completo, dict) and "dados" in json_completo else json_completo
            df_int = pd.DataFrame(lista_docs)
    except Exception as e:
        st.error(f"Falha ao reter dados de Interações: {e}")

    # Carga: Matriz de Afinidade
    try:
        res = requests.get(URL_API_MATRIZ, timeout=10)
        if res.status_code == 200:
            dados_json = res.json()
            df_matriz = pd.DataFrame(dados_json["dados"]) if isinstance(dados_json, dict) and "dados" in dados_json else pd.DataFrame(dados_json)
            if not df_matriz.empty:
                col_linhas = 'Unnamed: 0' if 'Unnamed: 0' in df_matriz.columns else df_matriz.columns[0]
                df_matriz = df_matriz.set_index(col_linhas)
                df_matriz = df_matriz.apply(pd.to_numeric, errors='coerce')
                colunas_ordenadas = sorted(df_matriz.columns, key=lambda x: int(x[1:]) if x[1:].isdigit() else x)
                df_matriz = df_matriz[colunas_ordenadas]
    except Exception as e:
        st.error(f"Falha ao mapear Matriz de Afinidade: {e}")

# =========================================================================
# 1. MICROSSERVIÇO DE OPERAÇÕES 
# =========================================================================
with tab_operacoes:
    st.header("Serviço de Operações")
    st.info("Dados e análises dinâmicas da rota de pedidos do microsserviço relacional.")

    if not df_op.empty:
        st.sidebar.header("🎯 Filtros de Operações")
        col_cliente = 'nome_cliente' if 'nome_cliente' in df_op.columns else ('id_cliente' if 'id_cliente' in df_op.columns else None)
        col_categoria = 'nome_categoria' if 'nome_categoria' in df_op.columns else ('id_categoria' if 'id_categoria' in df_op.columns else None)
        
        if col_cliente:
            lista_clientes = ["Todos"] + sorted(df_op[col_cliente].dropna().unique().tolist())
            cliente_selecionado = st.sidebar.selectbox("Filtrar por Cliente:", lista_clientes, key="op_cli")
        
        if col_categoria:
            lista_categorias = ["Todas"] + sorted(df_op[col_categoria].dropna().unique().tolist())
            categoria_selecionada = st.sidebar.selectbox("Filtrar por Categoria:", lista_categorias, key="op_cat")
        
        df_filtrado = df_op.copy()
        if col_cliente and cliente_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado[col_cliente] == cliente_selecionado]
        if col_categoria and categoria_selecionada != "Todas":
            df_filtrado = df_filtrado[df_filtrado[col_categoria] == categoria_selecionada]
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Qtd. de Itens Filtrados", len(df_filtrado))
        with col2:
            if 'subtotal_item' in df_filtrado.columns:
                st.metric("Valor Total Filtrado", f"R$ {df_filtrado['subtotal_item'].sum():,.2f}")
            elif 'preco_unitario' in df_filtrado.columns and 'quantidade' in df_filtrado.columns:
                df_filtrado['subtotal_calculado'] = df_filtrado['preco_unitario'] * df_filtrado['quantidade']
                st.metric("Valor Total Filtrado", f"R$ {df_filtrado['subtotal_calculado'].sum():,.2f}")

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

        st.subheader("📋 Dados Detalhados")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("Aguardando dados estruturados de operações...")

# =========================================================================
# 2. MICROSSERVIÇO DE INTERAÇÕES
# =========================================================================
with tab_interacoes:
    st.header("Serviço de Interações")
    st.info("Análise dinâmica dos logs de cliques e perfil de usuários do microsserviço NoSQL.")

    if not df_int.empty:
        st.sidebar.markdown("---")
        st.sidebar.header("🖱️ Filtros de Interações")
        
        col_classif = 'status_classificacao' if 'status_classificacao' in df_int.columns else None
        if col_classif:
            lista_classif = ["Todas"] + sorted(df_int[col_classif].dropna().unique().tolist())
            classif_selecionada = st.sidebar.selectbox("Filtrar por Classificação:", lista_classif, key="int_class")
        
        todos_anuncios = []
        if 'anuncios_clicados' in df_int.columns:
            for lista in df_int['anuncios_clicados'].dropna():
                if isinstance(lista, list):
                    todos_anuncios.extend(lista)
        todos_anuncios = ["Todos"] + sorted(list(set(todos_anuncios)))
        anuncio_selecionado = st.sidebar.selectbox("Filtrar por Anúncio Clicado:", todos_anuncios, key="int_anun")
        
        df_int_filtrado = df_int.copy()
        if col_classif and classif_selecionada != "Todas":
            df_int_filtrado = df_int_filtrado[df_int_filtrado[col_classif] == classif_selecionada]
            
        if anuncio_selecionado != "Todos" and 'anuncios_clicados' in df_int_filtrado.columns:
            df_int_filtrado = df_int_filtrado[df_int_filtrado['anuncios_clicados'].apply(
                lambda x: anuncio_selecionado in x if isinstance(x, list) else False
            )]

        st.subheader("📊 Análise Visual de Cliques")
        if 'anuncios_clicados' in df_int_filtrado.columns and col_classif:
            df_explodido = df_int_filtrado.explode('anuncios_clicados')
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                st.write("**Total de Cliques por Classificação do Usuário**")
                df_contagem = df_explodido.groupby(col_classif).size().reset_index(name='Total de Cliques')
                st.bar_chart(data=df_contagem, x=col_classif, y='Total de Cliques', color="#ff7f0e")
                
            with col_g2:
                st.write("**Anúncios Mais Clicados (Volume por Código)**")
                df_anuncios_relev = df_explodido.groupby('anuncios_clicados').size().reset_index(name='Cliques')
                st.bar_chart(data=df_anuncios_relev, x='anuncios_clicados', y='Cliques', color="#9467bd")
        else:
            st.warning("Colunas necessárias para os gráficos não encontradas.")

        df_tabela = df_int_filtrado.copy()
        if 'anuncios_clicados' in df_tabela.columns:
            df_tabela['anuncios_clicados'] = df_tabela['anuncios_clicados'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
        mapeamento_colunas = {
            "_id": "ID do Cliente (Mongo)",
            "nome_completo": "Nome do Usuário",
            "anuncios_clicados": "Anúncios Clicados",
            "status_classificacao": "Classificação"
        }
        colunas_existentes = {k: v for k, v in mapeamento_colunas.items() if k in df_tabela.columns}
        df_tabela = df_tabela.rename(columns=colunas_existentes)
        
        st.subheader("📋 Dados Detalhados Filtrados")
        st.dataframe(df_tabela, use_container_width=True)
        st.success(f"Dados filtrados com sucesso: {len(df_tabela)} usuários correspondem aos critérios.")
    else:
        st.warning("Aguardando dados comportamentais de interações...")

# =========================================================================
# 3. MATRIZ DE AFINIDADE
# =========================================================================
with tab_inteligencia:
    st.header("Matriz de Afinidade")
    st.info("Visualização analítica da correlação. Linhas representam Produtos (L) e Colunas representam códigos de Clientes (C).")

    if not df_matriz.empty:
        st.subheader("🔥 Mapa de Calor (Produtos [L] vs Clientes [C])")
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.heatmap(
            df_matriz, 
            annot=True, 
            cmap="YlOrRd", 
            fmt=".2f", 
            linewidths=.8, 
            vmin=0.0, 
            vmax=1.0, 
            ax=ax
        )
        plt.title("Afinidade de Conversão: Cruzamento Comportamental", fontsize=12, pad=15)
        plt.xlabel("Clientes (Código C de Interações)", fontsize=10, labelpad=10)
        plt.ylabel("Produtos (Código L de Operações)", fontsize=10, labelpad=10)
        st.pyplot(fig)
        
        st.subheader("📋 Dados Estruturados de Apoio")
        st.dataframe(df_matriz, use_container_width=True)
    else:
        st.warning("Aguardando cargas da matriz analítica de adjacência...")

# =========================================================================
# 4. SISTEMA DE RECOMENDAÇÃO PREDITIVA GLOBAL (Top 10 Melhores Afinidades)
# =========================================================================
with tab_recomendacao:
    st.header("🧠 Sistema de Recomendação Preditiva Global")
    st.info("Varredura Matricial Completa: Exibindo os 10 cruzamentos com as maiores taxas de afinidade ativa.")

    if not df_op.empty and not df_int.empty and not df_matriz.empty:
        col_nome_cli = 'nome_completo' if 'nome_completo' in df_int.columns else None
        
        if col_nome_cli:
            # 1. Recupera a ordenação real dos usuários mapeados para vincular os códigos 'C1', 'C2' aos nomes reais
            lista_usuarios_mapeados = sorted(df_int[col_nome_cli].unique())
            mapa_codigos_clientes = {f"C{i+1}": nome for i, nome in enumerate(lista_usuarios_mapeados)}
            
            # 2. Transforma a estrutura pivotada da matriz em uma lista linear (melt)
            # Reseta o índice para que a coluna de Produtos ('Produto') volte a ser um campo de dados ativo
            df_linear = df_matriz.reset_index().melt(
                id_vars=[df_matriz.index.name if df_matriz.index.name else df_matriz.columns[0]],
                var_name='Codigo_Cliente',
                value_name='Afinidade'
            )
            df_linear.columns = ['Produto', 'Codigo_Cliente', 'Afinidade']
            
            # 3. Substitui os códigos ('C1', 'C2'...) pelos nomes reais correspondentes dos clientes
            df_linear['Cliente'] = df_linear['Codigo_Cliente'].map(mapa_codigos_clientes)
            
            # Organiza as colunas exatamente no formato solicitado
            df_linear = df_linear[['Cliente', 'Produto', 'Afinidade']]
            
            # 4. Limpeza anti-redundância: Remove linhas onde o cliente já comprou o respectivo produto
            if 'nome_cliente' in df_op.columns and 'nome_produto' in df_op.columns:
                # Cria uma lista de strings combinadas "NomeCliente-NomeProduto" das compras reais
                compras_efetuadas = (df_op['nome_cliente'] + "||" + df_op['nome_produto']).tolist()
                
                # Filtra o DataFrame linear mantendo apenas combinações que não existam nas compras passadas
                df_linear = df_linear[~(df_linear['Cliente'] + "||" + df_linear['Produto']).isin(compras_efetuadas)]

            # 5. Ordena para obter as maiores taxas globais e extrai o Top 10
            top_10_afinidades = df_linear.sort_values(by='Afinidade', ascending=False).head(10)
            
            # --- RENDERIZAÇÃO NA INTERFACE ---
            st.markdown("---")
            st.subheader("📊 Top 10 Conversores de Alta Afinidade (Geral)")
            
            col_rec1, col_rec2 = st.columns([3, 2])
            
            with col_rec1:
                st.write("### Projeção Gráfica de Afinidade Combinada")
                # Cria um identificador visual rápido no gráfico combinando Cliente + Produto
                top_10_afinidades['Target'] = top_10_afinidades['Cliente'] + " (" + top_10_afinidades['Produto'] + ")"
                
                fig_rec_global = px.bar(
                    top_10_afinidades, 
                    x='Afinidade', 
                    y='Target',
                    orientation='h',  # Gráfico de barras horizontais para melhor leitura dos nomes
                    color='Afinidade',
                    color_continuous_scale='YlOrRd',
                    labels={'Target': 'Combinação Alvo', 'Afinidade': 'Taxa de Afinidade'}
                )
                fig_rec_global.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
                st.plotly_chart(fig_rec_global, use_container_width=True)
                
            with col_rec2:
                st.write("### Lista Consolidada de Disparos")
                # Removemos a coluna temporária do gráfico para exibir a tabela perfeitamente limpa
                tabela_exibicao = top_10_afinidades[['Cliente', 'Produto', 'Afinidade']].copy()
                st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)
                
            st.success("Cruzamento de dados matriciais (NoSQL x Relacional) realizado com sucesso para todos os perfis ativos.")
        else:
            st.error("Erro estrutural: Não foi possível mapear a coluna identificadora de usuários para associar as colunas C1, C2...")
    else:
        st.warning("Aguardando o carregamento dos microsserviços para calcular as recomendações globais.")