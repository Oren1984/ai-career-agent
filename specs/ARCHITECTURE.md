# Architecture

## Version 1 Goal
A lightweight, local-first, modular AI-assisted job discovery and matching system.

## Main Flow

Sources
→ Collectors
→ Normalizer
→ SQLite Database
→ Filter Engine
→ Match Engine
→ Streamlit Dashboard
→ Manual Status Tracking

## Main Modules

### Collectors
Responsible for collecting job listings from simple and reliable sources.

### Normalization
Converts collected job data into one consistent schema.

### Database
Stores jobs, scores, and status history.

### Filter Engine
Applies rules based on the candidate profile.

### Match Engine
Calculates match score and explanation.

### Dashboard
Displays jobs and allows manual status updates.

## Version 1 Boundaries

Included:
- job collection
- normalization
- deduplication
- filtering
- scoring
- dashboard
- manual tracking
- testing
- Docker support

Excluded:
- automatic applications
- browser automation for applying
- CAPTCHA solving
- paid API dependency
- advanced RAG
- multi-agent orchestration