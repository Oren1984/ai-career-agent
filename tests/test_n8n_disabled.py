# tests/test_n8n_disabled.py
# This file is part of the OpenLLM project issue tracker:

"""
Tests for the n8n integration layer — verifies that n8n is NOT activated
and that the automation directory structure is correct.
"""
import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent
_N8N_DIR = _REPO_ROOT / "automation" / "n8n"
_BRIDGE_DIR = _REPO_ROOT / "automation" / "bridge"


class TestN8nDisabled:
    """n8n is not activated — verify structure exists without activating it."""

    def test_n8n_directory_exists(self):
        assert _N8N_DIR.exists()

    def test_docker_compose_file_exists(self):
        dc_file = _N8N_DIR / "docker-compose.n8n.yml"
        assert dc_file.exists()

    def test_docker_compose_not_in_main_compose(self):
        """The n8n docker-compose must be separate from the main docker-compose.yml."""
        main_compose = _REPO_ROOT / "docker-compose.yml"
        if main_compose.exists():
            content = main_compose.read_text()
            assert "n8n" not in content.lower(), (
                "n8n service should NOT be in the main docker-compose.yml"
            )

    def test_workflows_directory_exists(self):
        assert (_N8N_DIR / "workflows").exists()

    def test_example_workflow_exists(self):
        wf = _N8N_DIR / "workflows" / "example_job_notification.json"
        assert wf.exists()

    def test_example_workflow_is_valid_json(self):
        wf = _N8N_DIR / "workflows" / "example_job_notification.json"
        data = json.loads(wf.read_text())
        assert isinstance(data, dict)

    def test_example_workflow_has_name(self):
        wf = _N8N_DIR / "workflows" / "example_job_notification.json"
        data = json.loads(wf.read_text())
        assert "name" in data

    def test_readme_exists(self):
        readme = _N8N_DIR / "README_FUTURE_N8N.md"
        assert readme.exists()


class TestBridgeContract:
    def test_bridge_directory_exists(self):
        assert _BRIDGE_DIR.exists()

    def test_webhook_contract_exists(self):
        assert (_BRIDGE_DIR / "webhook_contract.md").exists()

    def test_sample_payloads_exists(self):
        assert (_BRIDGE_DIR / "sample_payloads.json").exists()

    def test_sample_payloads_is_valid_json(self):
        data = json.loads((_BRIDGE_DIR / "sample_payloads.json").read_text())
        assert "examples" in data
        assert len(data["examples"]) > 0

    def test_sample_payload_has_required_fields(self):
        data = json.loads((_BRIDGE_DIR / "sample_payloads.json").read_text())
        example = data["examples"][0]["payload"]
        assert "event" in example
        assert "job" in example
        assert example["event"] == "new_high_match_job"

    def test_job_payload_has_score_fields(self):
        data = json.loads((_BRIDGE_DIR / "sample_payloads.json").read_text())
        job = data["examples"][0]["payload"]["job"]
        assert "match_score" in job
        assert "match_level" in job
        assert "title" in job
        assert "url" in job
