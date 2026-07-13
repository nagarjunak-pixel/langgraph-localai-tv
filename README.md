# 📺 LangGraph LocalAI TV Pipeline

**A three-stage news production pipeline built with LangGraph** — designed for real workflows that branch, loop, wait for human input, and recover from errors.

> Part of the [AY Automate](https://github.com/nagarjunak-pixel) AI framework demo series.

## 🏗 Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Stage 1        │     │  Human Approval   │     │  Stage 2           │
│  Fetch Headlines│────▶│  Gate (CLI/Auto)  │────▶│  Generate Raw Video│
│  (RSS/API)      │     │  ✓ Approve/Reject │     │  (Mock/API)        │
└─────────────────┘     └──────────────────┘     └─────────┬──────────┘
                                                           │
                        ┌──────────────────┐               │
                        │  Stage 3         │◀──────────────┘
                        │  Compile Bulletin│
                        │  (JSON/Text)     │
                        └──────────────────┘
```

## ✨ Features

- **🔄 Checkpoint Persistence** — SQLite-based state recovery; resume any failed run
- **🧑‍💼 Human-in-the-Loop** — CLI interactive approval or auto-approve mode
- **⚡ Error Recovery** — Each stage handles failures gracefully with retry support
- **📰 RSS Feed Integration** — Configurable news sources (AP/TG/India tech)
- **🎬 Video Generation** — Mock mode for demos, real API hook for production

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/nagarjunak-pixel/langgraph-localai-tv.git
cd langgraph-localai-tv
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys (optional — works without them)
```

### 3. Run

```bash
# Interactive mode (with human approval)
python pipeline.py

# Auto-approve mode (for demos/testing)
python pipeline.py --auto

# Resume a failed run
python pipeline.py --resume abc12345
```

## 📁 Project Structure

```
langgraph-localai-tv/
├── pipeline.py              # Main LangGraph pipeline runner
├── human_approval.py        # Human-in-the-loop approval gate
├── checkpoints.py           # SQLite checkpoint store
├── nodes/
│   ├── headline_fetcher.py  # RSS feed headline fetching
│   ├── video_generator.py   # Video script + generation
│   └── bulletin_compiler.py # Final bulletin assembly
├── docs/                    # Documentation website (Netlify)
├── requirements.txt
├── .env.example
└── .gitignore
```

## 📖 Documentation

**Live docs: [https://langgraph-localai-tv.netlify.app](https://langgraph-localai-tv.netlify.app)

## 🎓 Learning Points

This project demonstrates:
1. **LangGraph StateGraph** — Typed state flowing through pipeline nodes
2. **Checkpoint Persistence** — Crash recovery via SQLite
3. **Human Approval Gates** — Interactive CLI + auto-approve modes
4. **Error Recovery** — Graceful degradation at each stage
5. **Modular Node Design** — Each stage is independently testable

## 🔗 Related Projects

| Project | Framework | Purpose |
|---------|-----------|---------|
| [CrewAI Telugu Newsroom](https://github.com/nagarjunak-pixel/crewai-telugu-newsroom) | CrewAI | Multi-agent news crew |
| [Firecrawl NEXUS RSS](https://github.com/nagarjunak-pixel/firecrawl-nexus-rss) | Firecrawl | Web scraping aggregator |
| [DeerFlow Research Agent](https://github.com/nagarjunak-pixel/deerflow-research-agent) | DeerFlow | Long-horizon research |

## 📄 License

MIT License — Built for [Surya Agentic Academy](https://github.com/nagarjunak-pixel)
