# config.py

DEFAULT_SETTINGS = {
    "modules": [
        {"name": "1. modul", "start": "2026-09-07", "end": "2026-10-23"},
        {"name": "2. modul", "start": "2026-11-02", "end": "2026-12-18"},
        {"name": "3. modul", "start": "2027-01-11", "end": "2027-02-19"},
        {"name": "4. modul", "start": "2027-03-01", "end": "2027-04-16"},
        {"name": "5. modul", "start": "2027-05-03", "end": "2027-06-18"},
    ],
    "green_start": "2026-09-07",
    "other_school_start": "2026-10-19",
    "christmas_market_date": "2026-12-18",
    "graduation_date": "2027-06-04",
    "vacations": [
        {"name": "Őszi vakáció", "start": "2026-10-24", "end": "2026-11-01"},
        {"name": "Téli vakáció", "start": "2026-12-19", "end": "2027-01-10"},
        {"name": "Tavaszi vakáció", "start": "2027-04-17", "end": "2027-05-02"}
    ],
    "exam_mock": {"start": "2027-03-22", "end": "2027-03-26"},
    "exam_oral": {"start": "2027-06-07", "end": "2027-06-11"},
    "exam_written": {"start": "2027-06-21", "end": "2027-06-25"},
    "classes": [
        {"name": "9C", "room": "228"},
        {"name": "9D", "room": "140"},
        {"name": "9F", "room": "148"},
        {"name": "10A", "room": "231"},
        {"name": "10E", "room": "147"},
        {"name": "11C", "room": "237"},
        {"name": "11F", "room": "42"},
        {"name": "12B", "room": "230"}
    ],
    "half_filled_classes": []
}

MONTH_NAMES = {
    9: "Szeptember", 10: "Október", 11: "November", 12: "December",
    1: "Január", 2: "Február", 3: "Március", 4: "Április", 5: "Május", 6: "Június"
}