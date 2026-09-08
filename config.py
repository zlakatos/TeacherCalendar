# config.py

DEFAULT_SETTINGS = {
    "modules": [
        {"name": "1. modul", "start": "2026-09-07", "end": "2026-11-01"},
        {"name": "2. modul", "start": "2026-11-02", "end": "2027-01-10"},
        {"name": "3. modul", "start": "2027-01-11", "end": "2027-02-28"},
        {"name": "4. modul", "start": "2027-03-01", "end": "2027-04-30"},
        {"name": "5. modul", "start": "2027-05-03", "end": "2027-06-25"},
    ],
    "green_start": "2026-10-19",
    "other_school_start": "2026-12-14",
    "christmas_market_date": "2026-12-21",
    "graduation_date": "2027-05-28",
    "vacations": [
        {"name": "Pedagógus nap", "start": "2026-10-05", "end": "2026-10-05"},
        {"name": "Őszi vakáció", "start": "2026-10-26", "end": "2026-11-01"},
        {"name": "Téli vakáció", "start": "2026-12-22", "end": "2027-01-10"},
        {"name": "Sízős vakáció", "start": "2027-02-22", "end": "2027-02-28"},
        {"name": "Tavaszi vakáció", "start": "2027-04-26", "end": "2027-05-04"}
    ],
    "exam_mock": {"start": "2027-03-22", "end": "2027-03-26"},
    "exam_oral": {"start": "2027-06-07", "end": "2027-06-11"},
    "exam_written": {"start": "2027-06-14", "end": "2027-06-18"},
    "classes": [
        {"name": "9C", "room": "228"},
        {"name": "9D", "room": "140"},
        {"name": "9F", "room": "148"},
        {"name": "10C", "room": "231"},
        {"name": "10D", "room": "147"},
        {"name": "10E", "room": "237"},
        {"name": "11C", "room": "42"},
        {"name": "11F", "room": "230"}
    ],
    "half_filled_classes": []
}

MONTH_NAMES = {
    9: "Szeptember", 10: "Október", 11: "November", 12: "December",
    1: "Január", 2: "Február", 3: "Március", 4: "Április", 5: "Május", 6: "Június"
}