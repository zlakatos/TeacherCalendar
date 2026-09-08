import streamlit as st
import json
import os
from datetime import date, timedelta
import streamlit.components.v1 as components

from config import DEFAULT_SETTINGS, MONTH_NAMES
from calendar_logic import (
    parse_d, fetch_public_holidays, generate_academic_calendar,
    get_module_for_week, is_special_green_week, is_vacation_day,
    is_full_vacation_week, is_exam_day, is_xmas_market_completing_vacation
)
from html_renderer import build_calendar_html, get_print_button_html

st.set_page_config(page_title="Tanévi Naptár - Modulokkal", layout="wide")

# --- EGYÉNI SESSION STATE INICIALIZÁLÁS ---
# Adatforrás sorrendje: settings.json (ha érvényes) -> config.DEFAULT_SETTINGS (hiányzó/érvénytelen esetén)
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
public_holidays = fetch_public_holidays()
weeks = generate_academic_calendar(2026)


# --- OLDALSÁV: BEÁLLÍTÁSOK ---
updated_settings = {"modules": [], "vacations": [], "classes": [], "half_filled_classes": []}

# 1. Modulok beállítása
modules_config = []
with st.sidebar.expander("📚 **Modulok időtartama**", expanded=False):
    for i, mod in enumerate(saved_data.get("modules", DEFAULT_SETTINGS["modules"])):
        with st.expander(f"📅 {i + 1}. modul beállítása", expanded=False):
            start_d = st.date_input("Kezdet", value=parse_d(mod["start"]), key=f"start_{i}")
            end_d = st.date_input("Vége", value=parse_d(mod["end"]), key=f"end_{i}")

            modules_config.append({"name": f"{i + 1}. modul", "start": start_d, "end": end_d})
            updated_settings["modules"].append({
                "name": f"{i + 1}. modul",
                "start": start_d.strftime("%Y-%m-%d"),
                "end": end_d.strftime("%Y-%m-%d")
            })

# 2. Vakációk beállítása
vacations_config = []
current_vacations = saved_data.get("vacations", DEFAULT_SETTINGS["vacations"])
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

            vacations_config.append({"name": v_name, "start": v_start, "end": v_end})
            updated_settings["vacations"].append({
                "name": v_name,
                "start": v_start.strftime("%Y-%m-%d"),
                "end": v_end.strftime("%Y-%m-%d")
            })

if vac_to_delete is not None:
    current_vacations.pop(vac_to_delete)
    st.session_state.user_settings["vacations"] = current_vacations
    st.rerun()

# 3. Különleges hetek és napok
# Minden alapérték a config.DEFAULT_SETTINGS-ből jön - nincs duplikált dátum-literál.
with st.sidebar.expander("🌟 **Különleges hetek és napok**", expanded=False):
    with st.expander("🟢 Zöld hét beállítása", expanded=False):
        green_start = st.date_input(
            "Kezdeti nap",
            value=parse_d(saved_data.get("green_start", DEFAULT_SETTINGS["green_start"])),
            key="green_start"
        )
        green_end = green_start + timedelta(days=4)
        st.info(f"Vége: **{green_end.strftime('%Y.%m.%d')}**")

    with st.expander("🟢 Iskola másként hét beállítása", expanded=False):
        other_school_start = st.date_input(
            "Kezdeti nap",
            value=parse_d(saved_data.get("other_school_start", DEFAULT_SETTINGS["other_school_start"])),
            key="other_start"
        )
        other_school_end = other_school_start + timedelta(days=4)
        st.info(f"Vége: **{other_school_end.strftime('%Y.%m.%d')}**")

    with st.expander("🟧 Karácsonyi vásár beállítása", expanded=False):
        christmas_market_date = st.date_input(
            "Vásár napja",
            value=parse_d(saved_data.get("christmas_market_date", DEFAULT_SETTINGS["christmas_market_date"])),
            key="xmas_market"
        )

    with st.expander("🟪 Ballagás beállítása", expanded=False):
        graduation_date = st.date_input(
            "Ballagás napja",
            value=parse_d(saved_data.get("graduation_date", DEFAULT_SETTINGS["graduation_date"])),
            key="graduation"
        )

updated_settings["green_start"] = green_start.strftime("%Y-%m-%d")
updated_settings["other_school_start"] = other_school_start.strftime("%Y-%m-%d")
updated_settings["christmas_market_date"] = christmas_market_date.strftime("%Y-%m-%d")
updated_settings["graduation_date"] = graduation_date.strftime("%Y-%m-%d")

# 4. Érettségi beállítása
saved_mock = saved_data.get("exam_mock", DEFAULT_SETTINGS["exam_mock"])
saved_oral = saved_data.get("exam_oral", DEFAULT_SETTINGS["exam_oral"])
saved_written = saved_data.get("exam_written", DEFAULT_SETTINGS["exam_written"])

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

# 5. Osztályok és termek
current_classes = saved_data.get("classes", DEFAULT_SETTINGS["classes"])
class_to_delete = None

with st.sidebar.expander("🏫 **Osztályok és termek**", expanded=False):
    if st.button("➕ Új osztály hozzáadása"):
        current_classes.append({"name": "Új osztály", "room": "100"})
        st.session_state.user_settings["classes"] = current_classes
        st.rerun()

    for i, cls in enumerate(current_classes):
        with st.expander(f"🏫 {cls.get('name', '')} osztály ({cls.get('room', '')}. terem)", expanded=False):
            c_name = st.text_input("Osztály neve", value=cls.get("name", ""), key=f"cls_name_{i}")
            c_room = st.text_input("Terem száma", value=cls.get("room", ""), key=f"cls_room_{i}")

            if st.button("🗑️ Osztály törlése", key=f"del_cls_{i}T"):
                class_to_delete = i

            updated_settings["classes"].append({"name": c_name, "room": c_room})

if class_to_delete is not None:
    current_classes.pop(class_to_delete)
    st.session_state.user_settings["classes"] = current_classes
    st.rerun()

# 6. Elmaradó órák
# 6. Elmaradó órák
current_half_filled = saved_data.get("half_filled_classes", DEFAULT_SETTINGS["half_filled_classes"])
half_to_delete = None

week_start_options = [w['days'][0] for w in weeks]
class_names_options = [c.get("name", "") for c in updated_settings["classes"] if c.get("name", "")]

with st.sidebar.expander("🌗 **Elmaradó órák**", expanded=False):
    if st.button("➕ Új elmaradó óra hozzáadása"):
        if class_names_options:
            current_half_filled.insert(0, {
                "class_name": class_names_options[0],
                "week_start": week_start_options[0].strftime("%Y-%m-%d"),
                "full_cancellation": False
            })
            st.session_state.user_settings["half_filled_classes"] = current_half_filled
            st.rerun()
        else:
            st.warning("Előbb adj hozzá osztályokat!")

    for i, item in enumerate(current_half_filled):
        with st.expander(f"🌗 {item.get('class_name', '')} - Hét: {item.get('week_start', '')}", expanded=False):
            selected_cls = st.selectbox(
                "Osztály", options=class_names_options,
                index=class_names_options.index(item["class_name"]) if item["class_name"] in class_names_options else 0,
                key=f"half_cls_{i}"
            )

            default_w_date = parse_d(item["week_start"]) if "week_start" in item else week_start_options[0]
            if default_w_date not in week_start_options:
                default_w_date = week_start_options[0]

            selected_week_start = st.selectbox(
                "Melyik hét (Hétfői nap)", options=week_start_options,
                format_func=lambda d: f"{d.strftime('%Y.%m.%d')} hete",
                index=week_start_options.index(default_w_date),
                key=f"half_week_{i}"
            )

            # ÚJ: Jelölőnégyzet a teljes óraelmaradáshoz (alapértelmezetten False)
            is_full_cancel = st.checkbox(
                "Minden óra elmarad a héten (Teljesen piros cella)",
                value=item.get("full_cancellation", False),
                key=f"full_cancel_{i}"
            )

            if st.button("🗑️ Törlés", key=f"del_half_{i}"):
                half_to_delete = i

            updated_settings["half_filled_classes"].append({
                "class_name": selected_cls,
                "week_start": selected_week_start.strftime("%Y-%m-%d"),
                "full_cancellation": is_full_cancel
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

uploaded_file = st.sidebar.file_uploader("📂 Beállítások betöltése (JSON)", type=["json"], key="json_uploader")

if uploaded_file is not None:
    # Use session state to track if this specific file was already processed
    if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
        try:
            loaded_data = json.load(uploaded_file)
            st.session_state.user_settings = {**DEFAULT_SETTINGS, **loaded_data}
            st.session_state["last_uploaded_filename"] = uploaded_file.name
            st.success("Sikeres beállítás betöltés!")
            st.rerun()
        except Exception as e:
            st.error(f"Hiba a fájl olvasásakor: {e}")

if st.sidebar.button("🔄 Alapértelmezések visszaállítása"):
    st.session_state.user_settings = DEFAULT_SETTINGS.copy()
    st.rerun()


# --- NAPTÁR ÉS ADATOK ELŐKÉSZÍTÉSE ---
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

        valid_months = [d.month for d in w['days'] if d.month in MONTH_NAMES]
        if valid_months:
            main_month = max(set(valid_months), key=valid_months.count)
            header_months.append(MONTH_NAMES[main_month])
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

# HTML generálás a renderer modulból
calendar_html = build_calendar_html(
    header_modules, header_months, week_numbers, filtered_weeks,
    is_green_week_flags, is_module_border, days_of_week,
    table_data, dates_data, public_holidays, vacations_config,
    mock_start, mock_end, oral_start, oral_end, written_start,
    written_end, christmas_market_date, graduation_date,
    st.session_state.user_settings.get("half_filled_classes", []),
    st.session_state.user_settings.get("classes", DEFAULT_SETTINGS["classes"]),
    is_full_vacation_flags, xmas_market_complete_flags
)

print_button = get_print_button_html()

# Megjelenítés Streamlitben
components.html(print_button + calendar_html, height=800, scrolling=True)
