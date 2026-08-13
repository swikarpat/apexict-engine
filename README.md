# 🎯 ApexICT Engine

**Private AI Search Engine & Knowledge Base for ICT Trading Concepts**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-red?logo=qdrant)](https://qdrant.tech/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-white)](https://ollama.ai/)

ApexICT is a 100% local, private RAG (Retrieval-Augmented Generation) search engine designed to index, normalize, and search hundreds of hours of Michael Huddleston's (The Inner Circle Trader) YouTube mentorships. 

It allows non-native English speakers to ask casual trading questions, normalizes them into strict ICT terminology using a local LLM, and returns exact, clickable video timestamps embedded directly in a Next.js Command Center.

---

## 🚀 Core Architecture

### 1. 📥 Stealth Ingestion Pipeline
* Bypasses YouTube JS Bot Challenges using `yt-dlp` and authenticated cookie sessions.
* Automatically filters out outdated content (pre-2024) to ensure only the most refined trading models are indexed.
* **Delta Sync:** Includes a `sync_latest.py` script that calculates the delta between the local database and the YouTube channel, downloading only new videos in seconds.

### 2. 🧠 Local AI Intent Normalizer (Ollama)
* Users can query the database in broken or casual English (e.g., *"when market takes equal highs then reversal?"*).
* A local `llama3.1:8b` model intercepts the query and translates it into strict ICT jargon (e.g., *"Liquidity Sweep of Relative Equal Highs (EQH) leading to Market Structure Shift (MSS)"*).
* **Escape Hatch:** Automatically detects and rejects non-trading conversational queries.

### 3. 🗄️ Context-Enriched Vector Database (Qdrant)
* Transcripts are cleaned of YouTube ASR typos (e.g., "older block" ➔ "Order Block") via a custom Regex dictionary.
* Text is chunked into 30-second timestamped blocks.
* Video titles are prepended to chunks before embedding via Apple Silicon (Metal/MPS) accelerated `SentenceTransformers`, massively increasing vector search accuracy.
* Results are post-processed and sorted chronologically to prioritize the newest videos.

### 4. 🖥️ Next.js Command Center
* Dark-mode UI built with Tailwind CSS and Lucide Icons.
* Features an **Embedded YouTube Player** that dynamically syncs to the exact second (`&t=X`) of the retrieved search result without opening new browser tabs.

---

## ⚡ Quickstart

### 1. Requirements
* macOS (Apple Silicon M-Series recommended)
* Docker (Optional) / Python 3.11+
* Node.js 20+
* [Ollama](https://ollama.ai/) running locally with `llama3.1:8b`

### 2. Installation
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/apexict-engine.git
cd apexict-engine

# Setup Python Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup Next.js Frontend
cd frontend
npm install