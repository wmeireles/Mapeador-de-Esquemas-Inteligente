# 🗄️ Enhanced Intelligent Schema Mapper

AI-powered database schema mapping tool for legacy system migrations with advanced features for enterprise use.

## 🚀 New Enhanced Features

### ✨ **Core Improvements**
- **Enhanced UI**: Advanced filtering, sorting, and bulk operations
- **Data Quality Validation**: Comprehensive data quality assessment
- **Project Management**: Save/load mapping projects and configurations
- **Custom Rules Engine**: Define custom mapping patterns
- **Multiple Export Formats**: CSV, JSON, Excel with detailed reports
- **Validation Scripts**: Auto-generate data validation queries

### 📊 **Advanced Analytics**
- **Quality Scoring**: 0-100 data quality score with detailed breakdown
- **Mapping Confidence**: Enhanced confidence scoring with visual indicators
- **Progress Tracking**: Real-time approval rate and completion status
- **Detailed Reports**: Comprehensive mapping reports with suggestions

### 🔧 **Enterprise Features**
- **Configuration Management**: Project templates and reusable configurations
- **Batch Processing**: Approve multiple mappings at once
- **Data Transformation Suggestions**: Smart recommendations for data cleanup
- **Audit Trail**: Track mapping decisions and changes

## 📁 Enhanced Project Structure

```
Intelligent Schema Mapper/
├── 🎯 Core Files
│   ├── setup_db.py              # Database setup
│   ├── extractor.py             # Schema extraction
│   ├── mapper.py                # AI-powered mapping (with API)
│   ├── simple_mapper.py         # Rule-based mapping (no API)
│   └── app.py                   # Original Streamlit UI
│
├── 🚀 Enhanced Features
│   ├── enhanced_app.py          # Advanced UI with all features
│   ├── config_manager.py        # Project configuration management
│   ├── data_quality.py          # Data quality validation
│   └── simple_app.py            # Simplified UI (no API required)
│
├── 📋 Configuration
│   ├── requirements.txt         # Basic dependencies
│   ├── requirements_enhanced.txt # All dependencies
│   ├── .env.example            # Environment template
│   └── .gitignore              # Git ignore rules
│
├── 📊 Generated Files
│   ├── legacy.db               # Sample legacy database
│   ├── modern.db               # Sample modern database
│   ├── configs/                # Saved project configurations
│   └── chroma_db/              # Vector embeddings (if using AI)
│
└── 📖 Documentation
    └── README.md               # This file
```

## 🛠️ Installation & Setup

### 1. **Basic Setup**
```bash
git clone <repository-url>
cd "Intelligent Schema Mapper"
pip install -r requirements_enhanced.txt
```

### 2. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google AI Studio API key
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. **Initialize Sample Data**
```bash
python setup_db.py
```

## 🎯 Usage Options

### 🚀 **Option 1: Enhanced App (Recommended)**
Full-featured application with all advanced capabilities:
```bash
streamlit run enhanced_app.py
```

**Features:**
- ✅ Advanced filtering and sorting
- ✅ Data quality validation
- ✅ Project management
- ✅ Custom mapping rules
- ✅ Multiple export formats
- ✅ Detailed analytics

### 🎯 **Option 2: Simple App (No API Required)**
Works without Google AI Studio API:
```bash
streamlit run simple_app.py
```

**Features:**
- ✅ Rule-based mapping
- ✅ Basic UI interface
- ✅ SQL script generation
- ❌ No AI-powered analysis
- ❌ Limited customization

### 🤖 **Option 3: AI-Powered App (API Required)**
Original app with Google AI integration:
```bash
streamlit run app.py
```

**Features:**
- ✅ AI-powered semantic mapping
- ✅ Vector similarity search
- ✅ LLM verification
- ⚠️ Requires Google AI Studio API
- ⚠️ Subject to API quotas

## 📊 Feature Comparison

| Feature | Enhanced App | Simple App | AI App |
|---------|-------------|------------|--------|
| **UI Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Mapping Accuracy** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Data Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Customization** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **No API Required** | ✅ | ✅ | ❌ |
| **Enterprise Ready** | ✅ | ❌ | ❌ |

## 🎮 Quick Start Guide

### 1. **Schema Overview**
- View both legacy and modern database structures
- See table relationships and data types
- Get statistics and metadata

### 2. **Configure Custom Rules** (Enhanced App)
```
Legacy Pattern: c_*     → Modern Pattern: *_name
Legacy Pattern: dt_*    → Modern Pattern: *_date
Legacy Pattern: vl_*    → Modern Pattern: *_amount
```

### 3. **Generate Mappings**
- Click "Start Mapping Process"
- Review confidence scores and suggestions
- Use filters to focus on specific issues

### 4. **Review & Approve**
- Filter by confidence level or table
- Bulk approve high-confidence mappings
- Edit individual mappings as needed

### 5. **Export Results**
- Generate SQL migration scripts
- Export detailed reports (Excel, CSV, JSON)
- Download validation queries

## 📋 Data Quality Features

### **Automatic Detection**
- ✅ Null value analysis
- ✅ Email format validation
- ✅ Phone number consistency
- ✅ Date format issues
- ✅ Duplicate detection
- ✅ Data type mismatches

### **Quality Scoring**
- **100-90**: Excellent quality
- **89-70**: Good quality (minor issues)
- **69-50**: Fair quality (needs attention)
- **<50**: Poor quality (requires cleanup)

### **Improvement Suggestions**
- Automated recommendations for data cleanup
- SQL scripts for common fixes
- Best practices for data governance

## 🔧 Configuration Management

### **Save Project**
```python
from config_manager import ConfigManager, ProjectConfig

config = ProjectConfig(
    name="My Migration Project",
    description="ERP to Cloud migration",
    # ... other settings
)

manager = ConfigManager()
manager.save_project(config)
```

### **Load Project**
```python
config = manager.load_project("my_project.json")
```

## 📊 Export Options

### **SQL Scripts**
- Migration INSERT statements
- Data validation queries
- Rollback scripts

### **Reports**
- **Excel**: Multi-sheet with summary and details
- **CSV**: Simple tabular format
- **JSON**: Structured data for APIs
- **Markdown**: Human-readable reports

## ⚠️ Troubleshooting

### **Google AI API Issues**
```bash
# Check API key
echo $GOOGLE_API_KEY

# Use simple mapper instead
python simple_mapper.py
```

### **Database Connection Issues**
```bash
# Recreate sample databases
python setup_db.py
```

### **Missing Dependencies**
```bash
# Install all dependencies
pip install -r requirements_enhanced.txt
```

## 🚀 Next Steps & Roadmap

### **Planned Features**
- [ ] PostgreSQL/MySQL support
- [ ] Real-time collaboration
- [ ] API endpoints for integration
- [ ] Machine learning model training
- [ ] Advanced data profiling
- [ ] Automated testing framework

### **Enterprise Extensions**
- [ ] LDAP/SSO integration
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Scheduled migrations
- [ ] Multi-tenant support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📧 **Email**: [your-email@domain.com]
- 💬 **Issues**: [GitHub Issues](link-to-issues)
- 📖 **Wiki**: [Project Wiki](link-to-wiki)
- 🎥 **Demos**: [Video Tutorials](link-to-videos)

---

**Made with ❤️ for database migration professionals**