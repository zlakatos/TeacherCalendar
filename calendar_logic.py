# calendar_logic.py
from datetime import date, datetime, timedelta
import requests
import streamlit as st

def parse_d(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()

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