from unittest.mock import Mock, patch

import pytest

from ingestion.src.ingestion.submitter import ProcessSubmitter


@pytest.fixture
def submitter():
    return ProcessSubmitter(base_url="http://api:8000")

@patch("shared.celery_client.app.send_task")
def test_launch_scraper(mock_send_task, submitter):
    payload = {"key": "value"}

    # Mock the Celery task id
    mock_task = Mock()
    mock_task.id = "test_task_id"
    mock_send_task.return_value = mock_task

    # Call the function
    task_id = submitter.launch_scraper(payload)

    # Assertions
    mock_send_task.assert_called_once_with("scraper.run_pipeline", args=[payload])
    assert task_id == "test_task_id"
