# Ingestion Contract  
**Data Titan OS — Phase 1**

---

## 1. Purpose of This Contract

This document defines the **non-negotiable rules** governing how raw data enters the Data Titan OS platform.

The ingestion layer is responsible for:
- reliably capturing external data
- preserving raw data immutability
- emitting deterministic metadata
- enabling downstream validation and orchestration

This contract exists to prevent:
- silent data corruption
- undocumented assumptions
- irreproducible downstream analytics

Any ingestion process that violates this contract is considered **invalid** and must fail explicitly.

---

## 2. Scope

This contract applies to **all data domains**, including but not limited to:

- Equities market data
- Macro-economic indicators
- Sentiment and alternative data sources

All domain-specific ingestors must conform to the same interface and behavioral guarantees.

---

## 3. Core Principles

### 3.1 Raw Data Is Immutable

- Raw data must be stored **exactly as received**
- No cleaning, correction, or enrichment is allowed at ingestion time
- If upstream data is incorrect, incomplete, or malformed, it must still be stored as-is

Any transformation logic belongs strictly to downstream layers.

---

### 3.2 Ingestion Is Not Validation

- Ingestion does **not** decide whether data is “correct”
- Ingestion only guarantees:
  - data capture
  - traceability
  - reproducibility

Validation rules are enforced in later pipeline stages.

---

### 3.3 Event Emission Is Mandatory

Every successful ingestion run must emit a standardized event indicating:
- what data arrived
- when it arrived
- where it was stored

Downstream processes rely exclusively on these events.

---

## 4. Ingestion Output Requirements

Each ingestion run **must produce two outputs**:

### 4.1 Raw Data Artifact

- Stored in the Bronze layer
- Organized by:
  - domain
  - ingestion date
- Format: CSV or JSON (domain-dependent)

Example path:
