## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

# You are now implementing the V2.5 improvements for the AI Career Agent project.

# The repository is currently at V2.0 stable with all tests passing.

Your goal is to implement a small V2.5 upgrade WITHOUT breaking any existing functionality.


## Focus only on the following improvements:

1. Add AI analysis inside the Streamlit job detail panel.

Add a button labeled "Get AI Analysis".

When clicked:
- call provider.analyze_job(title, description, candidate_profile_prompt)
- display the analysis in an expandable panel
- cache the result for that job to avoid repeated API calls

Do not make API calls automatically. The user must trigger it.


2. Implement additional job collectors:

# GreenhouseCollector
Use:
https://boards-api.greenhouse.io/v1/boards/{company}/jobs

# LeverCollector
Use:
https://api.lever.co/v0/postings/{company}

# HackerNewsHiringCollector
Use:
https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=story

Add them as optional collectors in sources.yaml.


3. Update source_loader.py to support the new collector types.


4. Add minimal tests to ensure collectors return RawJob objects.


5. Update documentation:
# NEXT_STEPS_V2.md
# SOURCE_STRATEGY.md
# FINAL_IMPLEMENTATION_REPORT.md

Mark this as V2.5 incremental upgrade.

Rules:
- Do not modify existing scoring logic
- Do not break V2 tests
- Do not introduce scraping of LinkedIn or Indeed
- Keep everything modular

## After implementation:
- Run tests
- Update documentation
- Provide a short summary of changes