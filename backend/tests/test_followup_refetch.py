from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app import main
from app.schemas import ReportFollowup


class DummyRequest:
    base_url = "http://testserver/"


def _make_report(report_id):
    return SimpleNamespace(
        id=report_id,
        report_images=[],
        clarification=None,
        description="Initial description",
        latitude=40.0,
        longitude=-70.0,
        thread_id="thread-1",
        category=None,
    )


@pytest.mark.asyncio
async def test_followup_refetches_report_when_ai_result_empty(monkeypatch):
    report_id = uuid4()
    initial_report = _make_report(report_id)
    fresh_report = SimpleNamespace(id=report_id)
    reports = [initial_report, fresh_report]

    def get_report_stub(db, report_id):
        return reports.pop(0) if reports else None

    def get_similar_reports_count_stub(
        db, category, latitude, longitude, exclude_report_id=None, **kwargs
    ):
        return 0

    monkeypatch.setattr(main.crud, "get_report", get_report_stub)
    monkeypatch.setattr(
        main.crud, "get_similar_reports_count", get_similar_reports_count_stub
    )
    monkeypatch.setattr(main, "reverse_geocode", lambda lat, lon: "addr")
    monkeypatch.setattr(main, "ai_followup", lambda **kwargs: None)
    update_spy = MagicMock()
    monkeypatch.setattr(main.crud, "update_report_with_ai_response", update_spy)

    transformed = object()

    def transform_stub(report, base_url):
        assert report is fresh_report
        return transformed

    monkeypatch.setattr(main, "transform_to_response", transform_stub)

    result = await main.make_followup(
        DummyRequest(),
        report_id,
        ReportFollowup(followup={}),
        db=MagicMock(),
    )

    assert result is transformed
    update_spy.assert_not_called()


@pytest.mark.asyncio
async def test_followup_refetches_missing_report_raises(monkeypatch):
    report_id = uuid4()
    initial_report = _make_report(report_id)
    calls = {"count": 0}

    def get_report_stub(db, report_id):
        calls["count"] += 1
        return initial_report if calls["count"] == 1 else None

    def get_similar_reports_count_stub(
        db, category, latitude, longitude, exclude_report_id=None, **kwargs
    ):
        return 0

    monkeypatch.setattr(main.crud, "get_report", get_report_stub)
    monkeypatch.setattr(
        main.crud, "get_similar_reports_count", get_similar_reports_count_stub
    )
    monkeypatch.setattr(main, "reverse_geocode", lambda lat, lon: "addr")
    monkeypatch.setattr(main, "ai_followup", lambda **kwargs: None)

    with pytest.raises(HTTPException) as exc_info:
        await main.make_followup(
            DummyRequest(),
            report_id,
            ReportFollowup(followup={}),
            db=MagicMock(),
        )

    assert exc_info.value.status_code == 404
