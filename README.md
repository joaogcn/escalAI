# ⚽ EscalAI - Cartola FC

## 🎯 **Sobre o Projeto**
EscalAI é uma aplicação web desenvolvida em Streamlit que consome dados das APIs oficiais do Cartola FC e os armazena em um banco de dados Supabase. O foco é exclusivamente nos dados do mercado atual, fornecendo dashboards interativos para análise de jogadores e clubes.

## 🚀 **Funcionalidades Principais**

### 📊 **Dashboard do Mercado**
- Status atual do mercado
- Destaques e estatísticas
- Resumo de jogadores e clubes

### 👥 **Gestão de Jogadores**
- Lista completa de jogadores no mercado
- Filtros por posição, clube e status
- Análise de preços e médias
- Gráficos de distribuição

### 🏆 **Gestão de Clubes**
- Informações dos clubes ativos
- Estatísticas de jogadores por clube
- Visualizações gráficas

### 📈 **Análises e Relatórios**
- Distribuição de preços
- Análise de médias
- Comparativos e métricas

## 🛠️ **Tecnologias Utilizadas**

- **Frontend**: Streamlit
- **Backend**: Python
- **Banco de Dados**: Supabase (PostgreSQL)
- **APIs**: Cartola FC Oficiais
- **Visualização**: Plotly

## 📋 **Estrutura do Banco de Dados**

### **Tabelas Principais**
- **`clubes`**: Informações dos clubes no mercado
- **`jogadores`**: Dados dos jogadores (posição e status diretos)
- **`mercado`**: Status atual do mercado

### **Vantagens da Estrutura Otimizada**
- ✅ Sem JOINs desnecessários
- ✅ Dados sempre sincronizados
- ✅ Consultas mais rápidas
- ✅ Manutenção simplificada

## 🚀 **Instalação e Configuração**

### **1. Pré-requisitos**
- Python 3.8+
- Conta no Supabase
- Credenciais das APIs do Cartola FC

### **2. Instalação**
```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd escalai

# Instalar dependências
pip install -r requirements.txt
```

### **3. Configuração do Supabase**
1. Crie um projeto no Supabase
2. Configure as variáveis de ambiente:
   ```bash
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_do_supabase
   ```
3. Execute os scripts SQL na ordem:
   - `safe_migration.sql` (migração segura)
   - `optimized_schema.sql` (esquema completo)

### **4. Execução**
```bash
streamlit run app.py
```

## 📊 **APIs Consumidas**

- **Status do Mercado**: `/mercado/status`
- **Jogadores**: `/atletas/mercado`
- **Destaques**: `/mercado/destaques`
- **Pontuações**: `/atletas/pontuados`

## 🔧 **Solução de Problemas**

### **Erro de Coluna Inexistente**
Se encontrar erro `column "posicao" does not exist`:
1. Execute `safe_migration.sql` primeiro
2. Depois execute `optimized_schema.sql`
3. Teste o app novamente

### **Problemas de Conexão**
- Verifique as credenciais do Supabase
- Confirme se o banco foi configurado corretamente
- Teste a conexão com `test_supabase.py`

## 📁 **Estrutura do Projeto**

```
escalai/
├── app.py                 # Aplicativo principal
├── safe_migration.sql     # Migração segura do banco
├── optimized_schema.sql   # Esquema otimizado
├── requirements.txt       # Dependências Python
├── .streamlit/           # Configurações do Streamlit
├── INSTRUCOES.md         # Instruções rápidas
└── README.md             # Este arquivo
```

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 **Suporte**

Para dúvidas ou problemas:
1. Verifique o arquivo [INSTRUCOES.md](INSTRUCOES.md)
2. Consulte a documentação do Streamlit e Supabase
3. Abra uma issue no repositório

---

**Desenvolvido com ❤️ para a comunidade do Cartola FC**
