# Test Plan

The system must include tests for:

1 Job collector

Test that jobs are correctly parsed.

2 Duplicate detection

Ensure the same job is not inserted twice.

3 Filter logic

Verify keyword filtering works.

4 Match scoring

Ensure scoring rules produce expected results.

5 Database integrity

Check records persist correctly.

6 Dashboard loading

Verify Streamlit dashboard loads without errors.

---

# Test Execution

Use pytest.

All tests must pass before release.

---

# Output

A test report summarizing:

- tests executed
- passed
- failed
- execution time