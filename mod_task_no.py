import sys
from datetime import datetime



def main():
    if len(sys.argv) < 3:
        if len(sys.argv) == 2 and sys.argv[1] == "walk":
            argument = ""
        else:
            print("Usage: python mod_task.py <route> <argument>")
            sys.exit(1)
    
    path = '/home/mike/.config/nctasks/mod_task.ics'
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

    route = sys.argv[1]
    if route == "walk":
        # Read the file and process the status
        with open(path, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if "STATUS:" in line:
                    pre_status = line.split(":")[1].strip()
                    if pre_status == "NEEDS-ACTION":
                        status_to_set = "IN-PROCESS"
                    elif pre_status == "IN-PROCESS":
                        print("delete")
                        pass
                    else:
                        status_to_set = "NEEDS-ACTION"  # Reset
                    lines[index] = f"STATUS:{status_to_set}\n"
        # Write the updated status back to the file
        with open('mod_task.ics', 'w') as file:
            file.writelines(lines)
            sys.exit(0)


    if route == "due":
        due_date = sys.argv[2]
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

                for index, line in enumerate(path):
                    if 'DUE:' in line:
                        # Update the existing DUE line with the new due_date
                        path[index] = f"DUE:{due_date}\n"
                        break
                else:
                    # Check if path is a string and convert it to a list
                    if isinstance(path, str):
                        path = path.splitlines()
                    # Add a new DUE line with the due_date
                    path.append(f"DUE:{due_date}\n")
                sys.exit(0)
            except ValueError:
                print("Invalid due date format. Use '<day> <month>' or 'None'.")
                sys.exit(1)
    if route == "prio":
        # Implement route 2 logic here
        pass
    print("Invalid route")
    sys.exit(1)


if __name__ == "__main__":
    main()
