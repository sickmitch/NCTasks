#!/usr/bin/env python3

import sys
import os
from datetime import datetime

ICS_FILE = os.path.expanduser("~/.config/nctasks/mod_task.ics")

########### ICS OPERATIONS
def read_ics():
    """Read the content of the ICS file, or return an empty list if file is missing."""
    if not os.path.exists(ICS_FILE):
        return []
    with open(ICS_FILE, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_ics(lines):
    """Write back modified content to the ICS file."""
    with open(ICS_FILE, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def set_ics_field(lines, field, value):
    """Modify or add a specific field (like STATUS, DUE, PRIORITY) in the file."""
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{field}:"):
            new_lines.append(f"{field}:{value}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{field}:{value}\n")  # Add field if it didn't exist
    return new_lines

def get_ics_field(lines, field):
    """Get the value of a specific field."""
    for line in lines:
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip()
    return None

########### WALK
def handle_walk():
    lines = read_ics()
    pre_status = get_ics_field(lines, "STATUS")
    if pre_status == "NEEDS-ACTION":
        status_to_set = "IN-PROCESS"
    elif pre_status == "IN-PROCESS":
        delete_task()
        return
    else:
        status_to_set = "NEEDS-ACTION"  # Default fallback if status is unknown/missing

    updated_lines = set_ics_field(lines, "STATUS", status_to_set)
    write_ics(updated_lines)

########### STATUS
def handle_status(value):
    """Directly set STATUS to the given value."""
    lines = read_ics()
    if value == "To Do":
        status_to_set = "NEEDS-ACTION"
    elif value == "In Process":
        status_to_set = "IN-PROCESS"

    updated_lines = set_ics_field(lines, "STATUS", status_to_set)
    write_ics(updated_lines)

########### DUE
def handle_due(value):
    """Set DUE date, replacing existing or inserting as 3rd from bottom if missing."""
    italian_months = {
        "gen": "Jan",
        "feb": "Feb",
        "mar": "Mar",
        "apr": "Apr",
        "mag": "May",
        "giu": "Jun",
        "lug": "Jul",
        "ago": "Aug",
        "set": "Sep",
        "ott": "Oct",
        "nov": "Nov",
        "dic": "Dec"
    }
    lines = read_ics()
    due_date = value
    # If due_date is valid (not None or 'none'), format it.
    if due_date and due_date.lower() != 'none':
        try:
            day, month_ita = due_date.split()
            month = italian_months.get(month_ita.lower(), month_ita)
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            due_month = datetime.strptime(month, "%b").month
            due_year = current_year if due_month >= current_month else current_year + 1
            # Format to 'YYYYMMDDT235959'
            due_date_formatted = datetime.strptime(f"{day} {month} {due_year}", "%d %b %Y").strftime('%Y%m%dT235959')
        except ValueError:
            print("Invalid due date format. Use '<day> <month>' or 'None'.")
            sys.exit(1)
    else:
        due_date_formatted = None

    updated_lines = []
    due_found = False
    # Process lines - replace DUE if found
    for line in lines:
        if line.startswith('DUE:'):
            if due_date_formatted:
                updated_lines.append(f'DUE:{due_date_formatted}\n')
            due_found = True
        else:
            updated_lines.append(line)
    # If DUE was not found and due_date is valid, insert it at 3rd from the bottom
    if not due_found and due_date_formatted:
        insert_position = max(0, len(updated_lines) - 2)  # 3rd from bottom
        updated_lines.insert(insert_position, f'DUE:{due_date_formatted}\n')
    # If due_date is None or 'none', remove existing DUE
    if due_date_formatted is None:
        updated_lines = [line for line in updated_lines if not line.startswith('DUE:')]
    write_ics(updated_lines)

########### PRIO
def handle_prio(value):
    priority_mapping = {
        "Low": "9",
        "Medium": "5",
        "High": "1"
    }
    priority = priority_mapping.get(value, None)
    if priority is None:
        priority = "9"
    lines = read_ics()

    updated_lines = set_ics_field(lines, "PRIORITY", priority)
    write_ics(updated_lines)

########### SUMMARY
def handle_summary(value):
    lines = read_ics()

    updated_lines = set_ics_field(lines, "SUMMARY", value)
    write_ics(updated_lines)

########### DELETE
def delete_task():
    sys.exit(4)

########### MAIN
def main():
    action = sys.argv[1]
    print(action)
    if action == "walk":
        handle_walk()
    elif action == "status":
        if len(sys.argv) == 3:
            handle_status(sys.argv[2])
    elif action == "due":
        if len(sys.argv) == 3:
            handle_due(sys.argv[2])
    elif action == "prio":
        if len(sys.argv) == 3:
            handle_prio(sys.argv[2])
    elif action == "summary":
        if len(sys.argv) == 3:
            handle_summary(sys.argv[2])
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
