#!/usr/bin/env python3

import sys
import os

ICS_FILE = os.path.expanduser("~/.config/nctasks/mod_task.ics")

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

def handle_walk():
    """Walk logic - toggle STATUS between NEEDS-ACTION and IN-PROCESS, or delete the task."""
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

def handle_status(value):
    """Directly set STATUS to the given value."""
    lines = read_ics()
    if value == "To-do":
        status_to_set = "NEEDS-ACTION"
    elif value == "In-Progress":
        status_to_set = "IN-PROCESS"

    updated_lines = set_ics_field(lines, "STATUS", status_to_set)
    write_ics(updated_lines)

def handle_due(value):
    """Set DUE date."""
    lines = read_ics()
    updated_lines = set_ics_field(lines, "DUE", value)
    write_ics(updated_lines)

def handle_prio(value):
    """Set PRIORITY."""
    lines = read_ics()
    updated_lines = set_ics_field(lines, "PRIORITY", value)
    write_ics(updated_lines)

def delete_task():
    sys.exit(4)

def main():

    action = sys.argv[1]

    if action == "walk":
        print(len(sys.argv))
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
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
