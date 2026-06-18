<div align="center">

# EleitorAI

**PT:** Plataforma de inteligência eleitoral agentica — fact-checker, detecção de narrativas e análise de debate
**EN:** Agentic electoral intelligence platform — fact-checker, narrative detection and debate analysis

<br/>

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5-4285F4?style=flat-square&logo=google)](https://aistudio.google.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-1C3C3C?style=flat-square&logo=langchain)](https://langchain-ai.github.io/langgraph/)
[![SQLite](https://img.shields.io/badge/SQLite-+--sqlite--vec-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://github.com/asg017/sqlite-vec)
[![Deploy](https://img.shields.io/badge/deploy-Fly.io-7C3AED?style=flat-square&logo=fly.io)](https://fly.io)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/simoesleandro/eleitorai?style=flat-square&color=8b5cf6)](https://github.com/simoesleandro/eleitorai/commits)
[![Issues](https://img.shields.io/github/issues/simoesleandro/eleitorai?style=flat-square&color=f59e0b)](https://github.com/simoesleandro/eleitorai/issues)
[![Tests](https://img.shields.io/badge/tests-48_passing-22c55e?style=flat-square&logo=pytest)](tests/)

<br/>

[🚀 Demo *(em breve / coming soon)*](#-demo) &nbsp;·&nbsp;
[🐛 Reportar bug](https://github.com/simoesleandro/eleitorai/issues) &nbsp;·&nbsp;
[💡 Sugerir feature](https://github.com/simoesleandro/eleitorai/issues)

</div>

---

## 📋 Índice / Table of Contents

- [📌 Sobre / About](#-sobre--about)
- [🎯 Demo](#-demo)
- [📊 Status / Status](#-status--status)
- [✨ Funcionalidades / Features](#-funcionalidades--features)
- [🛠 Stack](#-stack)
- [🚀 Instalação / Setup](#-instalação--setup)
- [🔐 Variáveis de Ambiente / Environment Variables](#-variáveis-de-ambiente--environment-variables)
- [🏗 Arquitetura / Architecture](#-arquitetura--architecture)
- [🧪 Testes / Tests](#-testes--tests)
- [🗺 Roadmap](#-roadmap)
- [👤 Autor / Author](#-autor--author)
- [📄 Licença / License](#-licença--license)

---

## 📌 Sobre / About

**PT:**
EleitorAI é uma plataforma agentica para campanhas políticas brasileiras. Três módulos integrados cobrem os três momentos críticos de uma campanha:

- **Veritas** — fact-checker contínuo de declarações de opositores com RAG sobre 5–10k checagens históricas + APIs públicas brasileiras (IBGE, TSE, Tesouro, DataSUS)
- **Eco** — detecção de narrativas emergentes e amplificação coordenada (Telegram forward chains, YouTube comment velocity)
- **Tribuno** — análise de debate em tempo real com streaming Whisper + agentes LangGraph paralelos

Construído como monolito Flask + worker APScheduler comunicando via SQLite + tabela `job_queue`. Deploy no Fly.io (região São Paulo / GRU).

**EN:**
EleitorAI is an agentic platform for Brazilian political campaigns. Three integrated modules cover the three critical moments of a campaign:

- **Veritas** — continuous fact-checker for opponent statements, with RAG over 5–10k historical fact-checks + Brazilian public APIs (IBGE, TSE, Tesouro, DataSUS)
- **Eco** — detection of emerging narratives and coordinated amplification (Telegram forward chains, YouTube comment velocity)
- **Tribuno** — real-time debate analysis with streaming Whisper + parallel LangGraph agents

Built as a Flask monolith + APScheduler worker communicating via SQLite + `job_queue` table. Deployed on Fly.io (São Paulo / GRU region).

---

## 🎯 Demo

> **PT:** Deploy em produção ainda não disponível — projeto está na **Phase 0 (Foundation)**.
> **EN:** Production deploy not yet available — the project is at **Phase 0 (Foundation)**.

🔗 **Demo ao vivo / Live demo:** *(em breve / coming soon)*

<details>
<summary>📸 Screenshots</summary>
<br/>

> *Screenshot em breve / Screenshot coming soon.*

</details>

---

## 📊 Status / Status

| Phase | Descrição / Description | Status |
|-------|------------------------|--------|
| **Phase 0** | Foundation — core, DB, schema, RAG, LLM, coletores, notifier, Flask, worker, Docker, CI | ✅ Entregue / Delivered — **48 tests passing** |
| **Phase 1** | Veritas — fact-checker agentic com 5 agentes LangGraph | 🚧 Em desenvolvimento / In progress |
| **Phase 2** | Eco — detecção de narrativas e amplificação coordenada | 🚧 Aguardando Phase 1 / Awaiting Phase 1 |
| **Phase 3** | Tribuno — análise de debate em tempo real | 🚧 Aguardando Phase 2 / Awaiting Phase 2 |

---

## ✨ Funcionalidades / Features

> **PT:** Esta entrega cobre a **Phase 0 (Foundation)** — todo o core, infraestrutura e coletores base.
> **EN:** This release covers **Phase 0 (Foundation)** — all core, infrastructure and base collectors.

### Phase 0 (entregue / delivered)

- ✅ Coleta de transcrições YouTube via `youtube-transcript-api` com dedup por hash
- ✅ Coleta de mensagens Telegram (Telethon) com captura de `forwarded_from`
- ✅ Schema SQLite unificado (17 tabelas, 5 índices, vec0 para RAG)
- ✅ RAG foundation: embeddings Gemini + `sqlite-vec` + hybrid retriever (keyword + semântico)
- ✅ Gemini client (google-genai SDK) com structured output
- ✅ Notifier Telegram (httpx + respx mock para testes)
- ✅ Flask app com dashboard base e auth bcrypt
- ✅ Worker APScheduler (CLI: `--daemon` / `--once`)
- ✅ Dockerfile, docker-compose, `fly.toml` (região `gru`)
- ✅ CI GitHub Actions (ruff + pytest)

### Phase 1 — Veritas (em desenvolvimento / in progress)

- 🚧 5 agentes LangGraph (extrator, pesquisador, verificador, redator, crítico)
- 🚧 Base de fact-checks: Lupa, Boatos, FatoFake, Checamos, Estadão Verifica, Comprova, Truco
- 🚧 6 ferramentas: RAG fact-checks, IBGE, TSE, Tesouro, DataSUS, notícias RSS
- 🚧 Guard *"≥2 fontes para classificar falso"*
- 🚧 Dossiê MD/PDF com contraposição sugerida

### Phase 2 — Eco (planejado / planned)

- 🚧 Embeddings + HDBSCAN clustering
- 🚧 NetworkX graph (Telegram forward chains, YouTube comments)
- 🚧 4 agentes (narratólogo, analista de rede, caracterizador, crítico)
- 🚧 Dashboard d3 force-directed

### Phase 3 — Tribuno (planejado / planned)

- 🚧 Stream `yt-dlp` + Whisper streaming
- 🚧 3 agentes paralelos por chunk (claims, falácias, scoring)
- 🚧 Feed SSE ao vivo + alertas Telegram
- 🚧 Relatório pós-debate MD/PDF

---

## 🛠 Stack

| Camada / Layer | Tecnologia / Technology | Justificativa / Rationale |
|----------------|-------------------------|---------------------------|
| Backend web | Python 3.12, Flask 3.x, Waitress | Alinha com `Pulso_Eleitoral` |
| Worker | APScheduler daemon | Pattern `sentinela-rj` (`--daemon`) |
| Banco de dados / Database | SQLite + `sqlite-vec` | Volume de campanha é gerenciável; volume persistente no Fly.io |
| IA / AI | Gemini 2.5 Flash/Pro (google-genai SDK) | Flash p/ sub-tarefas, Pro p/ síntese |
| Orquestração / Orchestration | LangGraph 0.2 | State machines, paralelismo, loops de crítica |
| Embeddings | Gemini embedding API | Indexação RAG |
| RAG | `sqlite-vec` + hybrid retrieval | Sem dependência de Postgres |
| Scraping | Playwright, Telethon, `yt-dlp` | Coletores de YouTube e Telegram |
| Transcrição / Transcription | Whisper, `youtube-transcript-api` | Tribuno + Veritas |
| Notificações / Notifications | Telegram Bot | Alertas do worker |
| Deploy | Fly.io (região `gru`) | `fly.toml` + `docker-compose` |
| Testes / Tests | pytest (48 testes) | Mocks de LLM nos testes |

---

## 🚀 Instalação / Setup

### Pré-requisitos / Prerequisites

- Python 3.12+
- Git
- (Opcional / Optional) Docker para deploy

### Setup local / Local setup

```bash
# Clone / Clone the repo
git clone https://github.com/simoesleandro/eleitorai.git
cd eleitorai

# Ambiente virtual / Virtual env
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # Linux/Mac

# Dependências / Dependencies
pip install -r requirements.txt

# (Opcional / Optional) Playwright browser
python -m playwright install chromium --with-deps

# Variáveis de ambiente / Environment variables
cp .env.example .env
# Edite .env com suas chaves / Edit .env with your keys

# Inicializar o banco / Initialize the database
python -c "from core.db import init_db; init_db()"

# Rodar a web / Run the web app
python -m app

# Em outro terminal: rodar o worker / In another terminal: run the worker
python -m worker --daemon
```

Acesse / Access: `http://localhost:5090/dashboard`

---

## 🔐 Variáveis de Ambiente / Environment Variables

> Lista completa em / Full list in: [`.env.example`](.env.example)

| Variável | Descrição / Description | Obrigatória / Required? |
|----------|-------------------------|-------------------------|
| `GEMINI_API_KEY` | Chave API Google Gemini (AI Studio ou Vertex AI) | Sim / Yes — para usar LLM |
| `TELEGRAM_BOT_TOKEN` | Token do Telegram Bot (BotFather) | Sim / Yes — para alertas |
| `TELEGRAM_CHAT_ID` | ID do chat/canal que recebe alertas | Sim / Yes — para alertas |
| `TELEGRAM_API_ID` | `my.telegram.org` API ID | Sim / Yes — para coletor Telegram |
| `TELEGRAM_API_HASH` | `my.telegram.org` API hash | Sim / Yes — para coletor Telegram |
| `ADMIN_PASS` | Senha do admin (bcrypt ou plain) | Sim / Yes — para auth |
| `SECRET_KEY` | Flask session secret | Sim / Yes — para auth |
| `DB_PATH` | Caminho do SQLite | Não / No — default `data/eleitorai.db` |
| `LANGFUSE_*` | Tracing opcional (Langfuse Cloud ou self-hosted) | Não / No |

---

## 🏗 Arquitetura / Architecture

```
eleitorai/
├── app/                    # Flask monolith (Waitress)
│   ├── __main__.py         # python -m app  →  porta 5090
│   ├── routes/             # auth (bcrypt) + dashboard
│   ├── static/             # CSS base
│   └── templates/          # base, login, dashboard
├── core/                   # Domínio compartilhado
│   ├── config.py           # Settings via pydantic-settings
│   ├── db.py               # SQLite + sqlite-vec + init_db
│   ├── schema.sql          # 17 tabelas, 5 índices, vec0
│   ├── modelos.py          # Pydantic: Mencao, Afirmacao, Checagem, Alerta, Job
│   ├── fila.py             # job_queue helpers (enqueue/dequeue/complete/fail)
│   ├── llm.py              # Gemini client + embedding wrapper
│   ├── notifier.py         # Telegram notifier (httpx)
│   ├── rag/                # embeddings.py + retriever.py (hybrid)
│   └── coletores/          # youtube.py + telegram.py
├── worker/                 # APScheduler daemon
│   ├── __main__.py         # python -m worker --daemon
│   └── pipeline.py         # run_once + schedule_jobs
├── tests/                  # 48 testes pytest
├── .github/workflows/      # CI: ruff + pytest
├── Dockerfile
├── docker-compose.yml
├── fly.toml                # região gru, processos web + worker
├── requirements.txt
└── .env.example
```

**Fluxo principal / Main flow:**

```
APScheduler (worker)
        ↓ enqueue
SQLite job_queue
        ↓ dequeue
pipeline.run_once()
        ↓ processa
Coletores (YouTube / Telegram)
        ↓ persiste
SQLite (mencoes, afirmacoes, checagens, embeddings)
        ↓
Notifier Telegram (alertas)
        ↓
Flask dashboard (http://localhost:5090/dashboard)
```

**Padrões de design / Design patterns:**

- **Monolito modular / Modular monolith** — Flask + worker compartilham `core/`
- **Job queue com SQLite** — `job_queue` table como fila persistente (sem Redis)
- **Shared volume no Fly.io** — `eleitorai_data` mount em `/data` para o SQLite
- **Phase 0 first, agents later** — `langgraph` instalado mas sem grafos até Phase 1

> Spec completa em / Full spec at: [`../docs/specs/2026-06-18-eleitorai-platform-design.md`](../docs/specs/2026-06-18-eleitorai-platform-design.md)

---

## 🧪 Testes / Tests

```bash
# Rodar suite completa (48 tests) / Run full suite
pytest -v

# Com cobertura / With coverage
pytest --cov=. --cov-report=term-missing

# Suites específicas / Specific suites
pytest tests/core/ -v
pytest tests/app/ -v
pytest tests/core/rag/ -v
pytest tests/core/coletores/ -v
```

> **PT:** Cobertura — 80%+ em `core/`, 70%+ em módulos. LLM mockado via `respx` e fixtures pytest.
> **EN:** Coverage — 80%+ on `core/`, 70%+ on modules. LLM is mocked via `respx` and pytest fixtures.

**48 testes** cobrindo / covering:

- `core/config`, `core/db`, `core/fila`, `core/llm`, `core/modelos`, `core/notifier`
- `core/coletores/youtube`, `core/coletores/telegram`
- `core/rag/embeddings`, `core/rag/retriever`
- `app/routes/auth`, `app/routes/dashboard`
- `worker/pipeline`

---

## 🗺 Roadmap

> Planos detalhados em / Detailed plans at: [`../docs/plans/`](../docs/plans/)

- [x] **Phase 0** — Foundation: core, DB, schema, RAG, LLM, coletores, notifier, Flask, worker, Docker, CI *(esta entrega / this release)*
- [ ] **Phase 1** — Veritas fact-checker (~3 semanas / weeks)
- [ ] **Phase 2** — Eco detecção de narrativas (~3 semanas / weeks)
- [ ] **Phase 3** — Tribuno análise de debate (~4 semanas / weeks)
- [ ] **Deploy Fly.io produção** com secrets reais / with real secrets
- [ ] **Demo vídeo** de cada módulo / of each module
- [ ] **A/B Gemini vs Gemma 4 local** (opcional / optional)

---

## 👤 Autor / Author

<div align="center">

**Leandro Simões**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/leandro-sim%C3%B5es-7a0b3537b)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/simoesleandro)
[![Portfolio](https://img.shields.io/badge/Portfolio-06b6d4?style=flat-square&logo=safari&logoColor=white)](https://simoesleandro.github.io/portfolio)

*Fullstack · IA Aplicada · Civic Tech · Direito*

*17 anos de gestão + Direito + IA agentica. Esta plataforma é parte do portfólio de especialização eleitoral híbrida.*

</div>

---

## 📄 Licença / License

**PT:** MIT — ver [`LICENSE`](LICENSE). *(Arquivo a ser criado em task futura / File to be added in a future task.)*
**EN:** MIT — see [`LICENSE`](LICENSE). *(File to be added in a future task.)*

---

<div align="center">

Feito com ☕ e IA em / Made with ☕ and AI in 🇧🇷 Rio de Janeiro

</div>
