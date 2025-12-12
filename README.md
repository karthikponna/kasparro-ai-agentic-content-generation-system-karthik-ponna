# Multi-Agent Content Generation System

A modular agentic automation system built with **LangGraph** that automatically generates structured, machine-readable content pages from product data.

## 🛠️ Tech Stack

- **LangGraph** - Multi-agent workflow orchestration
- **Pydantic** - Data validation and structured outputs
- **OpenAI** - LLM for content generation
- **uv** - Fast Python package management
- **Makefile** - Automation and task running

## 📋 Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key

## 🎯 Getting Started

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
git clone https://github.com/karthikponna/kasparro-ai-agentic-content-generation-system-karthik-ponna.git
cd kasparro-ai-agentic-content-generation-system-karthik-ponna
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

To install the dependencies and activate the virtual environment, run the following commands:

```bash
uv venv .venv
source .venv/bin/activate
uv sync
```

### 3. Running the code

```bash
make run-agent
```

### 4. Running the tests
```bash
make run-test
```


> [!NOTE]
> For more information on the current project please check this file [projectdocumentation.md](./docs/projectdocumentation.md)