# Dashboard Analítico Centralizador 📊

Este repositório contém o front-end analítico desenvolvido em **Python** com **Streamlit**, projetado para consolidar e apresentar visualmente os dados de um ecossistema distribuído de microsserviços. 

A aplicação consome dados em tempo real de APIs independentes hospedadas na **Vercel**, eliminando conexões diretas a bancos de dados na camada de apresentação e atuando estritamente como um hub de inteligência de negócios (BI).

🔗 **Acesse a aplicação em produção:** [Clique aqui para visualizar o Dashboard](https://servicosoperacoesrelatorios-y25kt6wb8dfvla87hs7g3k.streamlit.app/)

---

## 🏗️ Arquitetura do Ecossistema

O projeto adota uma abordagem descentralizada, simulando bancos de dados operacionais distintos que são unificados visualmente através deste painel:

1. **Microsserviço de Operações (MySQL / AlwaysData):** Gerencia o fluxo transacional de vendas, clientes, categorias e produtos de forma relacional.
2. **Microsserviço de Interações (MongoDB):** Armazena logs de navegação de usuários e histórico de cliques em anúncios em formato NoSQL/documento.
3. **Módulo de Inteligência (Matriz de Afinidade):** Camada analítica que expõe os coeficientes de correlação gerados via Pandas para alimentar futuros sistemas de recomendação.

---

## 🛠️ Tecnologias Utilizadas no Dashboard

* **Linguagem Principal:** Python 3.10+
* **Framework Web:** Streamlit (Interface reativa de alto desempenho)
* **Manipulação de Dados:** Pandas
* **Visualização de Dados:** Matplotlib & Seaborn (Geração de mapas de calor analíticos)
* **Consumo de APIs:** Requests (Comunicação HTTP síncrona com os microsserviços)

---

## 🖥️ Funcionalidades do Painel

O dashboard é dividido em três abas operacionais isoladas, cada uma focada em seu respectivo serviço:

### 🛒 1. Microsserviço de Operações
* **Filtros Dinâmicos na Barra Lateral:** Filtragem em tempo real por Cliente e Categoria de Produto.
* **Métricas de Performance:** Cálculo automático do total de itens movimentados e faturamento acumulado com base nos filtros aplicados.
* **Gráficos Interativos:** Gráfico de barras exibindo a quantidade de itens por produto e faturamento consolidado por cliente.
* **Auditoria de Dados:** Tabela detalhada contendo o resultado da query relacional completa.

### 🖱️ 2. Microsserviço de Interações
* **Filtro de Logs:** Seleção dinâmica por Classificação de Usuário (Ouro, Prata, Bronze, Latão) e códigos de anúncios específicos.
* **Gráficos de Engajamento:** Volume total de cliques agrupado pelo perfil do usuário e ranking dos anúncios mais clicados do sistema.
* **Tratamento de Dados:** Conversão de arrays complexos do MongoDB em strings limpas e tabulares para o usuário final.

### 🧠 3. Matriz de Afinidade
* **Heatmap Analítico:** Mapa de calor interativo gerado via Seaborn que destaca visualmente, através de gradientes de cores (Amarelo ao Vermelho Escuro), as maiores forças de correlação e probabilidade de conversão entre Anúncios e Produtos.

---

## ⚙️ Instalação e Execução Local

Caso queira rodar o painel em sua máquina local, certifique-se de ter o Python instalado e siga os passos abaixo:

### 1. Instalar as Dependências
Navegue até a pasta raiz do projeto e execute a instalação via pip utilizando o arquivo de requerimentos:
```bash
pip install -r requirements.txt
