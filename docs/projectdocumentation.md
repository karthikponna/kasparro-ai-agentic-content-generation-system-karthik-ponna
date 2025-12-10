# Project Documentation

## Problem Statement

Design and implement a **modular agentic automation system** that processes a small product dataset and automatically generates structured, machine-readable content pages. The system must demonstrate:

- Multi-agent workflows with clear boundaries
- Automation graphs and orchestration
- Reusable content logic
- Template-based generation
- Structured JSON output
- System abstraction and documentation

## Solution Overview

Built a **LangGraph-based multi-agent content generation system** with 6 specialized agents orchestrated through a state machine workflow. The system:

1. **Parses** product data into validated Pydantic models
2. **Generates** 15+ categorized user questions using LLM
3. **Creates** reusable content transformation blocks
4. **Assembles** three distinct content pages using custom templates
5. **Outputs** machine-readable JSON files

## Scopes & Assumptions

### Scopes

- Single product data processing (GlowBoost Vitamin C Serum)  
- Generation of 15+ categorized questions  
- Three output pages: FAQ, Product, Comparison  
- Machine-readable JSON outputs  
- Multi-agent architecture with LangGraph

### Assumptions

- Output files saved to `output/` directory
- Fictional Product B generated programmatically by LLM


## System Design

### Architecture Overview

The system follows a **directed acyclic graph (DAG)** architecture orchestrated by LangGraph's StateGraph:

<p align="center">
    <img src="static/agentic_architecture.png" alt="Architecture" width="700">
  </a>
</p>

- additionally the main code is organised inside a single folder src/
- used Makefile to run the commands easily
- used uv to stay away from the package dependency conflicts
