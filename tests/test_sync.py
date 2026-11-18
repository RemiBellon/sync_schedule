"""Tests for the download of several schedules and their merge into one calendar."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from icalendar import Calendar

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "schedule_sync"))

import fetcher
import main
from calendar_generator import create_ics
from parser import parse_schedule


def _fake_response(status_code: int, content: bytes = b"ods-content") -> MagicMock:
    """
    Build a fake ``requests`` response.

    Parameters
    ----------
    status_code : int
        HTTP status code returned by the fake server.
    content : bytes, optional
        Body of the response.

    Returns
    -------
    MagicMock
        Object mimicking ``requests.Response``.
    """
    response = MagicMock()
    response.status_code = status_code
    response.iter_content.return_value = [content]
    return response


def _write_ods(path: Path, rows: list[dict[str, str]]) -> None:
    """
    Write a .ods file with the same layout as the real schedules (headers on line 2).

    Parameters
    ----------
    path : Path
        Destination file.
    rows : list of dict
        One dict per day with the morning and afternoon columns.
    """
    columns = ["Date", "Time", "Course", "Where", "Who", "Time", "Course", "Where", "Who"]
    body = [
        [r["date"], r["t1"], r["c1"], r["w1"], r["p1"], r["t2"], r["c2"], r["w2"], r["p2"]]
        for r in rows
    ]
    df = pd.DataFrame([["Title"] + [""] * 8, columns, *body])
    df.to_excel(path, engine="odf", header=False, index=False)


def test_schedule_files_contains_core_and_electives() -> None:
    remote = list(fetcher.SCHEDULE_FILES)
    assert "Schedule/Schedule_PPF_2026_Core.ods" in remote
    assert "Schedule/Schedule_PPF_2026_Electives.ods" in remote
    # The previous local file name is kept
    assert fetcher.SCHEDULE_FILES["Schedule/Schedule_PPF_2026_Core.ods"] == "current_schedule.ods"
    # Two remote files must never overwrite the same local file
    assert len(set(fetcher.SCHEDULE_FILES.values())) == len(fetcher.SCHEDULE_FILES)


def test_download_schedule_downloads_every_file(tmp_path, monkeypatch) -> None:
    get = MagicMock(return_value=_fake_response(200))
    monkeypatch.setattr(fetcher.requests, "get", get)

    paths = fetcher.download_schedule(str(tmp_path))

    assert [Path(p).name for p in paths] == list(fetcher.SCHEDULE_FILES.values())
    assert all(Path(p).read_bytes() == b"ods-content" for p in paths)
    called_urls = [c.args[0] for c in get.call_args_list]
    assert called_urls == [
        f"{fetcher.BASE_URL}/public.php/webdav/{remote}" for remote in fetcher.SCHEDULE_FILES
    ]


def test_download_schedule_fails_if_one_file_is_missing(tmp_path, monkeypatch) -> None:
    get = MagicMock(side_effect=[_fake_response(200), _fake_response(404)])
    monkeypatch.setattr(fetcher.requests, "get", get)

    with pytest.raises(RuntimeError, match="404"):
        fetcher.download_schedule(str(tmp_path))


def test_main_merges_both_schedules_in_one_calendar(tmp_path, monkeypatch) -> None:
    core = tmp_path / "data" / "current_schedule.ods"
    electives = tmp_path / "data" / "current_schedule_electives.ods"
    core.parent.mkdir()
    _write_ods(core, [{
        "date": "2026-09-02", "t1": "09:00-12:15", "c1": "Plasma physics", "w1": "Room A",
        "p1": "Dupont", "t2": "14:00-17:15", "c2": "Fluid mechanics", "w2": "Room B", "p2": "Martin",
    }])
    _write_ods(electives, [{
        "date": "2027-01-15", "t1": "09:00-12:15", "c1": "Fusion", "w1": "Room C",
        "p1": "Durand", "t2": "", "c2": "", "w2": "", "p2": "",
    }])

    monkeypatch.setattr(main, "download_schedule", lambda _: [str(core), str(electives)])
    monkeypatch.setattr(main, "__file__", str(tmp_path / "src" / "schedule_sync" / "main.py"))

    main.main()

    cal = Calendar.from_ical((tmp_path / "data" / "planning_promo.ics").read_bytes())
    summaries = sorted(str(e["summary"]) for e in cal.walk("VEVENT"))
    assert summaries == ["Fluid mechanics (Martin)", "Fusion (Durand)", "Plasma physics (Dupont)"]


def test_parse_and_create_ics_on_generated_file(tmp_path) -> None:
    ods = tmp_path / "s.ods"
    _write_ods(ods, [{
        "date": "2027-01-15", "t1": "09:00-12:15", "c1": "Fusion", "w1": "Room C",
        "p1": "Durand", "t2": "", "c2": "", "w2": "", "p2": "",
    }])
    events = parse_schedule(str(ods))
    assert len(events) == 1

    ics = tmp_path / "out.ics"
    create_ics(events, str(ics))
    assert "Fusion (Durand)" in ics.read_text()
