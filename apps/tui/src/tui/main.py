"""
main.py

Starting point of the Dormitory Parcel Management System.
It shows the terminal menu and asks the user for input.

Stage 3: registration, searching and JSON saving/loading are working.
"""

from datetime import datetime
from pathlib import Path
from typing import override

from parcel.parcel import DATE_FORMAT
from parcel.parcel_manager import ParcelManager
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.types import CSSPathType

DATA_FILE = Path(__file__).parent / "parcels.json"


def get_non_empty_input(prompt: str) -> str:
    """Ask the user for text and keep asking until something is typed."""

    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_arrival_time() -> datetime:
    """
    Ask the user for the parcel's arrival date and time.

    Pressing Enter uses the current date and time. Otherwise the user
    must type a date in the format YYYY-MM-DD HH:MM.

    Returns:
        datetime: The arrival date and time.
    """

    while True:
        text = input(
            "Arrival time (YYYY-MM-DD HH:MM), or press Enter for now: "
        ).strip()

        if text == "":
            return datetime.now()

        try:
            arrival_time = datetime.strptime(text, DATE_FORMAT)
        except ValueError:
            print("Invalid date/time. Example of a valid value: 2026-11-26 14:30")
            continue

        if arrival_time > datetime.now():
            print("The arrival time cannot be in the future.")
            continue

        return arrival_time


def register_parcel_menu(manager: ParcelManager) -> None:
    """Collect parcel details from the user and register the parcel."""

    print("\n--- Register Incoming Parcel ---")
    student_name = get_non_empty_input("Student name: ")
    room_number = get_non_empty_input("Room number: ").upper()
    tracking_number = get_non_empty_input("Tracking number: ").upper()
    arrival_time = get_arrival_time()

    try:
        parcel = manager.register_parcel(
            student_name, room_number, tracking_number, arrival_time
        )
    except ValueError as error:
        print(f"Registration failed: {error}")
        return
    except OSError as error:
        print(
            f"Warning: the parcel was registered but could not be saved to the file: {error}"
        )
        return

    print("\nParcel registered and saved successfully!")
    print(parcel)
    print(f"Total parcels registered: {manager.count_parcels()}")


def search_by_name_menu(manager: ParcelManager) -> None:
    """Ask for a student name and show every matching parcel."""

    print("\n--- Search Parcel by Student Name ---")
    name = get_non_empty_input("Enter student name (full or part): ")
    results = manager.search_by_student_name(name)

    if len(results) == 0:
        print(f"No parcels found for '{name}'.")
        return

    print(f"\nFound {len(results)} parcel(s):")
    print(*results)


def search_by_tracking_menu(manager: ParcelManager) -> None:
    """Ask for a tracking number and show the matching parcel."""

    print("\n--- Search Parcel by Tracking Number ---")
    tracking_number = get_non_empty_input("Enter tracking number: ")
    parcel = manager.find_by_tracking_number(tracking_number)

    if parcel is None:
        print(f"No parcel found with tracking number '{tracking_number.upper()}'.")
        return

    print("\nParcel found:")
    print(parcel)


def show_menu() -> None:
    """Print the main menu options."""

    print("\n===== Dormitory Parcel Management System =====")
    print("1. Register Incoming Parcel")
    print("2. Search Parcel by Student Name")
    print("3. Search Parcel by Tracking Number")
    print("4. Save and Exit")


class TuiApp(App[None]):
    def __init__(
        self,
        driver_class: type[Driver] | None = None,
        css_path: CSSPathType | None = None,
        watch_css: bool = False,
        ansi_color: bool | None = None,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

    @override
    def compose(self) -> ComposeResult:
        return super().compose()


def main() -> None:
    """Run the main menu loop until the user chooses to exit."""

    TuiApp().run()

    # manager = ParcelManager(DATA_FILE)
    # print(manager.load_from_file())
    #
    # while True:
    #     show_menu()
    #     choice = input("Choose an option (1-4): ").strip()
    #
    #     if choice == "1":
    #         register_parcel_menu(manager)
    #     elif choice == "2":
    #         search_by_name_menu(manager)
    #     elif choice == "3":
    #         search_by_tracking_menu(manager)
    #     elif choice == "4":
    #         try:
    #             manager.save_to_file()
    #         except OSError as error:
    #             # Stay in the menu so the records in memory are not lost.
    #             print(f"Error: could not save records: {error}")
    #             continue
    #         print(
    #             f"Saved {manager.count_parcels()} parcel(s) to parcels.json. Goodbye!"
    #         )
    #         break
    #     else:
    #         print("Invalid choice. Please enter a number from 1 to 4.")


if __name__ == "__main__":
    main()
