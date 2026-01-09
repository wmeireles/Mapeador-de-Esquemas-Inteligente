# 🗄️ Intelligent Schema Mapper

**🚀 NOVA VERSÃO MELHORADA DISPONÍVEL!** - Veja [README_ENHANCED.md](README_ENHANCED.md) para recursos avançados.

AI-powered database schema mapping tool for legacy system migrations. Uses semantic analysis and LLM verification to map obscure legacy database schemas to modern, clean schemas.

## 🎯 Escolha Sua Versão

### 🚀 **Enhanced App (RECOMENDADO)**
```bash
streamlit run enhanced_app.py
```
**Recursos:** Interface avançada, validação de qualidade, gerenciamento de projetos, múltiplos formatos de export

### 🎯 **Simple App (Sem API)**
```bash
streamlit run simple_app.py
```
**Recursos:** Mapeamento baseado em regras, interface básica, sem necessidade de API

### 🤖 **AI App (Requer API)**
```bash
streamlit run app.py
```
**Recursos:** Mapeamento com IA, busca semântica, verificação LLM

## 🚀 Features

- **Semantic Mapping**: Uses vector embeddings to find semantically similar columns
- **AI Verification**: LLM validates and explains mapping decisions
- **Human-in-the-Loop**: Streamlit UI for reviewing and approving mappings
- **SQL Generation**: Automatically generates migration scripts
- **Multi-language Support**: Handles Portuguese/foreign language legacy schemas

## 📋 Requirements

- Python 3.10+
- Google AI Studio API Key
- SQLite (included with Python)

## 🛠️ Installation

1. **Clone and setup:**
```bash
cd "Intelligent Schema Mapper"
pip install -r requirements.txt
```

2. **Set Google AI Studio API Key:**
```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

## 🎯 Usage

### Phase 1: Setup Mock Databases
```bash
python setup_db.py
```
Creates `legacy.db` (Portuguese/obscure names) and `modern.db` (clean English names).

### Phase 2: Extract Schemas & Create Embeddings
```bash
python extractor.py
```
Extracts schemas and creates vector embeddings for semantic matching.

### Phase 3: Generate Mappings
```bash
python mapper.py
```
Uses AI to generate semantic mappings between legacy and modern schemas.

### Phase 4: Review & Approve (Streamlit UI)
```bash
streamlit run app.py
```
Launch the web interface to review, edit, and approve mappings.

## 📁 Project Structure

```
Intelligent Schema Mapper/
├── setup_db.py          # Phase 1: Create mock databases
├── extractor.py         # Phase 2: Schema extraction & embeddings
├── mapper.py            # Phase 3: AI-powered mapping logic
├── app.py              # Phase 4: Streamlit UI
├── requirements.txt    # Dependencies
├── README.md          # This file
├── legacy.db          # Generated: Legacy database
├── modern.db          # Generated: Modern database
└── chroma_db/         # Generated: Vector embeddings
```

## 🔧 Configuration

The system uses these key components:

- **SQLAlchemy**: Database schema introspection
- **ChromaDB**: Vector storage for semantic search
- **LangChain**: LLM integration and embeddings
- **Google Gemini**: AI models for mapping verification
- **Streamlit**: Web interface for human review
- **Pydantic**: Data validation

## 📊 Example Mappings

| Legacy | Modern | Confidence |
|--------|--------|------------|
| `tb_cli_reg.c_nom` | `customers.full_name` | 0.92 |
| `tb_vendas_hdr.dt_vnd` | `orders.order_date` | 0.88 |
| `tb_prod_cat.preco_unit` | `products.unit_price` | 0.85 |

## 🎮 Demo Workflow

1. **Setup**: Run `setup_db.py` to create sample databases
2. **Extract**: Run `extractor.py` to analyze schemas and create embeddings
3. **Map**: Run `mapper.py` to generate AI mappings (optional - can be done via UI)
4. **Review**: Run `streamlit run app.py` and navigate through:
   - Schema Overview: See both database structures
   - Generate Mappings: Create AI-powered mappings
   - Review Mappings: Approve/edit individual mappings
   - Generate Script: Download final SQL migration script

## 🔍 How It Works

1. **Schema Extraction**: SQLAlchemy inspects database structures
2. **Embedding Creation**: Table/column descriptions converted to vectors
3. **Semantic Search**: ChromaDB finds similar modern schema elements
4. **LLM Verification**: Google Gemini validates and explains mappings
5. **Human Review**: Streamlit interface for final approval
6. **Script Generation**: Creates executable SQL migration scripts

## ⚠️ Notes

- Requires Google AI Studio API key for embeddings and LLM verification
- Demo uses SQLite databases - easily adaptable to other databases
- Vector embeddings are persisted in `chroma_db/` directory
- Confidence scores help prioritize manual review efforts

## 🚀 Next Steps

- Add support for PostgreSQL, MySQL, SQL Server
- Implement data type transformation suggestions
- Add batch processing for large schemas
- Include data quality validation
- Support for complex relationships and constraints