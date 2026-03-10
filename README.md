# AI Career Agent

AI-assisted job hunting system designed to help discover and analyze job opportunities automatically.

The system collects job listings from multiple sources, analyzes job descriptions, and scores how well they match a candidate profile.

This project focuses on **decision support**, not automatic applications.

The user remains in control of the final decision to apply.

---

## Features (Version 1)

- Job collection from selected sources
- Job description parsing
- Profile-based filtering
- Match scoring engine
- Explanation of match results
- Streamlit dashboard
- Manual tracking of job status

---

## Planned Future Features

- LLM-based job analysis
- Resume adaptation
- Cover letter generation
- Browser automation for applications
- Multi-agent architecture

---

## Tech Stack

- Python
- Streamlit
- SQLite
- Docker
- BeautifulSoup
- FastAPI (optional layer)

---

## Architecture
Sources → Collector → Database → Filter → Match Engine → Dashboard


---

## Important Design Principle

This system **does not automatically send job applications**.

The agent suggests opportunities and explains why they match the user's profile.

---

## Run
docker compose up

- Dashboard will be available on:

http://localhost:8501


---