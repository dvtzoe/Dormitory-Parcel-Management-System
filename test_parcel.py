"""Tests for parcel.py: the Parcel class and parcel_from_dict()."""

from datetime import datetime

import pytest

from parcel import STATUS_WAITING, Parcel, ParcelDict, parcel_from_dict

ARRIVAL = datetime(2026, 11, 20, 9, 15)


def make_parcel() -> Parcel:
    return Parcel("Aisha Rahman", "B204", "TRK123", ARRIVAL)


def test_new_parcel_is_waiting_for_pickup() -> None:
    parcel = make_parcel()

    assert parcel.student_name == "Aisha Rahman"
    assert parcel.room_number == "B204"
    assert parcel.tracking_number == "TRK123"
    assert parcel.arrival_time == ARRIVAL
    assert parcel.status == STATUS_WAITING


def test_to_dict_stores_arrival_time_as_iso_text() -> None:
    assert make_parcel().to_dict() == {
        "student_name": "Aisha Rahman",
        "room_number": "B204",
        "tracking_number": "TRK123",
        "arrival_time": "2026-11-20T09:15:00",
        "status": STATUS_WAITING,
    }


def test_from_dict_is_the_opposite_of_to_dict() -> None:
    original = make_parcel()
    copy = parcel_from_dict(original.to_dict())

    assert copy.to_dict() == original.to_dict()
    assert copy.arrival_time == ARRIVAL


def test_from_dict_keeps_status() -> None:
    data = make_parcel().to_dict()
    data["status"] = "Collected"

    assert parcel_from_dict(data).status == "Collected"


def test_from_dict_missing_field_raises_key_error() -> None:
    data = dict(make_parcel().to_dict())
    del data["room_number"]

    with pytest.raises(KeyError):
        parcel_from_dict(data)  # pyright: ignore[reportArgumentType]


def test_from_dict_bad_date_raises_value_error() -> None:
    data: ParcelDict = make_parcel().to_dict()
    data["arrival_time"] = "not a date"

    with pytest.raises(ValueError):
        parcel_from_dict(data)


def test_display_prints_every_field(capsys: pytest.CaptureFixture[str]) -> None:
    make_parcel().display()
    output = capsys.readouterr().out

    assert "Aisha Rahman" in output
    assert "B204" in output
    assert "TRK123" in output
    assert "2026-11-20 09:15" in output
    assert STATUS_WAITING in output
