# ⚽ EscalAI - Análise de Dados do Cartola FC

## 🎯 **Sobre o Projeto**

O **EscalAI** é uma aplicação web desenvolvida em **Streamlit** que combina tecnologia e análise de dados para ajudar você a montar seu time do **Cartola FC** com mais estratégia e confiança.
Com base em dados históricos e informações de mercado em tempo real, o EscalAI oferece uma visão completa do desempenho dos jogadores e das tendências da rodada.

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

Após a instalação, execute o comando abaixo para o pipeline de dados e em seguida para rodar a aplicação.

```bash
# Executa o pipeline de processamento de dados
python scripts/run_pipeline.py

# Inicia a aplicação Streamlit
streamlit run EscalAI.py
```

## 📁 **Estrutura do Projeto**

```
escalAI/
├── EscalAI.py             # Aplicativo principal Streamlit
├── requirements.txt       # Dependências Python
├── scripts/               # Scripts para o pipeline de dados
├── pages/                 # Páginas da aplicação Streamlit
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