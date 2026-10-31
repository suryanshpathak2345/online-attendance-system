import re
import io
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.models.academic import ClassRoom, Subject, Student
from app.models.session import ClassSession, SessionStatus
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.config import settings
from app.services.attendance_calculator import calculate_percentage


def sanitize_filename(filename: str) -> str:
    """Sanitize string for safe filenames across OSes."""
    return re.sub(r'[\\/*?:"<>| ]', '_', filename)


def generate_attendance_excel(
    db: Session,
    class_id: int,
    subject_id: int,
    teacher_name: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[io.BytesIO, str]:
    """
    Generate an Excel attendance register workbook matching official attendance records.
    Returns (BytesIO buffer, sanitized_filename).
    """
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not classroom or not subject:
        raise ValueError("Class or Subject not found")

    # Fetch all relevant sessions ordered by date
    query = db.query(ClassSession).filter(
        ClassSession.class_id == class_id,
        ClassSession.subject_id == subject_id
    )
    if start_date:
        query = query.filter(ClassSession.session_date >= start_date)
    if end_date:
        query = query.filter(ClassSession.session_date <= end_date)
    
    sessions = query.order_by(ClassSession.session_date, ClassSession.id).all()

    # Active students in class
    students = db.query(Student).filter(
        Student.class_id == class_id,
        Student.is_active == True
    ).order_by(Student.roll_number).all()

    # Create Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance Register"
    ws.views.sheetView[0].showGridLines = True

    # Styles
    title_font = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    subtitle_font = Font(name="Calibri", size=11, bold=True, color="334155")
    header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10)
    summary_font = Font(name="Calibri", size=10, bold=True)
    
    header_fill = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
    conducted_date_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    cancelled_date_fill = PatternFill(start_color="64748B", end_color="64748B", fill_type="solid")
    holiday_date_fill = PatternFill(start_color="7C3AED", end_color="7C3AED", fill_type="solid")
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    
    # Status Fills
    present_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")  # soft green
    absent_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")   # soft red
    halfday_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")  # soft amber

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # 1. Header Information Block
    ws.merge_cells("A1:G1")
    ws["A1"] = f"{settings.institution_name} - Attendance Register"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="left", vertical="center")

    info_rows = [
        ("Class & Section:", f"{classroom.name} - {classroom.section}", "Academic Year:", classroom.academic_year),
        ("Subject:", f"{subject.name} ({subject.code})", "Teacher:", teacher_name),
        ("Date Range:", f"{start_date.isoformat() if start_date else 'All'} to {end_date.isoformat() if end_date else 'Present'}", "Threshold:", f"{settings.default_attendance_threshold}%")
    ]

    current_row = 3
    for label1, val1, label2, val2 in info_rows:
        ws.cell(row=current_row, column=1, value=label1).font = subtitle_font
        ws.cell(row=current_row, column=2, value=val1).font = data_font
        ws.cell(row=current_row, column=4, value=label2).font = subtitle_font
        ws.cell(row=current_row, column=5, value=val2).font = data_font
        current_row += 1

    current_row += 1
    table_header_row = current_row

    # 2. Table Column Headers
    headers = ["Roll No", "Student Name"]
    ws.cell(row=table_header_row, column=1, value=headers[0])
    ws.cell(row=table_header_row, column=2, value=headers[1])
    ws.cell(row=table_header_row, column=1).font = header_font
    ws.cell(row=table_header_row, column=1).fill = header_fill
    ws.cell(row=table_header_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
    ws.cell(row=table_header_row, column=2).font = header_font
    ws.cell(row=table_header_row, column=2).fill = header_fill
    ws.cell(row=table_header_row, column=2).alignment = Alignment(horizontal="left", vertical="center")

    col_idx = 3
    session_col_map = {}

    for s in sessions:
        date_label = s.session_date.strftime("%d/%m")
        cell = ws.cell(row=table_header_row, column=col_idx, value=date_label)
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
        if s.status == SessionStatus.CONDUCTED:
            cell.fill = conducted_date_fill
        elif s.status == SessionStatus.CANCELLED:
            cell.fill = cancelled_date_fill
        elif s.status == SessionStatus.HOLIDAY:
            cell.fill = holiday_date_fill
        else:
            cell.fill = header_fill
            
        session_col_map[s.id] = col_idx
        col_idx += 1

    # Summary columns
    summary_headers = ["Conducted", "Attended", "Absent", "Attendance %"]
    for sh in summary_headers:
        cell = ws.cell(row=table_header_row, column=col_idx, value=sh)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        col_idx += 1

    # Pre-fetch attendance records for all sessions
    conducted_sessions = [s for s in sessions if s.status == SessionStatus.CONDUCTED and s.is_attendance_submitted]
    conducted_count = len(conducted_sessions)
    session_ids = [s.id for s in sessions]

    all_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.session_id.in_(session_ids)
    ).all() if session_ids else []

    record_lookup = {(r.student_id, r.session_id): r for r in all_records}
    half_weight = settings.half_day_weight if settings.allow_half_day else 0.0

    # 3. Data Rows
    data_start_row = table_header_row + 1
    r_idx = data_start_row

    for st in students:
        ws.cell(row=r_idx, column=1, value=st.roll_number).font = data_font
        ws.cell(row=r_idx, column=1).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r_idx, column=2, value=st.full_name).font = data_font
        ws.cell(row=r_idx, column=2).alignment = Alignment(horizontal="left", vertical="center")

        p_count = 0
        a_count = 0
        hd_count = 0

        for s in sessions:
            c_idx = session_col_map[s.id]
            cell = ws.cell(row=r_idx, column=c_idx)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = data_font
            cell.border = thin_border

            if s.status == SessionStatus.CANCELLED:
                cell.value = "C"
                cell.fill = zebra_fill
            elif s.status == SessionStatus.HOLIDAY:
                cell.value = "H"
                cell.fill = zebra_fill
            elif s.status == SessionStatus.CONDUCTED:
                rec = record_lookup.get((st.id, s.id))
                if rec:
                    if rec.status == AttendanceStatus.PRESENT:
                        cell.value = "P"
                        cell.fill = present_fill
                        p_count += 1
                    elif rec.status == AttendanceStatus.ABSENT:
                        cell.value = "A"
                        cell.fill = absent_fill
                        a_count += 1
                    elif rec.status == AttendanceStatus.HALF_DAY:
                        cell.value = "HD"
                        cell.fill = halfday_fill
                        hd_count += 1
                else:
                    cell.value = "-"
            else:
                cell.value = "-"

        # Total calculations
        st_attended = float(p_count) + (float(hd_count) * half_weight)
        pct = calculate_percentage(st_attended, conducted_count)

        summary_col_start = len(sessions) + 3
        # Conducted
        c_cell = ws.cell(row=r_idx, column=summary_col_start, value=conducted_count)
        c_cell.alignment = Alignment(horizontal="center", vertical="center")
        c_cell.font = data_font
        c_cell.border = thin_border
        
        # Attended
        att_cell = ws.cell(row=r_idx, column=summary_col_start + 1, value=st_attended)
        att_cell.alignment = Alignment(horizontal="center", vertical="center")
        att_cell.font = data_font
        att_cell.border = thin_border

        # Absent
        abs_cell = ws.cell(row=r_idx, column=summary_col_start + 2, value=a_count)
        abs_cell.alignment = Alignment(horizontal="center", vertical="center")
        abs_cell.font = data_font
        abs_cell.border = thin_border

        # Percentage
        pct_cell = ws.cell(row=r_idx, column=summary_col_start + 3)
        pct_cell.alignment = Alignment(horizontal="center", vertical="center")
        pct_cell.border = thin_border
        if pct is not None:
            pct_cell.value = f"{pct}%"
            if pct < settings.default_attendance_threshold:
                pct_cell.font = Font(name="Calibri", size=10, bold=True, color="DC2626")
            else:
                pct_cell.font = Font(name="Calibri", size=10, bold=True, color="16A34A")
        else:
            pct_cell.value = "N/A"
            pct_cell.font = summary_font

        ws.cell(row=r_idx, column=1).border = thin_border
        ws.cell(row=r_idx, column=2).border = thin_border

        r_idx += 1

    # 4. Legend below data
    legend_row = r_idx + 2
    ws.cell(row=legend_row, column=1, value="Legend:").font = subtitle_font
    legends = [
        ("P", "Present (1.0)"),
        ("A", "Absent (0.0)"),
        ("HD", f"Half-Day ({half_weight})"),
        ("H", "Holiday (Not Counted)"),
        ("C", "Cancelled (Not Counted)")
    ]
    leg_col = 2
    for code, desc in legends:
        ws.cell(row=legend_row, column=leg_col, value=f"{code} = {desc}").font = data_font
        leg_col += 2

    # Column Auto-Width adjustments
    ws.column_dimensions['A'].width = 16
    ws.column_dimensions['B'].width = 26
    for c in range(3, col_idx):
        col_letter = get_column_letter(c)
        ws.column_dimensions[col_letter].width = 12

    # Filename generation
    # e.g., attendance_CSE_A_Data_Structures_October_2026.xlsx
    class_part = f"{classroom.name}_{classroom.section}"
    subject_part = subject.name
    date_part = start_date.strftime("%B_%Y") if start_date else classroom.academic_year
    raw_filename = f"attendance_{class_part}_{subject_part}_{date_part}.xlsx"
    filename = sanitize_filename(raw_filename)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output, filename
