# ⚽ EscalAI - Análise de Dados do Cartola FC

## 🎯 **Sobre o Projeto**

O EscalAI é uma aplicação web desenvolvida em Streamlit para análise de dados do Cartola FC. O projeto combina dados históricos, para estudos de desempenho, com dados de mercado ao vivo, fornecendo uma ferramenta completa para auxiliar na escalação de times.

## ⚙️ **Arquitetura de Dados**

Este projeto abandonou o uso de um banco de dados tradicional em favor de uma arquitetura mais simples e automatizada:

1.  **Dados Históricos**: Os dados históricos de rodadas passadas são obtidos do excelente projeto [caRtola](https://github.com/henriquepgomide/caRtola).
2.  **Sincronização Automática**: Uma **GitHub Action** configurada neste repositório é executada semanalmente. Ela clona o repositório `caRtola`, copia os arquivos de dados brutos (`.csv`) e os armazena na pasta `dados_cartola/raw`.
3.  **Consumo Local**: A aplicação Streamlit lê os dados diretamente desses arquivos CSV locais para todas as análises históricas.
4.  **Dados ao Vivo**: Para informações em tempo real, como o status do mercado e os jogadores mais escalados, a aplicação consome as APIs oficiais do Cartola FC.

## 🛠️ **Tecnologias Utilizadas**

-   **Linguagem**: Python
-   **Frontend**: Streamlit
-   **Análise de Dados**: Pandas
-   **Visualização**: Plotly
-   **Automação**: GitHub Actions

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

Após a instalação, execute o comando abaixo. A primeira sincronização de dados pode levar algum tempo para ser concluída pela GitHub Action. Se a pasta `dados_cartola/raw` ainda não existir, você pode rodar a Action manualmente na aba "Actions" do repositório no GitHub.

```bash
streamlit run app.py
```

## 📁 **Estrutura do Projeto**

```
escalAI/
├── app.py                 # Aplicativo principal Streamlit
├── requirements.txt       # Dependências Python
├── dados_cartola/raw/     # (Criado pela Action) Dados históricos em CSV
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