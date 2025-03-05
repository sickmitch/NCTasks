#!/bin/bash

# source var
source ~/.config/nctasks/.env
##### !!!!! #####
# need to assign $user $api_key $base_url $root if not using .env
cal_url=$base_url/remote.php/dav/calendars/$user/personal

# cleanup
rm ~/.cache/wofi-dmenu
rm $root/tasks
rm $root/*.ics

wofi_cmd="wofi --height=400 --width=700 -n -s /home/$user/.config/nctasks/wofi_nctasks.css --show=dmenu --prompt"
wofi_cal_cmd="wofi --height=400 --width=700 --columns=7 -n -s /home/$user/.config/nctasks/wofi_nctasks.css --show=dmenu --prompt"

### REUSABLE WOFIS
wofi_cal() {
    # Define start and end dates (GNU date is assumed)
    start=$(date -d "tomorrow" +%Y-%m-%d)
    end=$(date -d "+2 months" +%Y-%m-%d)
    end_year=$(date -d "+2 months" +%Y)
    current_year=$(date -d "$current" +%Y)
    if [ $current_year -ne $end_year ]; then
        end=$(date -d "next year" +%Y-%m-%d)
    fi
    current="$start"
    dates="$(for i in {0..6}; do date -d "yesterday +$i days" +%A; done)"
    dates+=$'\n'"None"$'\n'"Today"$'\n'
    # Loop through each day until the end date
    while [ "$(date -d "$current" +%Y%m%d)" -le "$(date -d "$end" +%Y%m%d)" ]; do
        # Format each date as "DD MMM" (e.g. "05 Mar")
        dates+=$(date -d "$current" '+%d %b')
        current=$(date -I -d "$current + 1 day")
        if [ "$(date -d "$current" +%Y%m%d)" -le "$(date -d "$end" +%Y%m%d)" ]; then
            dates+=$'\n'
        fi
    done
    echo "$dates" | $wofi_cal_cmd "Select date:"
}
wofi_status() {
    status="To Do\nIn Process"
    echo -e "$status" | $wofi_cmd "Select status:"
}
wofi_prio() {
    status="Low\nMedium\nHigh"
    echo -e "$status" | $wofi_cmd "Select priority:"
}

### MOD TASK
mod_task() {
    case "$1" in
        walk)
            python3 $root/mod_task.py walk
            if [ $? == 4 ]; then
                delete_task
            fi
            ;;
        status)
            STATUS_TO_SET=$(wofi_status)
            python3 $root/mod_task.py status "$STATUS_TO_SET"
            ;;
        due)
            DUE_TO_SET=$(wofi_cal)
            python3 $root/mod_task.py due "$DUE_TO_SET"
            ;;
        prio)
            PRIO_TO_SET=$(wofi_prio)
            python3 $root/mod_task.py prio "$PRIO_TO_SET"
            ;;
        summary)
            SUM_TO_SET=$(echo "Insert the new summary" | $wofi_cmd "Input new summary here")
            python3 $root/mod_task.py summary "$SUM_TO_SET"
            ;;
        *)
            echo "Something went wrong" | $wofi_cmd ":("
            ;;
    esac
    # Extract ETag from previous response (to handle concurrency)
    ETAG=$(grep -B5 "$N" "$root/tasks" | grep "<d:getetag>" | sed -E 's|.*<d:getetag>(.*)</d:getetag>.*|\1|')
    # Update the modified task
    curl -X PUT -u "$user:$api_key" \
        -H "Content-Type: text/calendar" \
        --data-binary @$root/mod_task.ics \
        $TASK_URL
}

### DEL TASK
delete_task(){
    curl -v --user "$user:$api_key" -X DELETE $TASK_URL
    exit 0
}

### NEW TASK
new_task() {
    new_task_sum=$(echo "Insert a name for the new task" | $wofi_cmd "Input a summary here")
    if [ -z "$new_task_sum" ] || [ "$new_task_sum" = "Insert a name for the new task" ]; then
        exit 0
    fi
    new_task_due=$(wofi_cal)
    if [ -z "$new_task_due" ]; then
        exit 0
    fi
    new_task_prio=$(wofi_prio)
    if [ -z "$new_task_prio" ]; then
        exit 0
    fi
    new_task_status=$(wofi_status)
    if [ -z "$new_task_status" ]; then
        exit 0
    fi
    # Generate the new task .ics file and get the unique ID to send it
    if [ "$1" = "secondary" ]; then
        new_task_uid=$(python3 $root/new_task.py "$new_task_sum" "$new_task_due" "$new_task_prio" "$new_task_status" "$1" "$N")
    else
        new_task_uid=$(python3 $root/new_task.py "$new_task_sum" "$new_task_due" "$new_task_prio" "$new_task_status")
    fi
    # Send it
    curl -v --user "$user:$api_key" \
    -H "Content-Type: text/calendar" -X PUT \
    --data-binary @"$root/$new_task_uid.ics" "$cal_url/$new_task_uid.ics"
    exit 0
}

### ACTION SELECTOR
action_selector () {
    # Get UID of selected task
    line_number=$(echo $SELECTED_TASK | sed 's/ [0-9][0-9].*$//' | grep -n -f - $root/tasks | cut -d: -f1) # Find the task from the summary
    N=$(awk -v line=$line_number 'NR<=line { if ($0 ~ /^UID:/) uid=$0 } END { if (uid) print uid }' $root/tasks | cut -d':' -f2) # Crawl up to find UID and assign to N
    ### N è Task UID
    TASK_URL="$base_url$(grep -B5 "$N" "$root/tasks" | grep "<d:href>" | sed -E 's|.*<d:href>(.*)</d:href>.*|\1|')" # Get URL of the .ics for the task
    curl -u "$user:$api_key" -X GET $TASK_URL > $root/mod_task.ics # Get only the task to modify

    ACTION=$(echo -e "Progress status\nAdd a secondary task\nAdd or change status\nAdd or change due\nAdd or change priority\nChange summary\nRemove task" | $wofi_cmd "Select the action to make")
    case "$ACTION" in
        "Progress status")
            mod_task walk
            ;;
        "Add a secondary task")
            new_task secondary
            ;;
        "Add or change status")
            mod_task status
            ;;
        "Add or change due")
            mod_task due
            ;;
        "Add or change priority")
            mod_task prio
            ;;
        "Change summary")
            mod_task summary
            ;;
        "Remove task")
            delete_task
            ;;
        *)
            echo "Something went wrong" | $wofi_cmd ":("
            ;;
    esac
}

##### MAIN ######
# Get updated tasks 
curl -v -u $user:$api_key -X PROPFIND \
-H "Depth: 1" \
-H "Content-Type: application/xml" \
"$cal_url" \
-d '<?xml version="1.0" encoding="UTF-8"?>
    <d:propfind xmlns:d="DAV:" xmlns:cal="urn:ietf:params:xml:ns:caldav">
        <d:prop>
            <d:getetag/>
            <cal:calendar-data/>
        </d:prop>
    </d:propfind>' \
> $root/tasks

# Visualize tasks into a Wofi menu
SELECTED_TASK=$($root/cal_visualizer.py $root/tasks | $wofi_cmd "Oggi è $(date +'%A %d %B')")
if [ -z "$SELECTED_TASK" ]; then
    exit 0
fi
echo $SELECTED_TASK
# add a command which takes $SELECTED_TASK and cuts the beginning of the string until it reaches an alphabet character
SELECTED_TASK=$(echo "$SELECTED_TASK" | sed 's/^[^a-zA-Z]*//')

# Grep into $SELECTED_TASK for the string "New Task" and pass a command if present
if echo "$SELECTED_TASK" | grep -q "New Task"; then
    new_task
else
    action_selector
fi


exit 0
