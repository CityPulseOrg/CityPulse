from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from app import crud


@pytest.mark.parametrize(
    ("initial_status", "expected_status"),
    [
        ("Waiting for user follow-up", "New"),
        ("", "New"),
        (None, "New"),
    ],
)
def test_update_report_with_ai_response_sets_new_for_waiting_or_blank(
    monkeypatch, initial_status, expected_status
):
    report = SimpleNamespace(status=initial_status)
    monkeypatch.setattr(crud, "get_report", lambda db, report_id: report)
    db = MagicMock()

    crud.update_report_with_ai_response(
        db=db,
        report_id=uuid4(),
        ai_response={"needs_clarification": False},
    )

    assert report.status == expected_status


def test_update_report_with_ai_response_preserves_status_when_not_waiting(monkeypatch):
    report = SimpleNamespace(status="In Progress")
    monkeypatch.setattr(crud, "get_report", lambda db, report_id: report)
    db = MagicMock()

    crud.update_report_with_ai_response(
        db=db,
        report_id=uuid4(),
        ai_response={"needs_clarification": False},
    )

    assert report.status == "In Progress"


def test_update_report_with_ai_response_sets_waiting_when_needed(monkeypatch):
    report = SimpleNamespace(status="Resolved")
    monkeypatch.setattr(crud, "get_report", lambda db, report_id: report)
    db = MagicMock()

    crud.update_report_with_ai_response(
        db=db,
        report_id=uuid4(),
        ai_response={"needs_clarification": True},
    )

    assert report.status == "Waiting for user follow-up"
