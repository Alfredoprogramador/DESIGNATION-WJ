# DESIGNATION-WJ
Sistema de Gerenciamento de Designações Religiosas Mensais

## 📋 Descrição

Sistema web para gerenciar designações mensais para reuniões religiosas. O sistema distribui automaticamente as seguintes designações entre as pessoas cadastradas:

- **Presidência** (1 pessoa)
- **Leitura** (1 pessoa)
- **Oração Final** (1 pessoa)
- **Áudio & Vídeo** (1 pessoa)
- **Palco** (1 pessoa)
- **Indicador** (2 pessoas)
- **Microfone Volante** (2 pessoas)

### ⚠️ Restrições

- Nenhuma pessoa pode ter mais de 2 designações no mesmo dia
- Somente pessoas marcadas como "disponíveis" recebem designações
- O sistema distribui as designações de forma equilibrada ao longo do mês

## 🚀 Como Usar

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Alfredoprogramador/DESIGNATION-WJ.git
cd DESIGNATION-WJ
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar o Sistema

```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5000`

## 📖 Manual de Uso

### 1. Gerenciar Pessoas

Na aba **"👥 Pessoas"**:
- Adicione pessoas pelo nome
- Marque pessoas como disponíveis ou indisponíveis
- Remova pessoas do sistema

### 2. Gerar Escala Mensal

Na aba **"📅 Gerar Escala"**:
1. Selecione o ano e mês
2. Adicione as datas das reuniões do mês
3. Clique em "🎯 Gerar Escala"

O sistema irá automaticamente distribuir as designações respeitando as restrições.

### 3. Visualizar Escalas

Na aba **"👁️ Ver Escalas"**:
- Selecione o ano e mês
- Clique em "🔍 Buscar" para ver a escala
- Visualize todas as designações organizadas por data
- Exclua escalas antigas se necessário

## 🏗️ Estrutura do Projeto

```
DESIGNATION-WJ/
├── app.py                    # Aplicação Flask (API Backend)
├── models.py                 # Modelos de dados
├── designation_manager.py    # Lógica de gerenciamento
├── requirements.txt          # Dependências Python
├── static/
│   └── index.html           # Interface web
├── data/                     # Dados persistidos (criado automaticamente)
│   ├── people.json
│   └── schedules.json
└── README.md
```

## 🔧 Tecnologias

- **Backend**: Python 3.x + Flask
- **Frontend**: HTML5 + CSS3 + JavaScript (Vanilla)
- **Persistência**: JSON files

## 📝 API Endpoints

### Pessoas
- `GET /api/people` - Listar todas as pessoas
- `POST /api/people` - Adicionar pessoa
- `PUT /api/people/<id>` - Atualizar pessoa
- `DELETE /api/people/<id>` - Remover pessoa

### Designações
- `GET /api/designations` - Listar tipos de designações

### Escalas
- `GET /api/schedules/<year>/<month>` - Obter escala mensal
- `POST /api/schedules/<year>/<month>/generate` - Gerar escala
- `DELETE /api/schedules/<year>/<month>` - Excluir escala
- `GET /api/schedules` - Listar todas as escalas

## 🎯 Funcionalidades

✅ Cadastro de pessoas  
✅ Gerenciamento de disponibilidade  
✅ Geração automática de escalas mensais  
✅ Validação de restrições (max 2 designações/dia)  
✅ Visualização organizada por data  
✅ Persistência de dados  
✅ Interface web responsiva  
✅ Distribuição equilibrada de designações  

## 📄 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
