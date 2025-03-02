import sys
from datetime import datetime

# Check for correct number of arguments
if len(sys.argv) != 5:
    print("Usage: python3 script.py <SUMMARY> <DUE> <PRIORITY> <STATUS>")
    sys.exit(1)

# Command-line arguments
summary = sys.argv[1]
due_date = sys.argv[2]
priority = sys.argv[3]
status = sys.argv[4]

# Update status and priority based on the conversions needed
status_map = {
    "To Do": "NEEDS-ACTION",
    "In Process": "IN-PROCESS",
    "Completed": "COMPLETED"
}

priority_map = {
    "High": 1,
    "Medium": 5,
    "Low": 9
}

status = status_map.get(status, status)
priority = priority_map.get(priority, priority)

# Generate timestamps
def get_current_timestamp():
    return datetime.now().strftime('%Y%m%dT%H%M%SZ')

created = get_current_timestamp()
last_modified = get_current_timestamp()
dtstamp = get_current_timestamp()

# Read template path
template_path = '/home/mike/.config/nctasks/new_task_templ'

try:
    with open(template_path, 'r') as file:
        template_lines = file.readlines()
except FileNotFoundError:
    print(f"Template file not found at {template_path}")
    sys.exit(1)

# Convert Italian month abbreviation to English
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

# Process due_date
if due_date and due_date.lower() != 'none':
    try:
        day, month_ita = due_date.split()
        month = italian_months.get(month_ita.lower(), month_ita)

        # Get the current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year

        # Calculate the due month and year
        due_month = datetime.strptime(month, "%b").month
        due_year = current_year if due_month >= current_month else current_year + 1

        # Format due_date with end-of-day time
        due_date = datetime.strptime(f"{day} {month} {due_year}", "%d %b %Y").strftime('%Y%m%dT235959')

        template_lines = [line.replace('DUE:', f'DUE:{due_date}') if 'DUE:' in line else line for line in template_lines]
    except ValueError:
        print("Invalid due date format. Use '<day> <month>' or 'None'.")
        sys.exit(1)
else:
    template_lines = [line for line in template_lines if 'DUE:' not in line]

# Replace placeholders
template_lines = [line.replace('CREATED:', f'CREATED:{created}') for line in template_lines]
template_lines = [line.replace('LAST-MODIFIED:', f'LAST-MODIFIED:{last_modified}') for line in template_lines]
template_lines = [line.replace('DTSTAMP:', f'DTSTAMP:{dtstamp}') for line in template_lines]
template_lines = [line.replace('SUMMARY:', f'SUMMARY:{summary}') for line in template_lines]
template_lines = [line.replace('PRIORITY:', f'PRIORITY:{priority}') for line in template_lines]
template_lines = [line.replace('STATUS:', f'STATUS:{status}') for line in template_lines]

# Generate unique UID
uid = f"{int(datetime.now().timestamp())}@nctasks"
template_lines = [line.replace('UID:', f'UID:{uid}') for line in template_lines]

# Write to new file
output_path = f'/home/mike/.config/nctasks/{uid}.ics'
with open(output_path, 'w') as file:
    file.writelines(template_lines)

print(f"{uid}")



# import sys
# from datetime import datetime

# # Check for correct number of arguments
# if len(sys.argv) != 5:
#     print("Usage: python3 script.py <SUMMARY> <DUE> <PRIORITY> <STATUS>")
#     sys.exit(1)

# # Command-line arguments
# summary = sys.argv[1]
# due_date = sys.argv[2]
# priority = sys.argv[3]
# status = sys.argv[4]

# # Update status and priority based on the conversions needed
# status_map = {
#     "To Do": "NEEDS-ACTION",
#     "In Process": "IN-PROCESS",
#     "Completed": "COMPLETED"
# }

# priority_map = {
#     "High": 1,
#     "Medium": 5,
#     "Low": 9
# }

# status = status_map.get(status, status)
# priority = priority_map.get(priority, priority)

# # Generate timestamps
# def get_current_timestamp():
#     return datetime.now().strftime('%Y%m%dT%H%M%SZ')

# created = get_current_timestamp()
# last_modified = get_current_timestamp()
# dtstamp = get_current_timestamp()

# # Read template path
# template_path = '/home/mike/.config/nctasks/new_task_templ'

# try:
#     with open(template_path, 'r') as file:
#         template_lines = file.readlines()
# except FileNotFoundError:
#     print(f"Template file not found at {template_path}")
#     sys.exit(1)

# # Convert Italian month abbreviation to English
# italian_months = {
#     "gen": "Jan",
#     "feb": "Feb",
#     "mar": "Mar",
#     "apr": "Apr",
#     "mag": "May",
#     "giu": "Jun",
#     "lug": "Jul",
#     "ago": "Aug",
#     "set": "Sep",
#     "ott": "Oct",
#     "nov": "Nov",
#     "dic": "Dec"
# }

# # Process due_date
# if due_date and due_date.lower() != 'none':
#     try:
#         day, month_ita = due_date.split()
#         month = italian_months.get(month_ita.lower(), month_ita)

#         # Get the current month and year
#         current_month = datetime.now().month
#         current_year = datetime.now().year

#         # Calculate the due month and year
#         due_month = datetime.strptime(month, "%b").month
#         due_year = current_year if due_month >= current_month else current_year + 1

#         due_date = datetime.strptime(f"{day} {month} {due_year}", "%d %b %Y").strftime('%Y%m%dT%H%M%S')
#         due_date += "T235959"  # Placeholder for the time part

#         template_lines = [line.replace('DUE:', f'DUE:{due_date}') if 'DUE:' in line else line for line in template_lines]
#     except ValueError:
#         print("Invalid due date format. Use '<day> <month>' or 'None'.")
#         sys.exit(1)
# else:
#     template_lines = [line for line in template_lines if 'DUE:' not in line]

# # Replace placeholders
# template_lines = [line.replace('CREATED:', f'CREATED:{created}') for line in template_lines]
# template_lines = [line.replace('LAST-MODIFIED:', f'LAST-MODIFIED:{last_modified}') for line in template_lines]
# template_lines = [line.replace('DTSTAMP:', f'DTSTAMP:{dtstamp}') for line in template_lines]
# template_lines = [line.replace('SUMMARY:', f'SUMMARY:{summary}') for line in template_lines]
# template_lines = [line.replace('PRIORITY:', f'PRIORITY:{priority}') for line in template_lines]
# template_lines = [line.replace('STATUS:', f'STATUS:{status}') for line in template_lines]

# # Generate unique UID
# uid = f"{int(datetime.now().timestamp())}@nctasks"
# template_lines = [line.replace('UID:', f'UID:{uid}') for line in template_lines]

# # Write to new file
# output_path = f'/home/mike/.config/nctasks/{uid}.ics'
# with open(output_path, 'w') as file:
#     file.writelines(template_lines)

# print(f"{uid}")


