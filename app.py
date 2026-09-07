import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import date, datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Tanévi Naptár - Modulokkal", layout="wide")

# --- ALAPÉRTELMEZETT BEÁLLÍTÁSOK ---
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

# --- EGYÉNI SESSION STATE INICIALIZÁLÁS ---
if "user_settings" not in st.session_state:
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                st.session_state.user_settings = {**DEFAULT_SETTINGS, **loaded}
        except Exception:
            st.session_state.user_settings = DEFAULT_SETTINGS.copy()
    else:
        st.session_state.user_settings = DEFAULT_SETTINGS.copy()

saved_data = st.session_state.user_settings

def parse_d(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


# --- HIVATALOS ÜNNEPNAPOK LEKÉRDEZÉSE API-RÓL ---
@st.cache_data
def fetch_public_holidays(years=[2026, 2027], country_code="RO"):
    holidays = set()
    for year in years:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                for item in data:
                    h_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
                    holidays.add(h_date)
        except Exception:
            pass
    return holidays

public_holidays = fetch_public_holidays()


# --- NAPTÁR ADATOK GENERÁLÁSA ---
def generate_academic_calendar(start_year=2026):
    start_date = date(start_year, 9, 1)
    end_date = date(start_year + 1, 6, 30)

    current_date = start_date - timedelta(days=start_date.weekday())
    weeks_data = []
    
    while current_date <= end_date:
        week_days = [current_date + timedelta(days=d) for d in range(7)]
        if any(start_date <= d <= end_date for d in week_days):
            weeks_data.append({'days': week_days})
        current_date += timedelta(days=7)

    return weeks_data

weeks = generate_academic_calendar(2026)


# --- OLDALSÁV: BEÁLLÍTÁSOK ---

updated_settings = {"modules": [], "vacations": [], "classes": [], "half_filled_classes": []}

# 1. MODULOK BEÁLLÍTÁSA
modules_config = []
with st.sidebar.expander("📚 **Modulok időtartama**", expanded=False):
    for i, mod in enumerate(saved_data.get("modules", [])):
        with st.expander(f"📅 {i + 1}. modul beállítása", expanded=False):
            start_d = st.date_input("Kezdet", value=parse_d(mod["start"]), key=f"start_{i}")
            end_d = st.date_input("Vége", value=parse_d(mod["end"]), key=f"end_{i}")
            
            modules_config.append({
                "name": f"{i + 1}. modul",
                "start": start_d,
                "end": end_d
            })
            
            updated_settings["modules"].append({
                "name": f"{i + 1}. modul",
                "start": start_d.strftime("%Y-%m-%d"),
                "end": end_d.strftime("%Y-%m-%d")
            })

# 2. MANUÁLIS VAKÁCIÓK BEÁLLÍTÁSA
vacations_config = []
current_vacations = saved_data.get("vacations", [])
vac_to_delete = None

with st.sidebar.expander("🏖️ **Vakációk beállítása**", expanded=False):
    if st.button("➕ Új vakáció hozzáadása"):
        current_vacations.append({"name": f"Új vakáció {len(current_vacations) + 1}", "start": "2026-10-24", "end": "2026-11-01"})
        st.session_state.user_settings["vacations"] = current_vacations
        st.rerun()

    for i, vac in enumerate(current_vacations):
        with st.expander(f"🏖️ {vac.get('name', 'Vakáció')}", expanded=False):
            v_name = st.text_input("Vakáció neve", value=vac.get("name", "Vakáció"), key=f"vac_name_{i}")
            v_start = st.date_input("Kezdő nap", value=parse_d(vac["start"]), key=f"vac_start_{i}")
            v_end = st.date_input("Utolsó nap", value=parse_d(vac["end"]), key=f"vac_end_{i}")
            
            if st.button("🗑️ Vakáció törlése", key=f"del_vac_{i}"):
                vac_to_delete = i
            
            vacations_config.append({
                "name": v_name,
                "start": v_start,
                "end": v_end
            })
            updated_settings["vacations"].append({
                "name": v_name,
                "start": v_start.strftime("%Y-%m-%d"),
                "end": v_end.strftime("%Y-%m-%d")
            })

if vac_to_delete is not None:
    current_vacations.pop(vac_to_delete)
    st.session_state.user_settings["vacations"] = current_vacations
    st.rerun()

# 3. KÜLÖNLEGES HETEK ÉS NAPOK
with st.sidebar.expander("🌟 **Különleges hetek és napok**", expanded=False):
    with st.expander("🟢 Zöld hét beállítása", expanded=False):
        green_start = st.date_input(
            "Kezdeti nap", 
            value=parse_d(saved_data.get("green_start", "2026-09-07")), 
            key="green_start"
        )
        green_end = green_start + timedelta(days=4)
        st.info(f"Vége: **{green_end.strftime('%Y.%m.%d')}**")

    with st.expander("🟢 Iskola másként hét beállítása", expanded=False):
        other_school_start = st.date_input(
            "Kezdeti nap", 
            value=parse_d(saved_data.get("other_school_start", "2026-10-19")), 
            key="other_start"
        )
        other_school_end = other_school_start + timedelta(days=4)
        st.info(f"Vége: **{other_school_end.strftime('%Y.%m.%d')}**")

    with st.expander("🟧 Karácsonyi vásár beállítása", expanded=False):
        christmas_market_date = st.date_input(
            "Vásár napja", 
            value=parse_d(saved_data.get("christmas_market_date", "2026-12-18")), 
            key="xmas_market"
        )

    with st.expander("🟪 Ballagás beállítása", expanded=False):
        graduation_date = st.date_input(
            "Ballagás napja", 
            value=parse_d(saved_data.get("graduation_date", "2027-06-04")), 
            key="graduation"
        )

updated_settings["green_start"] = green_start.strftime("%Y-%m-%d")
updated_settings["other_school_start"] = other_school_start.strftime("%Y-%m-%d")
updated_settings["christmas_market_date"] = christmas_market_date.strftime("%Y-%m-%d")
updated_settings["graduation_date"] = graduation_date.strftime("%Y-%m-%d")

# 4. ÉRETTSÉGI BEÁLLÍTÁSA
saved_mock = saved_data.get("exam_mock", {"start": "2027-03-22", "end": "2027-03-26"})
saved_oral = saved_data.get("exam_oral", {"start": "2027-06-07", "end": "2027-06-11"})
saved_written = saved_data.get("exam_written", {"start": "2027-06-21", "end": "2027-06-25"})

with st.sidebar.expander("🎓 **Érettségi**", expanded=False):
    with st.expander("📝 Próbaérettségi", expanded=False):
        mock_start = st.date_input("Kezdő nap", value=parse_d(saved_mock["start"]), key="mock_start")
        mock_end = st.date_input("Végső nap", value=parse_d(saved_mock["end"]), key="mock_end")

    with st.expander("🗣️ Szóbeli érettségi", expanded=False):
        oral_start = st.date_input("Kezdő nap", value=parse_d(saved_oral["start"]), key="oral_start")
        oral_end = st.date_input("Végső nap", value=parse_d(saved_oral["end"]), key="oral_end")

    with st.expander("✍️ Írásbeli érettségi", expanded=False):
        written_start = st.date_input("Kezdő nap", value=parse_d(saved_written["start"]), key="written_start")
        written_end = st.date_input("Végső nap", value=parse_d(saved_written["end"]), key="written_end")

updated_settings["exam_mock"] = {"start": mock_start.strftime("%Y-%m-%d"), "end": mock_end.strftime("%Y-%m-%d")}
updated_settings["exam_oral"] = {"start": oral_start.strftime("%Y-%m-%d"), "end": oral_end.strftime("%Y-%m-%d")}
updated_settings["exam_written"] = {"start": written_start.strftime("%Y-%m-%d"), "end": written_end.strftime("%Y-%m-%d")}

# 5. OSZTÁLYOK ÉS TERMEK BEÁLLÍTÁSA
current_classes = saved_data.get("classes", [])
class_to_delete = None

with st.sidebar.expander("🏫 **Osztályok és termek**", expanded=False):
    if st.button("➕ Új osztály hozzáadása"):
        current_classes.append({"name": f"Új osztály", "room": "100"})
        st.session_state.user_settings["classes"] = current_classes
        st.rerun()

    for i, cls in enumerate(current_classes):
        with st.expander(f"🏫 {cls.get('name', '')} osztály ({cls.get('room', '')}. terem)", expanded=False):
            c_name = st.text_input("Osztály neve", value=cls.get("name", ""), key=f"cls_name_{i}")
            c_room = st.text_input("Terem száma", value=cls.get("room", ""), key=f"cls_room_{i}")
            
            if st.button("🗑️ Osztály törlése", key=f"del_cls_{i}"):
                class_to_delete = i
            
            updated_settings["classes"].append({"name": c_name, "room": c_room})

if class_to_delete is not None:
    current_classes.pop(class_to_delete)
    st.session_state.user_settings["classes"] = current_classes
    st.rerun()

# 6. ELMARADÓ ÓRÁK BEÁLLÍTÁSA
current_half_filled = saved_data.get("half_filled_classes", [])
half_to_delete = None

week_start_options = [w['days'][0] for w in weeks]
class_names_options = [c.get("name", "") for c in updated_settings["classes"] if c.get("name", "")]

with st.sidebar.expander("🌗 **Elmaradó órák**", expanded=False):
    if st.button("➕ Új elmaradó óra hozzáadása"):
        if class_names_options:
            current_half_filled.insert(0, {
                "class_name": class_names_options[0],
                "week_start": week_start_options[0].strftime("%Y-%m-%d")
            })
            st.session_state.user_settings["half_filled_classes"] = current_half_filled
            st.rerun()
        else:
            st.warning("Előbb adj hozzá osztályokat!")

    for i, item in enumerate(current_half_filled):
        with st.expander(f"🌗 {item.get('class_name', '')} - Hét: {item.get('week_start', '')}", expanded=False):
            selected_cls = st.selectbox(
                "Osztály", 
                options=class_names_options, 
                index=class_names_options.index(item["class_name"]) if item["class_name"] in class_names_options else 0,
                key=f"half_cls_{i}"
            )
            
            default_w_date = parse_d(item["week_start"]) if "week_start" in item else week_start_options[0]
            if default_w_date not in week_start_options:
                default_w_date = week_start_options[0]
                
            selected_week_start = st.selectbox(
                "Melyik hét (Hétfői nap)",
                options=week_start_options,
                format_func=lambda d: f"{d.strftime('%Y.%m.%d')} hete",
                index=week_start_options.index(default_w_date),
                key=f"half_week_{i}"
            )
            
            if st.button("🗑️ Törlés", key=f"del_half_{i}"):
                half_to_delete = i
                
            updated_settings["half_filled_classes"].append({
                "class_name": selected_cls,
                "week_start": selected_week_start.strftime("%Y-%m-%d")
            })

if half_to_delete is not None:
    current_half_filled.pop(half_to_delete)
    st.session_state.user_settings["half_filled_classes"] = current_half_filled
    st.rerun()

for key in updated_settings:
    st.session_state.user_settings[key] = updated_settings[key]

st.sidebar.markdown("---")

st.sidebar.subheader("💾 Beállítások fájl")
json_str = json.dumps(st.session_state.user_settings, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 Saját beállítások letöltése",
    data=json_str,
    file_name="settings.json",
    mime="application/json"
)

uploaded_file = st.sidebar.file_uploader("📂 Beállítások betöltése (JSON)", type=["json"])
if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        st.session_state.user_settings = {**DEFAULT_SETTINGS, **loaded_data}
        st.success("Sikeres beállítás betöltés!")
        st.rerun()
    except Exception as e:
        st.error(f"Hiba a fájl olvasásakor: {e}")

if st.sidebar.button("🔄 Alapértelmezések visszaállítása"):
    st.session_state.user_settings = DEFAULT_SETTINGS.copy()
    st.rerun()


# --- SEGÉDFÜGGVÉNYEK ÉS FELTÉTELEK ---

month_names = {
    9: "Szeptember", 10: "Október", 11: "November", 12: "December",
    1: "Január", 2: "Február", 3: "Március", 4: "Április", 5: "Május", 6: "Június"
}

def get_module_for_week(week_days, modules):
    module_counts = {mod["name"]: 0 for mod in modules}
    for day in week_days:
        for mod in modules:
            if mod["start"] <= day <= mod["end"]:
                module_counts[mod["name"]] += 1
                
    best_module = max(module_counts, key=module_counts.get)
    if module_counts[best_module] > 0:
        return best_module
    return ""

def is_special_green_week(week_days, g_start, g_end, o_start, o_end):
    for day in week_days:
        if (g_start <= day <= g_end) or (o_start <= day <= o_end):
            return True
    return False

def is_vacation_day(day_date, vacations):
    for vac in vacations:
        if vac["start"] <= day_date <= vac["end"]:
            return True
    return False

def is_full_vacation_week(week_days, vacations):
    work_days = week_days[:5]
    return all(is_vacation_day(d, vacations) for d in work_days)

def is_exam_day(day_date, mock_s, mock_e, oral_s, oral_e, written_s, written_e):
    if day_date.weekday() in [5, 6]:
        return False
    return (mock_s <= day_date <= mock_e) or (oral_s <= day_date <= oral_e) or (written_s <= day_date <= written_e)

def is_xmas_market_completing_vacation(week_days, market_date, vacations):
    work_days = week_days[:5]
    if market_date not in work_days:
        return False
    
    other_work_days = [d for d in work_days if d != market_date]
    return all(is_vacation_day(d, vacations) for d in other_work_days)


# --- ADATOK ELŐKÉSZÍTÉSE ---
header_modules = []
header_months = []
week_numbers = []
filtered_weeks = []
is_green_week_flags = []
is_full_vacation_flags = []
xmas_market_complete_flags = []

display_week_counter = 1

for w in weeks:
    mod_name = get_module_for_week(w['days'], modules_config)
    full_vac = is_full_vacation_week(w['days'], vacations_config)
    
    if mod_name != "" or full_vac:
        filtered_weeks.append(w)
        is_full_vacation_flags.append(full_vac)
        
        xmas_complete = is_xmas_market_completing_vacation(w['days'], christmas_market_date, vacations_config)
        xmas_market_complete_flags.append(xmas_complete)
        
        if full_vac:
            header_modules.append("")
            week_numbers.append("")
        else:
            header_modules.append(mod_name)
            week_numbers.append(display_week_counter)
            display_week_counter += 1
        
        valid_months = [d.month for d in w['days'] if d.month in month_names]
        if valid_months:
            main_month = max(set(valid_months), key=valid_months.count)
            header_months.append(month_names[main_month])
        else:
            header_months.append("")
        
        special = is_special_green_week(w['days'], green_start, green_end, other_school_start, other_school_end)
        is_green_week_flags.append(special)

days_of_week = ["1", "2", "3", "4", "5", "6", "7"]
table_data = {day_label: [] for day_label in days_of_week}
dates_data = {day_label: [] for day_label in days_of_week}

for w in filtered_weeks:
    for idx, day_label in enumerate(days_of_week):
        day = w['days'][idx]
        dates_data[day_label].append(day)
        if date(2026, 9, 1) <= day <= date(2027, 6, 30):
            table_data[day_label].append(str(day.day))
        else:
            table_data[day_label].append("")

is_module_border = []
for i in range(len(header_modules)):
    if i == len(header_modules) - 1:
        is_module_border.append(False)
    else:
        curr_m = header_modules[i]
        next_m = header_modules[i+1]
        is_module_border.append(curr_m != "" and next_m != "" and curr_m != next_m)


# --- HTML TÁBLÁZAT KÓDJA (BELEÉRTVE A JELMAGYARÁZATOT IS) ---
table_css_and_html = """
<style>
    .calendar-container {
        font-family: Arial, sans-serif;
        background-color: #ffffff;
        color: #000000;
        padding: 10px;
    }
    .calendar-title {
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
        color: #000000;
    }
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 13px;
        text-align: center;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #000000;
        margin-bottom: 20px;
    }
    .calendar-table th, .calendar-table td {
        border: 1px solid #777777;
        padding: 4px;
        background-color: #ffffff;
        color: #000000;
        min-width: 30px;
    }
    .calendar-table th {
        font-weight: bold;
    }
    .day-label {
        font-weight: bold;
        text-align: center;
        background-color: #f2f2f2 !important;
        white-space: nowrap;
        width: 45px;
    }
    .border-bottom-major {
        border-bottom: 2px solid #000000 !important;
    }
    .border-right-major {
        border-right: 2px solid #000000 !important;
    }
    .border-bottom-section {
        border-bottom: 2px solid #000000 !important;
    }
    .public-holiday {
        background-color: #ef9a9a !important;
        color: #000000 !important;
    }
    .vacation-day {
        background-color: #90caf9 !important;
        color: #000000 !important;
    }
    .exam-day {
        background-color: #ffe082 !important;
        color: #000000 !important;
    }
    .green-week {
        background-color: #a5d6a7 !important;
        color: #000000 !important;
    }
    .xmas-market {
        background-color: #ffcc80 !important;
        color: #000000 !important;
    }
    .graduation {
        background-color: #e1bee7 !important;
        color: #000000 !important;
    }
    .half-vacation {
        background: linear-gradient(135deg, #ef9a9a 50%, #ffffff 50%) !important;
    }
    
    /* Jelmagyarázat stílusok */
    .legend-container {
        margin-top: 20px;
        border: 1px solid #777777;
        padding: 10px;
        background-color: #fafafa;
        font-size: 12px;
        text-align: left;
    }
    .legend-title {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .legend-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .legend-box {
        width: 16px;
        height: 16px;
        border: 1px solid #555;
        display: inline-block;
    }
</style>
<div style="overflow-x: auto;" id="printable-calendar" class="calendar-container">
<div class="calendar-title">2026–2027-ES TANÉV</div>
<table class="calendar-table">
    <thead>
"""

# 1. Modul sor
table_css_and_html += "<tr class='border-bottom-major'><th rowspan='3' class='border-bottom-major border-right-major'>Napok / Termek</th>"

blocks = []
if header_modules:
    current_mod = header_modules[0]
    current_span = 1
    for m in header_modules[1:]:
        if m == current_mod:
            current_span += 1
        else:
            blocks.append((current_mod, current_span))
            current_mod = m
            current_span = 1
    blocks.append((current_mod, current_span))

merged_blocks = []
for mod, span in blocks:
    if mod == "" and merged_blocks:
        prev_mod, prev_span = merged_blocks.pop()
        merged_blocks.append((prev_mod, prev_span + span))
    elif mod == "" and not merged_blocks:
        merged_blocks.append((mod, span))
    else:
        if merged_blocks and merged_blocks[-1][0] == "":
            empty_mod, empty_span = merged_blocks.pop()
            if merged_blocks:
                prev_mod, prev_span = merged_blocks.pop()
                merged_blocks.append((prev_mod, prev_span + empty_span + span))
            else:
                merged_blocks.append((mod, empty_span + span))
        else:
            merged_blocks.append((mod, span))

if len(merged_blocks) > 1 and merged_blocks[0][0] == "":
    empty_mod, empty_span = merged_blocks.pop(0)
    next_mod, next_span = merged_blocks.pop(0)
    merged_blocks.insert(0, (next_mod, empty_span + next_span))

for b_idx, (mod, span) in enumerate(merged_blocks):
    is_last = (b_idx == len(merged_blocks) - 1)
    border_cls = " class='border-right-major'" if not is_last else ""
    display_name = mod if mod != "" else ""
    table_css_and_html += f"<th colspan='{span}'{border_cls}>{display_name}</th>"

table_css_and_html += "</tr>"

# 2. Hónap sor
table_css_and_html += "<tr class='border-bottom-major'>"
current_month = header_months[0]
span = 0

for i, month in enumerate(header_months):
    if month == current_month:
        span += 1
    else:
        border_cls = " class='border-right-major'" if is_module_border[i-1] else ""
        table_css_and_html += f"<th colspan='{span}'{border_cls}>{current_month}</th>"
        current_month = month
        span = 1
border_cls = " class='border-right-major'" if is_module_border[len(header_months)-2] else ""
table_css_and_html += f"<th colspan='{span}'{border_cls}>{current_month}</th></tr>"

# 3. Hét sorszám sor
table_css_and_html += "<tr class='border-bottom-major'>"
for idx, w_num in enumerate(week_numbers):
    classes = []
    if is_green_week_flags[idx]:
        classes.append("green-week")
    if is_module_border[idx]:
        classes.append("border-right-major")
    cls_str = f" class='{' '.join(classes)}'" if classes else ""
    table_css_and_html += f"<th{cls_str}>{w_num}</th>"
table_css_and_html += "</tr></thead><tbody>"

# 4. Napok adatai (1-7)
for idx, day_label in enumerate(days_of_week):
    is_last_day_row = (idx == len(days_of_week) - 1)
    row_cls = " class='border-bottom-section'" if is_last_day_row else ""
    
    table_css_and_html += f"<tr{row_cls}><td class='day-label border-right-major'>{day_label}</td>"
    for w_idx in range(len(filtered_weeks)):
        val = table_data[day_label][w_idx]
        current_day_date = dates_data[day_label][w_idx]
        
        classes = []
        if val != "":
            if current_day_date in public_holidays:
                classes.append("public-holiday")
            elif is_vacation_day(current_day_date, vacations_config):
                classes.append("vacation-day")
            elif is_exam_day(current_day_date, mock_start, mock_end, oral_start, oral_end, written_start, written_end):
                classes.append("exam-day")
            elif current_day_date == christmas_market_date:
                classes.append("xmas-market")
            elif current_day_date == graduation_date:
                classes.append("graduation")
            elif is_green_week_flags[w_idx]:
                classes.append("green-week")
                
        if is_module_border[w_idx]:
            classes.append("border-right-major")
            
        cls_str = f" class='{' '.join(classes)}'" if classes else ""
        table_css_and_html += f"<td{cls_str}>{val}</td>"
    table_css_and_html += "</tr>"

# 5. OSZTÁLYOK ÉS TERMEK SORAI
half_filled_list = st.session_state.user_settings.get("half_filled_classes", [])

for cls_idx, cls in enumerate(st.session_state.user_settings["classes"]):
    room = cls.get("room", "")
    c_name = cls.get("name", "")
    
    label = f"{c_name} ({room})" if room and c_name else f"{c_name}{room}"
    
    table_css_and_html += f"<tr><td class='day-label border-right-major'>{label}</td>"
    for w_idx in range(len(filtered_weeks)):
        week_start_date_str = filtered_weeks[w_idx]['days'][0].strftime("%Y-%m-%d")
        
        is_half = any(
            h.get("class_name") == c_name and h.get("week_start") == week_start_date_str 
            for h in half_filled_list
        )
        
        classes = []
        
        if is_half:
            classes.append("half-vacation")
        elif is_full_vacation_flags[w_idx] or xmas_market_complete_flags[w_idx]:
            classes.append("vacation-day")
        elif is_green_week_flags[w_idx]:
            classes.append("green-week")
            
        if is_module_border[w_idx]:
            classes.append("border-right-major")
            
        cls_str = f" class='{' '.join(classes)}'" if classes else ""
        table_css_and_html += f"<td{cls_str}></td>"
    table_css_and_html += "</tr>"

# --- JELMAGYARÁZAT SZEKCIÓ A TÁBLÁZAT ALATT ---
table_css_and_html += """
</tbody></table>
<div class="legend-container">
    <div class="legend-title">Jelmagyarázat</div>
    <div class="legend-grid">
        <div class="legend-item"><span class="legend-box" style="background-color: #90caf9;"></span> Vakáció</div>
        <div class="legend-item"><span class="legend-box" style="background-color: #ef9a9a;"></span> Hivatalos ünnepnap</div>
        <div class="legend-item"><span class="legend-box" style="background-color: #a5d6a7;"></span> Zöld hét / Iskola másként</div>
        <div class="legend-item"><span class="legend-box" style="background-color: #ffcc80;"></span> Karácsonyi vásár</div>
        <div class="legend-item"><span class="legend-box" style="background-color: #ffe082;"></span> Érettségi / Próbaérettségi</div>
        <div class="legend-item"><span class="legend-box" style="background-color: #e1bee7;"></span> Ballagás</div>
        <div class="legend-item"><span class="legend-box" style="background: linear-gradient(135deg, #ef9a9a 50%, #ffffff 50%);"></span> Elmaradó óra / Részleges szünet</div>
    </div>
</div>
</div>
"""


# --- NYOMTATÁS GOMB ÉS JS LOGIKA ---
print_button_html = """
<script>
function printTable() {
    var divContent = document.getElementById("printable-calendar").innerHTML;
    var printWindow = window.open('', '', 'height=900,width=1200');
    printWindow.document.write('<html><head><title>Tanévi Naptár</title>');
    printWindow.document.write('<style>');
    printWindow.document.write(`
        body { font-family: Arial, sans-serif; margin: 10px; background: #fff; }
        .calendar-container { font-family: Arial, sans-serif; background-color: #ffffff; color: #000000; padding: 10px; }
        .calendar-title { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 15px; color: #000000; }
        .calendar-table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: center; background-color: #ffffff; color: #000000; border: 2px solid #000000; margin-bottom: 15px; }
        .calendar-table th, .calendar-table td { border: 1px solid #777777; padding: 3px; background-color: #ffffff; color: #000000; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .calendar-table th { font-weight: bold; }
        .day-label { font-weight: bold; text-align: center; background-color: #f2f2f2 !important; white-space: nowrap; width: 45px; }
        .border-bottom-major { border-bottom: 2px solid #000000 !important; }
        .border-right-major { border-right: 2px solid #000000 !important; }
        .border-bottom-section { border-bottom: 2px solid #000000 !important; }
        .public-holiday { background-color: #ef9a9a !important; color: #000000 !important; }
        .vacation-day { background-color: #90caf9 !important; color: #000000 !important; }
        .exam-day { background-color: #ffe082 !important; color: #000000 !important; }
        .green-week { background-color: #a5d6a7 !important; color: #000000 !important; }
        .xmas-market { background-color: #ffcc80 !important; color: #000000 !important; }
        .graduation { background-color: #e1bee7 !important; color: #000000 !important; }
        .half-vacation { background: linear-gradient(135deg, #ef9a9a 50%, #ffffff 50%) !important; }
        .legend-container { margin-top: 15px; border: 1px solid #777777; padding: 8px; background-color: #fafafa; font-size: 11px; text-align: left; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .legend-title { font-weight: bold; font-size: 12px; margin-bottom: 6px; }
        .legend-grid { display: flex; flex-wrap: wrap; gap: 12px; }
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .legend-box { width: 14px; height: 14px; border: 1px solid #555; display: inline-block; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    `);
    printWindow.document.write('</style></head><body>');
    printWindow.document.write(divContent);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(function() {
        printWindow.print();
        printWindow.close();
    }, 500);
}
</script>
<button onclick="printTable()" style="background-color: #4CAF50; color: white; padding: 10px 20px; font-size: 16px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 15px;">
    🖨️ Naptár nyomtatása
</button>
"""

# Megjelenítés Streamlitben
components.html(print_button_html + table_css_and_html, height=800, scrolling=True)