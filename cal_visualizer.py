#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from icalendar import Calendar
from datetime import datetime

# Define the XML namespaces found in Nextcloud's CalDAV responses
NAMESPACES = {
    'd': 'DAV:',
    'cal': 'urn:ietf:params:xml:ns:caldav',
    'oc': 'http://owncloud.org/ns',
    'nc': 'http://nextcloud.org/ns'
}

def parse_xml(source):
    """Parse the XML input from a file or sys.stdin."""
    try:
        tree = ET.parse(source)
    except Exception as e:
        sys.exit(f"Error parsing XML: {e}")
    return tree.getroot()

def extract_tasks(root):
    """Extract VTODO (task) components from calendar-data elements in the XML."""
    tasks = []
    responses = root.findall('d:response', NAMESPACES)
    for resp in responses:
        cal_data_elem = resp.find('.//cal:calendar-data', NAMESPACES)
        if cal_data_elem is not None and cal_data_elem.text:
            ical_data = cal_data_elem.text
            try:
                cal = Calendar.from_ical(ical_data)
                for component in cal.walk():
                    if component.name == "VTODO":
                        task = {
                            'uid': component.get('UID', 'N/A'),
                            'summary': component.get('SUMMARY', 'N/A'),
                            'due': due_parse(str(component.get('DUE', '00'))),
                            'status': status_form(str(component.get('STATUS', 'N/A'))),
                            'dtstamp': component.get('DTSTAMP', 'N/A'),
                            'priority': priority_to_string(str(component.get('PRIORITY', 'N/A'))),
                            'related_to': component.get('RELATED-TO', 'N/A') 
                        }
                        tasks.append(task)
            except Exception as e:
                print(f"Error parsing iCalendar data: {e}", file=sys.stderr)
    
    return tasks

""""Parse status"""
def status_form (status):
    if status == 'IN-PROCESS':
        return 'In Process'
    elif status == 'CANCELLED':
        return 'Cancelled'
    elif status == 'NEEDS-ACTION':
        return 'To Do'
    elif status == 'COMPLETED':
        return 'Completed'
    else:
        return status

def format_datetime(dt):
    """Convert a datetime object to a string, if needed."""
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, str) and 'vDDDTypes' in dt:
        # Extract the date from the vDDDTypes format
        return dt.split('(')[1].split(',')[0].strip()  # Extract the date part
    return str(dt)  # Fallback for other types

def priority_to_string(priority):
    """Convert numeric priority to string representation."""
    if priority == '0':
        return 'Not Assigned'
    elif priority in ['1', '2', '3', '4']:
        return 'High'
    elif priority == '5':
        return 'Medium'
    elif priority in ['6', '7', '8', '9']:
        return 'Low'
    return 'Err'  # Default case for unexpected values

def due_parse(due):
    import re
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', due)
    if match:
        return f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    return due

def visualize_tasks(tasks):
    """Print out tasks in a table format with indentation for related tasks, sorted by due date and priority."""
    if not tasks:
        print("No tasks found.")
        return

    # Convert due date to datetime object for sorting
    def parse_due_date(due):
        if due == '00' or due is None:
            return datetime.max  # Treat unset due dates as far future
        try:
            return datetime.strptime(due, "%d-%m-%Y")
        except ValueError:    
            footer = "{:<30}  {:<20}  {:<15}  {:<10}".format("Task", "Due", "Status", "Priority")
            separator = "-" * len(footer)
            print(footer)
            print(separator)
            return datetime.max  # Fallback in case of parsing errors

    # Map priority to numeric values for sorting
    def priority_value(priority):
        priority_map = {"High": 1, "Medium": 2, "Low": 3, "Not Assigned": 4}
        return priority_map.get(priority, 4)  # Default to lowest priority

    # Sort tasks by due date first, then by priority
    tasks.sort(key=lambda task: (parse_due_date(task['due']), priority_value(task['priority'])))

    # Create a mapping of task UIDs to their corresponding tasks
    task_map = {task['uid']: task for task in tasks}

    # Build a hierarchy (parent → list of children)
    parent_child_map = {}
    root_tasks = []

    for task in tasks:
        parent_uid = task.get('related_to', 'N/A').split(":")[-1]  # Extract UID after "RELATED-TO;RELTYPE=PARENT:"
        if parent_uid in task_map:  # It's a child task
            parent_child_map.setdefault(parent_uid, []).append(task)
        else:  # It's a root-level task
            root_tasks.append(task)

    # Sort children for each parent
    for parent_uid in parent_child_map:
        parent_child_map[parent_uid].sort(key=lambda task: (parse_due_date(task['due']), priority_value(task['priority'])))

    # Function to print tasks recursively
    def print_task(task, indent_level=0):
        indent = " " * 2 * indent_level  # ICONE QUI
        summary = indent + task.get('summary', 'N/A')
        due = task.get('due')
        status = task.get('status')
        priority = task.get('priority')

        print(f"{summary:<30}  {due:<20}  {status:<15}  {priority:<10}")

        # Print child tasks (if any)
        for child in parent_child_map.get(task['uid'], []):
            print_task(child, indent_level + 1)

    # Print root tasks and their children recursively
    for task in root_tasks:
        print_task(task)

    # Print footer
    footer = "{:<30}  {:<20}  {:<15}  {:<10}".format("Task", "Due", "Status", "Priority")
    separator = "New Task  " + "-" * (len(footer) - 15 ) 
    print(separator)
    print(footer)

def main():
    # Read XML from a file passed as an argument or from standard input
    if len(sys.argv) > 1:
        xml_source = sys.argv[1]
        root = parse_xml(xml_source)
    else:
        root = parse_xml(sys.stdin)
    
    tasks = extract_tasks(root)
    # Create a mapping of task UIDs to their corresponding tasks
    task_map = {task['uid']: task for task in tasks}

    visualize_tasks(tasks)

if __name__ == '__main__':
    main()

