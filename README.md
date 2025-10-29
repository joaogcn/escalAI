# ⚽ EscalAI - Análise de Dados do Cartola FC

## 🎯 **Sobre o Projeto**

O **EscalAI** é uma aplicação web desenvolvida em **Streamlit** que combina tecnologia e análise de dados para ajudar você a montar seu time do **Cartola FC** com mais estratégia e confiança.

Com base em dados históricos e informações de mercado em tempo real, o EscalAI oferece uma visão completa do desempenho dos jogadores e das tendências da rodada.

### ✨ **Funcionalidades Principais**

-   **Dashboard Interativo:** Análises visuais sobre o desempenho geral dos jogadores na temporada.
-   **Dicas da Rodada:** Uma página dedicada a recomendações com base em índices de desempenho:
    -   **Top 5 Jogadores por Posição:** Sugestões baseadas no **Índice EscalAI**, que pondera o momento atual (últimas 5 partidas) e a consistência do jogador na temporada.
    -   **Times para Ficar de Olho:** Análise dos times com melhor desempenho nas últimas 5 rodadas, considerando vitórias, gols marcados e saldo de gols.
-   **Bot EscalAI:** Um assistente com inteligência artificial (via Google Gemini) que responde suas perguntas sobre escalação, utilizando o contexto das dicas da rodada para fornecer insights personalizados.

## 🚀 **Instalação e Execução**

### **1. Pré-requisitos**
-   Python 3.8+
-   Git

### **2. Instalação**

```bash
# 1. Clone o repositório
git clone https://github.com/joaogcn/escalAI.git
cd escalAI

# 2. Instale as dependências
pip install -r requirements.txt
```

### **3. Execução

Após a instalação e configuração da API Key, execute os comandos abaixo.

```bash
# 1. Executa o pipeline de processamento de dados
# (Isso gera os dados para as dicas de jogadores e times)
python scripts/run_pipeline.py

# 2. Inicia a aplicação Streamlit
streamlit run EscalAI.py
```

## 📁 **Estrutura do Projeto**

```
escalAI/
├── EscalAI.py             # Aplicativo principal Streamlit
├── requirements.txt       # Dependências Python
├── .streamlit/            # Pasta para configuração do Streamlit
├── scripts/               # Scripts para o pipeline de dados (limpeza, análise, dicas)
├── pages/                 # Páginas da aplicação (Dashboard, Dicas, Bot)
├── dados_cartola/         # Dados brutos, intermediários e visualizações
├── .github/workflows/     # Contém o workflow de sincronização
└── README.md              # Este arquivo
```

## 🤝 **Contribuição**

1.  Faça um Fork do projeto
2.  Crie uma branch para sua nova feature (`git checkout -b feature/nova-feature`)
3.  Faça o commit de suas mudanças (`git commit -m 'Adiciona nova feature'`)
4.  Faça o push para a branch (`git push origin feature/nova-feature`)
5.  Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.