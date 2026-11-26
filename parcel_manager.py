"""
parcel_manager.py

Defines the ParcelManager class. It keeps the list of all parcels,
contains the rules for adding and finding them, and saves and loads
them from a JSON file.
"""

import json
from datetime import datetime
from pathlib import Path

from parcel import Parcel, ParcelListAdapter


class ParcelManager:
    """Stores and manages every parcel in the dormitory."""

    def __init__(self, file_path: Path) -> None:
        """
        Start with an empty list of parcels.

        Parameters:
            file_path (str): Where the JSON records file is stored.
        """
        self.file_path: Path = file_path
        self.parcels: list[Parcel] = []

    # ----- Saving and loading -----

    def load_from_file(self) -> str:
        """
        Load parcels from the JSON file into self.parcels.

        - If the file does not exist yet (first run), start empty.
        - If the file is damaged, move it to a backup file so it is
          never overwritten, then start empty.

        Returns:
            str: A message describing what happened.
        """

        try:
            self.parcels = ParcelListAdapter.validate_json(self.file_path.read_bytes())

        except FileNotFoundError:
            return "No saved records found. Starting with an empty list."

        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            backup_path = self.file_path.with_name(self.file_path.name + ".backup")
            _ = self.file_path.replace(backup_path)
            return (
                "Warning: the records file was damaged and could not "
                f"be read. It was moved to {backup_path} so nothing is "
                "lost. Starting with an empty list."
            )

        return f"Loaded {len(self.parcels)} parcel(s) from file."

    def save_to_file(self) -> None:
        """
        Write every parcel to the JSON file.

        The whole list is written each time. Because the list already
        holds the records loaded at start-up, old records are kept.

        Raises:
            OSError: If the file cannot be written.
        """

        _ = self.file_path.write_bytes(
            ParcelListAdapter.dump_json(self.parcels, indent=2)
        )

    def find_by_tracking_number(self, tracking_number: str) -> Parcel | None:
        """
        Find the parcel with this exact tracking number.

        Tracking numbers are unique, so there is at most one match.

        Returns:
            Parcel or None: The matching parcel, or None if not found.
        """

        tracking_number = tracking_number.upper()
        for parcel in self.parcels:
            if parcel.tracking_number == tracking_number:
                return parcel
        return None

    def search_by_student_name(self, name: str) -> list[Parcel]:
        """
        Find all parcels whose student name contains the given text.

        The search ignores upper/lower case, so "aisha" finds "Aisha Rahman".
        One student can have many parcels, so a list is returned.

        Returns:
            list: Matching parcels (empty if nothing matches).
        """

        search_text = name.lower()
        results: list[Parcel] = []
        for parcel in self.parcels:
            if search_text in parcel.student_name.lower():
                results.append(parcel)
        return results

    def tracking_number_exists(self, tracking_number: str) -> bool:
        """
        Check whether a parcel with this tracking number is already registered.

        Returns:
            bool: True if the tracking number is already used, otherwise False.
        """

        return self.find_by_tracking_number(tracking_number) is not None

    def register_parcel(
        self,
        student_name: str,
        room_number: str,
        tracking_number: str,
        arrival_time: datetime,
    ) -> Parcel:
        """
        Create a new Parcel, add it to the list and save the file.

        Raises:
            ValueError: If the tracking number is already registered.
            OSError: If the records file cannot be saved.

        Returns:
            Parcel: The parcel that was just registered.
        """

        if self.tracking_number_exists(tracking_number):
            raise ValueError(
                f"Tracking number {tracking_number} is already registered."
            )

        new_parcel = Parcel(
            student_name=student_name,
            room_number=room_number,
            tracking_number=tracking_number,
            arrival_time=arrival_time,
        )
        self.parcels.append(new_parcel)

        self.save_to_file()
        return new_parcel

    def count_parcels(self) -> int:
        """Return how many parcels are currently registered."""

        return len(self.parcels)
