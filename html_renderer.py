# html_renderer.py
from calendar_logic import is_vacation_day, is_exam_day


def build_calendar_html(
    header_modules, header_months, week_numbers, filtered_weeks,
    is_green_week_flags, is_module_border, days_of_week,
    table_data, dates_data, public_holidays, vacations_config,
    mock_start, mock_end, oral_start, oral_end, written_start,
    written_end, christmas_market_date, graduation_date,
    half_filled_classes, classes,
    is_full_vacation_flags, xmas_market_complete_flags
):
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
        background-color: #ffffff !important;
        position: relative;
    }
    .half-vacation::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background-color: #ef9a9a;
        clip-path: polygon(0 0, 100% 0, 0 100%);
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
    .weekend-row td {
        background-color: #e0e0e0 !important;
    }
    .full-cancellation {
        background-color: #ef9a9a !important;
        color: #000000 !important;
    }
    .legend-divider {
        width: 1px;
        height: 18px;
        background-color: #777777;
        margin: 0 4px;
        align-self: center;
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
        classes_ = []
        if is_green_week_flags[idx]:
            classes_.append("green-week")
        if is_module_border[idx]:
            classes_.append("border-right-major")
        cls_str = f" class='{' '.join(classes_)}'" if classes_ else ""
        table_css_and_html += f"<th{cls_str}>{w_num}</th>"
    table_css_and_html += "</tr></thead><tbody>"

    # 4. Napok adatai (1-7)
    for idx, day_label in enumerate(days_of_week):
        is_last_day_row = (idx == len(days_of_week) - 1)

        # Check if the row represents Saturday (6) or Sunday (7)
        is_weekend = day_label in ["6", "7"]

        row_classes = []
        if is_last_day_row:
            row_classes.append("border-bottom-section")
        if is_weekend:
            row_classes.append("weekend-row")

        row_cls = f" class='{' '.join(row_classes)}'" if row_classes else ""

        table_css_and_html += f"<tr{row_cls}><td class='day-label border-right-major'>{day_label}</td>"
        for w_idx in range(len(filtered_weeks)):
            val = table_data[day_label][w_idx]
            current_day_date = dates_data[day_label][w_idx]

            classes_ = []
            if val != "":
                if current_day_date in public_holidays:
                    classes_.append("public-holiday")
                elif is_vacation_day(current_day_date, vacations_config):
                    classes_.append("vacation-day")
                elif is_exam_day(current_day_date, mock_start, mock_end, oral_start, oral_end, written_start, written_end):
                    classes_.append("exam-day")
                elif current_day_date == christmas_market_date:
                    classes_.append("xmas-market")
                elif current_day_date == graduation_date:
                    classes_.append("graduation")
                elif is_green_week_flags[w_idx]:
                    classes_.append("green-week")

            if is_module_border[w_idx]:
                classes_.append("border-right-major")

            cls_str = f" class='{' '.join(classes_)}'" if classes_ else ""
            table_css_and_html += f"<td{cls_str}>{val}</td>"
        table_css_and_html += "</tr>"

    # 5. OSZTÁLYOK ÉS TERMEK SORAI
    for cls_idx, cls in enumerate(classes):
        room = cls.get("room", "")
        c_name = cls.get("name", "")

        label = f"{c_name} ({room})" if room and c_name else f"{c_name}{room}"

        table_css_and_html += f"<tr><td class='day-label border-right-major'>{label}</td>"
        for w_idx in range(len(filtered_weeks)):
            week_start_date_str = filtered_weeks[w_idx]['days'][0].strftime("%Y-%m-%d")

            # Megkeressük az adott héthez és osztályhoz tartozó bejegyzést
            half_entry = next(
                (h for h in half_filled_classes if h.get("class_name") == c_name and h.get("week_start") == week_start_date_str),
                None
            )

            classes_ = []

            if half_entry is not None:
                # Ha el van maradva óra, megnézzük, hogy teljesen vagy csak félig
                if half_entry.get("full_cancellation", False):
                    classes_.append("full-cancellation")
                else:
                    classes_.append("half-vacation")
            elif is_full_vacation_flags[w_idx] or xmas_market_complete_flags[w_idx]:
                classes_.append("vacation-day")
            elif is_green_week_flags[w_idx]:
                classes_.append("green-week")

            if is_module_border[w_idx]:
                classes_.append("border-right-major")

            cls_str = f" class='{' '.join(classes_)}'" if classes_ else ""
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
        <div class="legend-divider"></div>
        <div class="legend-item"><span class="legend-box" style="background-color: #ef9a9a;"></span> Teljes óraelmaradás</div>
        <div class="legend-item"><span class="legend-box" style="background: linear-gradient(135deg, #ef9a9a 50%, #ffffff 50%);"></span> Elmaradó óra / Részleges szünet</div>
    </div>
</div>
</div>
"""

    return table_css_and_html


def get_print_button_html():
    # --- NYOMTATÁS GOMB ÉS JS LOGIKA ---
    return """
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
        .half-vacation { background-color: #ffffff !important; position: relative; }
        .half-vacation::before { content: ""; position: absolute; top: 0; right: 0; bottom: 0; left: 0; background-color: #ef9a9a; clip-path: polygon(0 0, 100% 0, 0 100%); }
        .legend-container { margin-top: 15px; border: 1px solid #777777; padding: 8px; background-color: #fafafa; font-size: 11px; text-align: left; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .legend-title { font-weight: bold; font-size: 12px; margin-bottom: 6px; }
        .legend-grid { display: flex; flex-wrap: wrap; gap: 12px; }
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .legend-box { width: 14px; height: 14px; border: 1px solid #555; display: inline-block; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
        .weekend-row td { background-color: #e0e0e0 !important; }
        .full-cancellation { background-color: #ef9a9a !important; color: #000000 !important; }
        .legend-divider { width: 1px !important; height: 18px !important; background-color: #777777 !important; margin: 0 4px !important; align-self: center !important;
    }
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
