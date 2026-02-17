# Data Titan OS  
### Institutional-Grade Market Data & Analytics Platform

---

## Executive Summary

**Data Titan OS** is an end-to-end, event-driven market data analytics platform designed to transform raw, unreliable financial data into validated, reproducible, and decision-ready intelligence.

The system is built with **institutional engineering standards**, emphasizing:

- deterministic pipeline execution  
- strict data contracts and validation  
- event-driven orchestration  
- full auditability  
- end-to-end reproducibility  

This repository demonstrates how a modern buy-side analytics platform can be designed **from first principles** — from raw data ingestion to backtested performance — in a way that mirrors real hedge-fund and financial-institution architectures.

---

## What This Project Does (Plain English)

This project simulates how an institutional data team processes market data.

When run, the system automatically:

1. Pulls **real market data** (equities and macroeconomic indicators)
2. Stores immutable **raw (Bronze)** data
3. Cleans and validates data into a **trusted (Silver)** layer
4. Computes financial **features** (returns, volatility, Sharpe, CAGR)
5. Generates **BUY / SELL / HOLD** trading signals
6. Backtests the strategy with transaction costs
7. Outputs **performance metrics and trade history**

Everything runs **end-to-end with a single command**.

---

## Problem Statement

Financial market data is noisy, delayed, and often unreliable.  
In practice, most analytical failures do **not** originate in modeling, but upstream:

- silent data corruption  
- undocumented assumptions  
- inconsistent feature logic  
- non-reproducible pipelines  
- time-triggered jobs running on incomplete data  

**The core problem this system addresses is:**

> *How do we convert chaotic, multi-domain market data into trusted, auditable, and action-ready intelligence — without sacrificing reproducibility or operational rigor?*

---

## Design Principles

The platform is governed by the following non-negotiable principles:

### 1. Event-Driven Over Time-Driven  
Pipelines advance based on **data readiness**, not blind schedules.  
Each stage emits explicit lifecycle events.

### 2. Domain Isolation  
Each data domain (Equities, Macro, Sentiment) owns its ingestion logic.  
Cross-domain dependencies are enforced downstream.

### 3. Immutable Raw Data  
Raw data is never modified after ingestion.  
All assumptions and corrections occur in later layers.

### 4. Validation Before Intelligence  
No feature, signal, or metric is produced unless upstream data passes strict validation.

### 5. Reproducibility by Construction  
Every run is deterministic, logged, and traceable.  
Identical inputs always produce identical outputs.

---

## Architecture Overview

The system follows a **data-mesh inspired medallion architecture**:

Bronze (Raw Data)
↓
Silver (Validated Data)
↓
Features (Analytics)
↓
Signals (Decisions)
↓
Gold (Backtest Results)


Each stage:
- consumes only validated upstream artifacts
- emits lifecycle events
- produces auditable outputs

---

## Data Domains

Currently implemented domains:

- **Equities** — Yahoo Finance (price data)
- **Macro** — Federal Reserve Economic Data (FRED)

The architecture is designed to support additional domains (e.g. Sentiment) without refactoring core logic.

---

## Pipeline Stages

### 1. Ingestion — Bronze Layer
- Pulls raw data from external APIs
- Stores immutable CSVs by domain and date
- Emits `DATA_INGESTED` events

### 2. Validation — Silver Layer
- Explicit type coercion
- Strict Pandera schemas
- Invalid rows dropped with logging
- Writes Parquet
- Emits `DATA_VALIDATED` events

### 3. Feature Factory
- Deterministic feature computation
- Rolling returns, volatility, Sharpe, CAGR
- Volatility regime classification
- Emits `FEATURES_READY` events

### 4. Signal Engine
- Explainable rule-based strategy
- BUY / SELL / HOLD signals
- Emits `SIGNALS_READY` events

### 5. Backtesting — Gold Layer
- Transaction cost modeling
- Trade ledger & equity curve
- Performance metrics (CAGR, Sharpe, Max Drawdown)
- Emits `BACKTEST_COMPLETE` event

---

## Repository Structure

data-titan-os/
│
├── src/ # Core system logic
│ ├── ingestion/ # Domain-specific ingestion
│ ├── silver/ # Validation & cleaning
│ ├── features/ # Feature engineering
│ ├── signals/ # Trading logic
│ ├── backtest/ # Simulation & metrics
│ ├── event_bus/ # Event dispatching
│ └── pipeline/ # Pipeline entrypoints
│
├── data/ # Generated artifacts (gitignored)
│ ├── bronze/
│ ├── silver/
│ ├── features/
│ ├── signals/
│ └── gold/
│
├── metadata/ # Run logs & audit trail (gitignored)
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore


---

## How to Run the Demo

### Prerequisites
- Docker
- Docker Compose

### Run the Full Pipeline

```bash
docker compose up --build


What You Will See

Logs for each pipeline stage

Lifecycle events emitted at every boundary

Final backtest metrics printed to stdout

Where Results Are Stored

data/bronze/ → raw data from APIs

data/silver/ → validated, trusted data

data/features/ → analytics-ready features

data/signals/ → trading decisions

data/gold/ → backtest results & metrics

Technology Stack

Python 3.10

Pandas / NumPy

Pandera (data contracts & validation)

Parquet / PyArrow

Docker & Docker Compose

GitHub Actions (CI-ready)

Intended Audience

This repository is written for:

data engineers

quantitative analysts

analytics engineers

technical leadership

It assumes familiarity with:

Python

data pipelines

market data concepts

production-grade engineering standards

This is not a tutorial repository.