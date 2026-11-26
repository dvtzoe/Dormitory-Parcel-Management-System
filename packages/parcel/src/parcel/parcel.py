"""
parcel.py

Defines the Parcel class. One Parcel object represents one parcel
that has arrived at the dormitory parcel room.
"""

import textwrap
from datetime import datetime
from typing import override

from pydantic import BaseModel, TypeAdapter

# The format used to show dates and times, for example "2026-11-26 14:30".
# %Y = year, %m = month, %d = day, %H = hour (24h), %M = minute.
DATE_FORMAT: str = "%Y-%m-%d %H:%M"

# The status every new parcel starts with.
STATUS_WAITING: str = "Waiting for pickup"


class Parcel(BaseModel):
    """Represents a single parcel stored at the dormitory."""

    student_name: str
    room_number: str
    tracking_number: str
    arrival_time: datetime
    status: str = STATUS_WAITING

    @override
    def __str__(self) -> str:
        """Print this parcel's information in a readable layout."""
        return textwrap.dedent(f"""\
            {"-" * 40}
            Student name    : {self.student_name}
            Room number     : {self.room_number}
            Tracking number : {self.tracking_number}
            Arrival time    : {self.arrival_time.strftime(DATE_FORMAT)}
            Status          : {self.status}
            {"-" * 40}
        """)


ParcelListAdapter: TypeAdapter[list[Parcel]] = TypeAdapter(list[Parcel])
