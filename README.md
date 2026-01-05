# Literature Review AI Assistant

An AI-powered web application that helps researchers conduct thorough literature reviews with chain-of-thought reasoning and structured output suitable for peer-reviewed articles.

## Features

- **Multi-Source Search**: Search PubMed and Semantic Scholar simultaneously for comprehensive coverage
- **AI-Powered Analysis**: Uses DeepSeek LLM to analyze papers and extract key findings
- **Chain-of-Thought Reasoning**: Visual timeline showing step-by-step how insights were derived
- **Relevance Scoring**: Automatically scores papers based on relevance to your research question
- **Theme Identification**: Identifies common themes, contradictions, and research gaps across papers
- **Review Generation**: Generates structured literature reviews ready for peer-reviewed articles
- **Export Options**: Copy or download reviews as Markdown

## Tech Stack

**Backend**
- Python 3.9+
- FastAPI
- SQLAlchemy + SQLite
- OpenAI-compatible API (DeepSeek)

**Frontend**
- React 19 + TypeScript
- Vite
- Tailwind CSS
- React Router

## Installation

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- DeepSeek API key (or other OpenAI-compatible API)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API key:
# DEEPSEEK_API_KEY=your_api_key_here

# Start the server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. **Create a New Review**: Click "New Review" and enter your research topic, domain, and research question

2. **Search Literature**: Enter search terms to find relevant papers from PubMed and Semantic Scholar

3. **Start Analysis**: Click "Start Full Analysis" to automatically:
   - Search for papers
   - Score relevance of each paper
   - Extract key findings
   - Identify themes, gaps, and contradictions

4. **View Chain of Thought**: Watch the "Insights" tab to see how the AI derives its conclusions step-by-step

5. **Generate Review**: Once analysis is complete, generate a structured literature review suitable for academic publication

## Project Structure

```
literature-ai-assist/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── review.py        # Review session model
│   │   │   ├── paper.py         # Paper model
│   │   │   └── insight.py       # Chain-of-thought insights
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   │   ├── reviews.py       # Review CRUD operations
│   │   │   ├── papers.py        # Paper search and management
│   │   │   └── analysis.py      # Analysis pipeline
│   │   └── services/            # Business logic
│   │       ├── pubmed.py        # PubMed API integration
│   │       ├── semantic_scholar.py  # Semantic Scholar API
│   │       └── llm_service.py   # LLM integration
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/          # React components
        │   ├── SearchPanel.tsx
        │   ├── PaperList.tsx
        │   ├── PaperCard.tsx
        │   ├── InsightTimeline.tsx
        │   ├── ReviewEditor.tsx
        │   └── ProgressIndicator.tsx
        ├── pages/               # Page components
        │   ├── Home.tsx
        │   └── ReviewSession.tsx
        ├── services/            # API client
        └── types/               # TypeScript definitions
```

## API Endpoints

### Reviews
- `POST /api/reviews` - Create new review session
- `GET /api/reviews` - List all reviews
- `GET /api/reviews/{id}` - Get review details
- `DELETE /api/reviews/{id}` - Delete review

### Papers
- `POST /api/papers/search` - Search literature sources
- `POST /api/papers/{review_id}/add` - Add paper to review
- `GET /api/papers/{review_id}/list` - List papers in review

### Analysis
- `POST /api/analysis/{review_id}/start` - Start analysis pipeline
- `GET /api/analysis/{review_id}/status` - Get analysis progress
- `GET /api/analysis/{review_id}/insights` - Get chain-of-thought insights
- `POST /api/analysis/{review_id}/generate-review` - Generate literature review

## Configuration

Environment variables (set in `backend/.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | Required |
| `DEEPSEEK_BASE_URL` | API base URL | `https://api.deepseek.com/v1` |
| `DEEPSEEK_MODEL` | Model to use | `deepseek-chat` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./literature_reviews.db` |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional, for higher rate limits | - |

## Using with Other LLM Providers

The application uses an OpenAI-compatible API client. To use other providers:

**OpenAI:**
```env
DEEPSEEK_API_KEY=your_openai_key
DEEPSEEK_BASE_URL=https://api.openai.com/v1
DEEPSEEK_MODEL=gpt-4
```

**Local LLM (Ollama):**
```env
DEEPSEEK_API_KEY=not-needed
DEEPSEEK_BASE_URL=http://localhost:11434/v1
DEEPSEEK_MODEL=llama2
```

## License

MIT License

## Acknowledgments

- [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) for biomedical literature access
- [Semantic Scholar API](https://www.semanticscholar.org/product/api) for academic paper data
- [DeepSeek](https://www.deepseek.com/) for LLM capabilities
