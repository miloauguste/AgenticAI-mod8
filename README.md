# MediSyn Labs Healthcare Research Assistant (Agentic AI - Mo8)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An AI-powered healthcare research assistant designed to streamline medical literature review, treatment comparisons, and clinical decision support for healthcare professionals at MediSyn Labs.

## 🎯 Overview

The Healthcare Research Assistant leverages AutoGen for orchestration, Google Gemini as the core LLM, and Streamlit for the user interface to provide real-time interaction between medical researchers and AI agents. The system supports literature summarization, treatment comparisons, clinical question answering, and comprehensive report generation.

## 🌟 Key Features

### 🔬 Core Functionality
- **Literature Summarization**: Analyze medical papers and extract key findings
- **Treatment Comparison**: Compare therapies across diseases and populations
- **Clinical Q&A**: Get evidence-based answers to clinical questions
- **Session Memory**: Maintain context across research sessions
- **Human-in-the-Loop**: Approve critical summaries and comparisons
- **Report Generation**: Download comprehensive research reports

### 🛠 Technical Features
- **AutoGen Integration**: State management using LangGraph StateGraph
- **Memory Management**: Short-term and long-term memory with SQLite persistence
- **Message Filtering**: Intelligent filtering of non-informational queries
- **Quality Control**: Confidence scoring and approval workflows
- **Multi-format Export**: Markdown, CSV, and JSON report formats

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for LLM functionality)
- At least 4GB RAM recommended
- Windows 10/11, macOS, or Linux

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd healthcare-research-assistant

# Create virtual environment (Windows)
python -m venv healthcare_assistant_env
healthcare_assistant_env\Scripts\activate

# Create virtual environment (macOS/Linux)
python -m venv healthcare_assistant_env
source healthcare_assistant_env/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env file and add your Google API key
# GOOGLE_API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Application

```bash
# Start web interface (recommended)
python main.py --web

# Or start command-line interface
python main.py --cli

# Or directly run Streamlit
streamlit run streamlit_app.py
```

## 📖 Detailed Setup Instructions

### Virtual Environment Setup

#### Windows
```cmd
# Navigate to project directory
cd C:\path\to\healthcare-research-assistant

# Create virtual environment
python -m venv healthcare_assistant_env

# Activate virtual environment
healthcare_assistant_env\Scripts\activate

# Verify activation (you should see (healthcare_assistant_env) in prompt)
where python
```

#### macOS/Linux
```bash
# Navigate to project directory
cd /path/to/healthcare-research-assistant

# Create virtual environment
python3 -m venv healthcare_assistant_env

# Activate virtual environment
source healthcare_assistant_env/bin/activate

# Verify activation
which python
```

### Dependencies Installation

The `requirements.txt` includes all necessary packages:

```
streamlit==1.28.1
langgraph==0.0.62
langchain==0.1.4
langchain-google-genai==0.0.8
google-generativeai==0.3.2
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.24.3
plotly==5.17.0
typing-extensions==4.8.0
pydantic==2.5.2
requests==2.31.0
beautifulsoup4==4.12.2
```

Install with:
```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file based on `.env.example`:

```env
# Required
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional (defaults provided)
DATABASE_URL=sqlite:///healthcare_memory.db
MAX_SHORT_TERM_QUERIES=7
CONFIDENCE_THRESHOLD=0.7
STREAMLIT_SERVER_PORT=8501
```

## 🎮 Usage Guide

### Web Interface (Recommended)

1. **Start the Application**
   ```bash
   python main.py --web
   ```

2. **Access the Interface**
   - Open your browser to `http://localhost:8501`
   - The application will load with the welcome page

3. **Create a Research Session**
   - Use the sidebar to create a new session
   - Enter your Researcher ID, Project ID, and Disease Focus
   - Click "Start New Session"

4. **Submit Queries**
   - Navigate to the "Query Interface" tab
   - Enter your medical research question
   - Select query type and priority
   - Click "Submit Query"

5. **Review Results**
   - Check the "Research Results" tab for responses
   - Use the "Approvals" tab for human-in-the-loop validation
   - Generate reports in the "Reports" tab

### Command Line Interface

```bash
python main.py --cli
```

Follow the interactive prompts to:
- Enter researcher and project information
- Submit medical queries
- View responses and generate reports
- Use commands like `help`, `report`, `status`, `quit`

### Available Commands

```bash
# Show configuration
python main.py --config

# Clean up old sessions
python main.py --cleanup

# Show version
python main.py --version

# Show help
python main.py --help
```

## 🏗 Architecture Overview

### Core Components

```
├── healthcare_schema.py      # Data schemas and type definitions
├── state_management.py       # StateGraph implementation for workflow
├── memory_manager.py         # Short-term and long-term memory management
├── medical_query_handler.py  # LLM integration for medical queries
├── message_filter.py         # Query filtering and validation
├── human_loop_integration.py # Human-in-the-loop approval system
├── report_generator.py       # Multi-format report generation
├── streamlit_app.py          # Web interface implementation
├── config.py                 # Configuration management
└── main.py                   # Application entry point
```

### Data Flow

```
User Query → Message Filter → State Management → Query Handler
     ↓
Memory Manager ← Human Approval ← Response Generation
     ↓
Report Generator → Export (MD/CSV/JSON)
```

### Memory Architecture

- **Short-term Memory**: Current session queries and responses (max 7 items)
- **Long-term Memory**: SQLite database for persistent storage
- **State Management**: LangGraph StateGraph for workflow orchestration
- **Memory Trimming**: Automatic cleanup based on configurable thresholds

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | None | Yes* |
| `DATABASE_URL` | SQLite database path | `sqlite:///healthcare_memory.db` | No |
| `MAX_SHORT_TERM_QUERIES` | Max queries in short-term memory | 7 | No |
| `CONFIDENCE_THRESHOLD` | Minimum confidence for auto-approval | 0.7 | No |
| `STREAMLIT_SERVER_PORT` | Web interface port | 8501 | No |
| `MOCK_EXTERNAL_APIS` | Use mock data instead of real APIs | true | No |

*Required unless running in mock mode

### Configuration Management

The application supports multiple configuration methods:

1. **Environment Variables** (recommended)
2. **`.env` file** (for development)
3. **JSON configuration file**
4. **Runtime configuration updates**

Example configuration update:
```python
from config import get_config

config = get_config()
config.update_config({
    'MAX_SHORT_TERM_QUERIES': 10,
    'CONFIDENCE_THRESHOLD': 0.8
})
```

## 📊 Features Deep Dive

### Literature Summarization

The system can analyze medical literature and extract:
- Key findings and clinical outcomes
- Treatment efficacy data
- Safety profiles and adverse events
- Population-specific considerations
- Confidence scoring based on source reliability

Example query:
```
"What are the latest findings on mRNA vaccine efficacy in elderly populations?"
```

### Treatment Comparison

Compare multiple treatments across:
- Efficacy metrics
- Safety profiles
- Population differences
- Cost-effectiveness (when available)
- Clinical recommendations

Example query:
```
"Compare the efficacy of Drug A vs Drug B for treating Type 2 diabetes"
```

### Human-in-the-Loop Features

- **Automatic Approval Detection**: Based on confidence scores and content sensitivity
- **Review Workflows**: Structured approval process for critical content
- **Quality Control**: Validation criteria for different content types
- **Escalation System**: For complex or controversial findings

### Report Generation

Generate comprehensive reports including:
- **Session Summary**: Overview of research session
- **Literature Review**: Detailed analysis of reviewed papers
- **Treatment Analysis**: Comparison of therapeutic options
- **Full Research Report**: Comprehensive analysis with recommendations

Export formats:
- Markdown (`.md`)
- CSV (`.csv`) for data tables
- JSON (`.json`) for complete session data

## 🔒 Security and Privacy

### Data Protection
- Local SQLite database (no cloud storage by default)
- Configurable encryption for sensitive data
- API key protection in environment variables
- Rate limiting for external API calls

### Medical Data Handling
- No patient-specific data processing
- Focus on published research and clinical guidelines
- Appropriate disclaimers for generated content
- Human oversight for medical recommendations

### Compliance Considerations
- Designed for research use, not direct patient care
- Requires human validation for clinical decisions
- Maintains audit trail of all approvals and modifications
- Supports data retention policies

## 🧪 Testing

### Manual Testing

1. **Start Application**
   ```bash
   python main.py --web
   ```

2. **Test Basic Functionality**
   - Create a research session
   - Submit various query types
   - Verify responses and confidence scores
   - Test approval workflow

3. **Test Report Generation**
   - Generate different report types
   - Verify export functionality
   - Check report content accuracy

### Configuration Testing

```bash
# Test with mock APIs (no API key required)
echo "MOCK_EXTERNAL_APIS=true" > .env
python main.py --cli

# Test configuration validation
python main.py --config
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'streamlit'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: `ValueError: GOOGLE_API_KEY is required`
```bash
# Solution: Set API key in .env file
echo "GOOGLE_API_KEY=your_key_here" >> .env
```

**Issue**: `Database connection error`
```bash
# Solution: Check database permissions and path
ls -la healthcare_memory.db
```

**Issue**: `Port 8501 already in use`
```bash
# Solution: Change port in configuration
echo "STREAMLIT_SERVER_PORT=8502" >> .env
```

### Logging

Enable debug logging:
```env
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG
ENABLE_DEBUG_LOGGING=true
```

Logs are written to:
- Console output
- `logs/healthcare_assistant.log` (if configured)

### Performance Issues

For better performance:
1. Increase memory limits if processing large datasets
2. Adjust `MAX_SHORT_TERM_QUERIES` for memory usage
3. Enable auto-trimming: `AUTO_TRIM_MEMORY=true`
4. Clean up old sessions regularly: `python main.py --cleanup`

## 🔄 Maintenance

### Regular Maintenance Tasks

1. **Database Cleanup**
   ```bash
   python main.py --cleanup
   ```

2. **Log Rotation**
   - Logs automatically rotate based on size
   - Configure retention: `LOG_RETENTION_DAYS=30`

3. **Dependency Updates**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

4. **Configuration Backup**
   ```bash
   python -c "from config import get_config; get_config().save_to_file('config_backup.json')"
   ```

### Scaling Considerations

For production deployment:
1. **Database**: Consider PostgreSQL for larger datasets
2. **Caching**: Implement Redis for session caching
3. **Load Balancing**: Use multiple Streamlit instances
4. **API Rate Limits**: Monitor and adjust API usage
5. **Security**: Implement authentication and authorization

## 🤝 Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Development Environment**
   ```bash
   python -m venv dev_env
   source dev_env/bin/activate  # or dev_env\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Run in Development Mode**
   ```bash
   echo "ENVIRONMENT=development" >> .env
   python main.py --web
   ```

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and returns
- Include docstrings for all classes and functions
- Maintain comprehensive error handling

### Testing Guidelines

- Test all new features with mock data
- Verify configuration changes don't break existing functionality
- Test both web and CLI interfaces
- Document any new configuration options

## 📚 API Reference

### Core Classes

#### `HealthcareResearchAssistant`
Main application class orchestrating all components.

```python
assistant = HealthcareResearchAssistant()
session_id = assistant.start_research_session("researcher_001", "project_covid", "COVID-19")
result = assistant.process_query(session_id, "What are the latest COVID-19 treatments?")
```

#### `HealthcareAgentState`
Core state schema for healthcare research sessions.

```python
from healthcare_schema import create_initial_state
state = create_initial_state("researcher_001", "project_001", "diabetes")
```

#### `MedicalQueryHandler`
Handles medical query processing with LLM integration.

```python
handler = MedicalQueryHandler(api_key="your_key")
response = handler.process_medical_query(query)
```

### Configuration API

```python
from config import get_config, reload_config

# Get current configuration
config = get_config()

# Update configuration
config.update_config({'MAX_SHORT_TERM_QUERIES': 10})

# Reload from environment
reload_config()
```

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this README thoroughly
2. **Check Configuration**: Verify all environment variables
3. **Check Logs**: Review application logs for error details
4. **Test with Mock Data**: Use `MOCK_EXTERNAL_APIS=true` for testing

### Common Questions

**Q: Can I use this without a Google API key?**
A: Yes, set `MOCK_EXTERNAL_APIS=true` in your `.env` file.

**Q: How do I backup my research data?**
A: The SQLite database file contains all session data. Back up `healthcare_memory.db`.

**Q: Can I customize the report templates?**
A: Yes, modify the templates in `report_generator.py`.

**Q: How do I add new query types?**
A: Extend the `QuerySchema` and update the query handler logic.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AutoGen Framework**: For state management and orchestration
- **Google Gemini**: For advanced language model capabilities
- **Streamlit**: For rapid web application development
- **LangChain**: For LLM integration and tools
- **MediSyn Labs**: For supporting healthcare research innovation

## 📈 Version History

### v1.0.0 (Current)
- Initial release
- Full AutoGen + Gemini + Streamlit integration
- Human-in-the-loop approval system
- Comprehensive reporting capabilities
- SQLite memory management
- Multi-format export support

---

**MediSyn Labs Healthcare Research Assistant** - Empowering medical professionals with AI-driven research capabilities. 🔬💊🏥
