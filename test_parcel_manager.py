"""Tests for parcel_manager.py: rules, searching and JSON saving/loading."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from parcel_manager import ParcelManager

ARRIVAL = datetime(2026, 11, 20, 9, 15)


@pytest.fixture
def data_file(tmp_path: Path) -> Path:
    """A records file path inside a temporary folder (not created yet)."""
    return tmp_path / "parcels.json"


@pytest.fixture
def manager(data_file: Path) -> ParcelManager:
    """A manager with three parcels already registered."""
    manager = ParcelManager(data_file)
    _ = manager.register_parcel("Aisha Rahman", "B204", "TRK123", ARRIVAL)
    _ = manager.register_parcel("Aisha Rahman", "B204", "TRK456", ARRIVAL)
    _ = manager.register_parcel("Ben Carter", "A101", "TRK789", ARRIVAL)
    return manager


# ----- Registering -----


def test_register_adds_parcel_and_returns_it(data_file: Path) -> None:
    manager = ParcelManager(data_file)
    parcel = manager.register_parcel("Aisha Rahman", "B204", "TRK123", ARRIVAL)

    assert manager.count_parcels() == 1
    assert manager.parcels == [parcel]
    assert parcel.tracking_number == "TRK123"


def test_register_saves_to_file_straight_away(data_file: Path) -> None:
    manager = ParcelManager(data_file)
    _ = manager.register_parcel("Aisha Rahman", "B204", "TRK123", ARRIVAL)

    saved = json.loads(data_file.read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["tracking_number"] == "TRK123"


def test_register_duplicate_tracking_number_is_blocked(
    manager: ParcelManager,
) -> None:
    with pytest.raises(ValueError, match="already registered"):
        _ = manager.register_parcel("Someone Else", "C303", "TRK123", ARRIVAL)

    assert manager.count_parcels() == 3


def test_register_duplicate_is_blocked_regardless_of_case(
    manager: ParcelManager,
) -> None:
    with pytest.raises(ValueError):
        _ = manager.register_parcel("Someone Else", "C303", "trk123", ARRIVAL)


# ----- Searching -----


def test_find_by_tracking_number(manager: ParcelManager) -> None:
    parcel = manager.find_by_tracking_number("TRK789")

    assert parcel is not None
    assert parcel.student_name == "Ben Carter"


def test_find_by_tracking_number_ignores_case(manager: ParcelManager) -> None:
    parcel = manager.find_by_tracking_number("trk789")

    assert parcel is not None
    assert parcel.tracking_number == "TRK789"


def test_find_by_tracking_number_not_found(manager: ParcelManager) -> None:
    assert manager.find_by_tracking_number("NOPE") is None


def test_tracking_number_exists(manager: ParcelManager) -> None:
    assert manager.tracking_number_exists("TRK123")
    assert not manager.tracking_number_exists("NOPE")


def test_search_by_full_name_returns_every_parcel(manager: ParcelManager) -> None:
    results = manager.search_by_student_name("Aisha Rahman")

    assert [p.tracking_number for p in results] == ["TRK123", "TRK456"]


@pytest.mark.parametrize("text", ["aisha", "RAHMAN", "sha ra"])
def test_search_by_part_of_name_ignores_case(manager: ParcelManager, text: str) -> None:
    assert len(manager.search_by_student_name(text)) == 2


def test_search_by_name_no_results(manager: ParcelManager) -> None:
    assert manager.search_by_student_name("Zoe") == []


# ----- Saving and loading -----


def test_load_with_no_file_starts_empty(data_file: Path) -> None:
    manager = ParcelManager(data_file)
    message = manager.load_from_file()

    assert "No saved records" in message
    assert manager.count_parcels() == 0


def test_records_survive_a_restart(manager: ParcelManager, data_file: Path) -> None:
    restarted = ParcelManager(data_file)
    message = restarted.load_from_file()

    assert message == "Loaded 3 parcel(s) from file."
    assert [p.to_dict() for p in restarted.parcels] == [
        p.to_dict() for p in manager.parcels
    ]


def test_loaded_records_are_kept_when_a_new_parcel_is_saved(
    manager: ParcelManager, data_file: Path
) -> None:
    restarted = ParcelManager(data_file)
    _ = restarted.load_from_file()
    _ = restarted.register_parcel("Chen Wei", "D404", "TRK999", ARRIVAL)

    saved = json.loads(data_file.read_text(encoding="utf-8"))
    assert len(saved) == 4


def test_save_to_file_writes_every_parcel(
    manager: ParcelManager, data_file: Path
) -> None:
    data_file.unlink()
    manager.save_to_file()

    saved = json.loads(data_file.read_text(encoding="utf-8"))
    assert [p["tracking_number"] for p in saved] == ["TRK123", "TRK456", "TRK789"]


@pytest.mark.parametrize(
    "content",
    [
        "{ this is not json",
        '[{"student_name": "Aisha"}]',  # missing fields -> KeyError
        (  # bad date -> ValueError
            '[{"student_name": "A", "room_number": "B", "tracking_number": "C",'
            ' "arrival_time": "bad date", "status": "Waiting for pickup"}]'
        ),
        "[1, 2, 3]",  # wrong type -> TypeError
    ],
)
def test_damaged_file_is_moved_to_backup(data_file: Path, content: str) -> None:
    _ = data_file.write_text(content, encoding="utf-8")
    manager = ParcelManager(data_file)

    message = manager.load_from_file()

    backup = data_file.with_name("parcels.json.backup")
    assert "damaged" in message
    assert manager.count_parcels() == 0
    assert not data_file.exists()
    assert backup.read_text(encoding="utf-8") == content


def test_save_error_is_raised(tmp_path: Path) -> None:
    # The parent folder does not exist, so the file cannot be written.
    manager = ParcelManager(tmp_path / "missing_folder" / "parcels.json")

    with pytest.raises(OSError):
        _ = manager.register_parcel("Aisha Rahman", "B204", "TRK123", ARRIVAL)
