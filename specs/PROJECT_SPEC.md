# Project Specification

Project Name: AI Career Agent

Goal:
Create a lightweight autonomous job discovery assistant that collects job listings and evaluates them against a candidate profile.

The system should help identify relevant job opportunities and present them through a dashboard.

---

# Core Principles

1. No automatic job applications
2. Modular architecture
3. Easy extension for LLM support
4. Lightweight local execution
5. Docker-based deployment

---

# Core Components

## 1 Job Collector

Collect jobs from sources such as:

- company career pages
- RSS feeds
- simple job boards

Data collected:

- job_title
- company
- location
- job_description
- url
- date_found

---

## 2 Job Normalization

Standardize job records.

Remove duplicates using a hash of:

job_title + company + description

---

## 3 Filter Engine

Filter jobs using profile rules.

Example filters:

Positive keywords:

- AI
- ML
- Python
- FastAPI
- MLOps
- Docker
- AWS
- Terraform

Negative keywords:

- Senior
- PhD
- 10+ years
- relocation

---

## 4 Match Engine

Compute match score.

Example scoring:

Python → +2  
AI / ML → +3  
Docker → +2  
AWS → +2  
LLM → +3  
Senior → −2  
PhD → −3

Output:

- match_score
- explanation
- matched_keywords
- missing_keywords

---

## 5 Dashboard

Streamlit interface.

Display:

- job list
- match score
- explanation
- filters

Status options:

- new
- saved
- ignored
- applied_manual

---

## 6 Database

SQLite database.

Tables:

jobs  
scores  
status

---

# Non Goals

The following are intentionally excluded in Version 1:

- automatic application submission
- browser automation
- complex RAG pipelines
- multi-agent orchestration

---

# Future Extension

The architecture must allow easy addition of:

LLM providers:

- OpenAI
- Gemini
- Claude

through a provider interface.