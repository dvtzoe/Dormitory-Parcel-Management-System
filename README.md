Dormitory Parcel Management System
A terminal-based Python program that helps dormitory staff keep track of parcels that arrive for students. Staff can register incoming parcels and look them up by student name or tracking number. Every record is saved to a JSON file, so nothing is lost when the program closes.

Author: Rawi Luxsuwong and Natpakan Tabudda

Project status — Stage 3. Parcel registration, searching, and JSON saving/loading are done. Recording pickups and calculating overdue storage fees are planned for the next stages (see Roadmap).

Features
Menu option	What it does
1. Register Incoming Parcel	Records the student's name, room number, tracking number and arrival time. New parcels start with the status Waiting for pickup. The record is saved to the file straight away.
2. Search Parcel by Student Name	Lists every parcel for a student. The search ignores upper/lower case and matches part of a name, so aisha finds Aisha Rahman.
3. Search Parcel by Tracking Number	Finds the one parcel with that tracking number. Lowercase input works too.
4. Save and Exit	Saves all records to parcels.json and closes the program.
Room numbers and tracking numbers are stored in uppercase, so b204 and B204 are treated as the same value.

Requirements
Python 3.12 or newer (set in pyproject.toml).
The program needs no extra packages. It only uses Python's built-in json, datetime, pathlib and typing modules.
Optional: uv to manage the environment and the dev tools (pytest, ruff).
How to run
In a terminal
python3 main.py
On Windows, use python main.py.

With uv
uv run main.py
In VS Code
Install Python from python.org, and install the Python extension in VS Code.
Choose File → Open Folder… and open the project folder.
Open main.py and click the ▶ Run button in the top-right corner.
Entering dates
When asked for the arrival time, type it as YYYY-MM-DD HH:MM, for example 2026-11-26 14:30, or press Enter to use the current date and time.

Example session
No saved records found. Starting with an empty list.

===== Dormitory Parcel Management System =====
1. Register Incoming Parcel
2. Search Parcel by Student Name
3. Search Parcel by Tracking Number
4. Save and Exit
Choose an option (1-4): 1

--- Register Incoming Parcel ---
Student name: Aisha Rahman
Room number: b204
Tracking number: trk123
Arrival time (YYYY-MM-DD HH:MM), or press Enter for now: 2026-11-20 09:15

Parcel registered and saved successfully!
----------------------------------------
Student name    : Aisha Rahman
Room number     : B204
Tracking number : TRK123
Arrival time    : 2026-11-20 09:15
Status          : Waiting for pickup
----------------------------------------
Total parcels registered: 1
Project structure
Dormitory-Parcel-Management-System/
├── main.py            # Terminal menu: asks for input and shows results
├── parcel.py          # Parcel class, ParcelDict type and date/status constants
├── parcel_manager.py  # ParcelManager class: parcel list, rules, JSON saving/loading
├── parcels.json       # Saved records (created automatically on first save)
├── parcel.json        # Example record showing the data format
├── tests/             # pytest tests for each module
├── pyproject.toml     # Project metadata, dev dependencies and pytest settings
├── uv.lock            # Locked dev dependency versions for uv
└── README.md          # This file
How the files work together
main.py is the only file that talks to the user (input() and print()). It checks the input, then asks the ParcelManager to do the work. The data file path is Path(__file__).parent / "parcels.json", so the program finds its records even when started from a different folder.
parcel_manager.py holds the list of all parcels and enforces the rules, such as no duplicate tracking numbers. It saves to the JSON file every time a parcel is registered.
parcel.py describes a single parcel. It can print itself (display()), convert itself to a dictionary for JSON (to_dict()), and be rebuilt from one (parcel_from_dict()).
Design choices
Classes: Parcel groups the data for one parcel. ParcelManager keeps every rule and all of the saving logic in one place, so main.py stays simple.
List: all parcels are stored in a list, because the number of parcels keeps growing and the searches loop through them.
Dictionaries: each parcel is converted to a dictionary before saving, because JSON objects and Python dictionaries have the same key/value shape.
JSON: a simple, readable text format supported by Python's built-in json module.
datetime: used for arrival times, and stored in the file as ISO 8601 text (e.g. 2026-11-20T09:15:00), because JSON cannot store dates directly.
pathlib.Path: used for the file location and for building the backup file name.
Type hints: every function has type hints, and ParcelDict (a TypedDict) describes the exact shape of a saved record.
Data file (parcels.json)
The file holds a list of parcels. Each parcel is saved like this:

{
    "student_name": "Aisha Rahman",
    "room_number": "B204",
    "tracking_number": "TRK123",
    "arrival_time": "2026-11-20T09:15:00",
    "status": "Waiting for pickup"
}
Error handling
Empty input is rejected and the question is asked again.
Invalid dates and arrival times in the future are rejected with a message.
Invalid menu choices show a message and the menu appears again.
Duplicate tracking numbers are blocked, regardless of upper/lower case.
Missing file: on the first run the program simply starts with no records.
Damaged file: if parcels.json cannot be read, it is renamed to parcels.json.backup so the old data is never overwritten, and the program starts with no records.
Save errors: if the file cannot be written, a warning is shown. When this happens on Save and Exit, the program stays open so the records in memory are not lost.
Development
Install the dev tools:

uv sync
Format and lint the code with ruff:

uv run ruff format .
uv run ruff check .
Testing
Automated tests
The tests/ folder holds pytest tests for every module:

File	What it checks
tests/test_parcel.py	Creating a parcel, to_dict() / parcel_from_dict() round trips, bad or missing fields, and display() output.
tests/test_parcel_manager.py	Registering, duplicate tracking numbers (any case), searching by name and tracking number, saving, reloading after a restart, damaged files being moved to a backup, and save errors.
tests/test_main.py	Input helpers (empty input, invalid and future dates, Enter for now), each menu action, a full session followed by a restart, and the program staying open when saving fails.
The tests use a temporary folder, so they never touch your real parcels.json. User input is simulated by replacing input() with prepared answers.

Run them with:

uv run pytest
Or, without uv (after pip install pytest):

python3 -m pytest
Manual testing
Each stage was also tested by hand before the next one was started:

Registration: valid input, empty fields, invalid and future dates, and duplicate tracking numbers.
Searching: full name, part of a name in a different case, lowercase tracking numbers, and no results.
JSON: records stayed available after restarting the program (including from a different folder), and missing or damaged files were handled.
Roadmap
Planned for the next stages:

Record Parcel Pickup: mark a parcel as Collected and save the pickup time.
View Parcel Collection Information: show parcels still waiting and parcels already collected.
Calculate Overdue Storage Fee: for example, the first 3 days free, then a fee for each full day after that.
Tests for the pickup and fee features once they are added.
Possible later improvements:

Let staff edit or delete a parcel that was entered by mistake.
Record whether an overdue fee has been paid.
Send an email notification to the student when a parcel arrives.
