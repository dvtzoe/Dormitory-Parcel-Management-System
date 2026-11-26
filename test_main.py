"""
Tests for main.py: the terminal menu and input helpers.

User input is simulated by replacing input() with a function that
returns the next prepared answer each time it is called.
"""

from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import main
from parcel_manager import ParcelManager


def fake_input(monkeypatch: pytest.MonkeyPatch, answers: Iterable[str]) -> None:
    """Make input() return each answer in turn."""
    remaining = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(remaining))


@pytest.fixture
def data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point main.py at a temporary records file instead of the real one."""
    path = tmp_path / "parcels.json"
    monkeypatch.setattr(main, "DATA_FILE", path)
    return path


# ----- Input helpers -----


def test_get_non_empty_input_asks_again_until_text_is_typed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_input(monkeypatch, ["", "   ", "  Aisha  "])

    assert main.get_non_empty_input("Name: ") == "Aisha"
    assert capsys.readouterr().out.count("cannot be empty") == 2


def test_get_arrival_time_accepts_valid_date(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_input(monkeypatch, ["2026-11-20 09:15"])

    assert main.get_arrival_time() == datetime(2026, 11, 20, 9, 15)


def test_get_arrival_time_enter_means_now(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_input(monkeypatch, [""])

    before = datetime.now()
    result = main.get_arrival_time()
    after = datetime.now()

    assert before <= result <= after


def test_get_arrival_time_rejects_invalid_then_future_dates(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    future = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
    fake_input(
        monkeypatch, ["yesterday", "2026-13-01 10:00", future, "2026-11-20 09:15"]
    )

    assert main.get_arrival_time() == datetime(2026, 11, 20, 9, 15)
    output = capsys.readouterr().out
    assert output.count("Invalid date/time") == 2
    assert "cannot be in the future" in output


# ----- Menu actions -----


def test_register_menu_uppercases_room_and_tracking(
    monkeypatch: pytest.MonkeyPatch, data_file: Path
) -> None:
    manager = ParcelManager(data_file)
    fake_input(monkeypatch, ["Aisha Rahman", "b204", "trk123", "2026-11-20 09:15"])

    main.register_parcel_menu(manager)

    parcel = manager.parcels[0]
    assert parcel.room_number == "B204"
    assert parcel.tracking_number == "TRK123"
    assert data_file.exists()


def test_register_menu_reports_duplicate(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_file: Path,
) -> None:
    manager = ParcelManager(data_file)
    fake_input(
        monkeypatch,
        ["Aisha", "B204", "TRK123", "2026-11-20 09:15"]
        + ["Ben", "A101", "trk123", "2026-11-20 10:00"],
    )

    main.register_parcel_menu(manager)
    main.register_parcel_menu(manager)

    assert manager.count_parcels() == 1
    assert "Registration failed" in capsys.readouterr().out


def test_search_by_name_menu(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_file: Path,
) -> None:
    manager = ParcelManager(data_file)
    _ = manager.register_parcel(
        "Aisha Rahman", "B204", "TRK123", datetime(2026, 11, 20)
    )
    fake_input(monkeypatch, ["aisha", "zoe"])

    main.search_by_name_menu(manager)
    assert "Found 1 parcel(s)" in capsys.readouterr().out

    main.search_by_name_menu(manager)
    assert "No parcels found for 'zoe'" in capsys.readouterr().out


def test_search_by_tracking_menu(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_file: Path,
) -> None:
    manager = ParcelManager(data_file)
    _ = manager.register_parcel(
        "Aisha Rahman", "B204", "TRK123", datetime(2026, 11, 20)
    )
    fake_input(monkeypatch, ["trk123", "nope"])

    main.search_by_tracking_menu(manager)
    assert "Parcel found" in capsys.readouterr().out

    main.search_by_tracking_menu(manager)
    assert "No parcel found with tracking number 'NOPE'" in capsys.readouterr().out


# ----- Whole program -----


def test_full_session_then_restart(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_file: Path,
) -> None:
    # First run: invalid choice, register a parcel, then save and exit.
    fake_input(
        monkeypatch,
        ["9", "1", "Aisha Rahman", "B204", "TRK123", "2026-11-20 09:15", "4"],
    )
    main.main()
    output = capsys.readouterr().out
    assert "No saved records found" in output
    assert "Invalid choice" in output
    assert "Saved 1 parcel(s)" in output

    # Second run: the parcel is loaded back and can be found.
    fake_input(monkeypatch, ["3", "TRK123", "4"])
    main.main()
    output = capsys.readouterr().out
    assert "Loaded 1 parcel(s) from file." in output
    assert "Aisha Rahman" in output


def test_save_error_on_exit_keeps_program_open(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    data_file: Path,
) -> None:
    calls = {"count": 0}

    def failing_save(_self: ParcelManager) -> None:
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("disk full")

    monkeypatch.setattr(ParcelManager, "save_to_file", failing_save)
    fake_input(monkeypatch, ["4", "4"])

    main.main()

    output = capsys.readouterr().out
    assert "could not save records: disk full" in output
    assert "Goodbye!" in output
    assert calls["count"] == 2
