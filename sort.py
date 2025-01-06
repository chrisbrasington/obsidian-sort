#!/usr/bin/env python3
import os
import re
import curses

# DIRECTORY = os.path.expanduser("~/obsidian/brain/03 - Resources/Video Games/Playing")
# DIRECTORY = os.path.expanduser("~/obsidian/brain/03 - Resources/Manga/Reading")
DIRECTORY = os.path.expanduser("~/obsidian/brain/03 - Resources/Video Games/Backlog")
PAGE_SIZE = 100
SORT_REGEX = r"^sort:\s*(-?\d+(\.\d+)?)"

def read_markdown_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith(".md"):
            # if file contains 'hltb: ∞' in contents, ignore
            with open(os.path.join(directory, file), "r") as f:
                if "hltb: ∞" in f.read():
                    continue
            files.append(os.path.join(directory, file))
    return files

def extract_sort_values(files):
    entries = []
    for file in files:
        sort_value = None
        with open(file, "r") as f:
            for line in f:
                match = re.match(SORT_REGEX, line)
                if match:
                    sort_value = float(match.group(1))
                    break
        entries.append({"file": file, "sort": sort_value})

    entries.sort(key=lambda x: (x["sort"] if x["sort"] is not None else float('inf'), os.path.basename(x["file"])))
    return entries

def write_sort_value(file, sort_value):
    lines = []
    sort_written = False
    with open(file, "r") as f:
        for line in f:
            if re.match(SORT_REGEX, line):
                lines.append(f"sort: {sort_value}\n")
                sort_written = True
            else:
                lines.append(line)

    if not sort_written:
        lines.insert(0, f"sort: {sort_value}\n")

    with open(file, "w") as f:
        f.writelines(lines)

def resort_all(entries):
    increment = 10
    current_value = 0
    for entry in entries:
        if entry['sort'] is not None:  # Include entries with 0, exclude None
            entry['sort'] = current_value
            write_sort_value(entry['file'], current_value)
            current_value += increment

def main(stdscr):
    curses.curs_set(0)
    # Get the current terminal height and adjust PAGE_SIZE accordingly
    terminal_height, _ = stdscr.getmaxyx()
    global PAGE_SIZE
    PAGE_SIZE = min(PAGE_SIZE, terminal_height - 4)  # Reserve space for status line and other elements

    files = read_markdown_files(DIRECTORY)
    entries = extract_sort_values(files)

    current_page = 0
    selected_index = 0
    moving_mode = False
    original_index = None

    while True:
        stdscr.clear()
        start_index = current_page * PAGE_SIZE
        end_index = min(start_index + PAGE_SIZE, len(entries))

        total_pages = (len(entries) - 1) // PAGE_SIZE + 1
        stdscr.addstr(PAGE_SIZE + 2, 0, f"Page {current_page + 1}/{total_pages}")

        for i in range(start_index, end_index):
            entry = entries[i]
            display_text = f"{entry['sort'] if entry['sort'] is not None else 'None':>6} {os.path.basename(entry['file'])}"
            if i == selected_index:
                stdscr.addstr(i - start_index, 0, display_text, curses.A_REVERSE)
            else:
                stdscr.addstr(i - start_index, 0, display_text)

        if moving_mode:
            stdscr.addstr(PAGE_SIZE + 1, 0, "Moving mode: Use arrow keys to reposition, Enter to commit.")
        else:
            stdscr.addstr(PAGE_SIZE + 1, 0, "Press Enter to move, 'i' to input a number, '<'/'>' to navigate pages, 'a' to resort, 'q' to quit.")

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            if moving_mode:
                selected_index = max(selected_index - 1, 0)
            else:
                selected_index = max(selected_index - 1, 0)
        elif key == curses.KEY_DOWN:
            if moving_mode:
                selected_index = min(selected_index + 1, len(entries) - 1)
            else:
                selected_index = min(selected_index + 1, len(entries) - 1)
        elif key == ord(','): # < key
            if not moving_mode:
                current_page = max(current_page - 1, 0)
                selected_index = max(selected_index, current_page * PAGE_SIZE)
        elif key == ord('.'): # > key
            if not moving_mode:
                max_page = (len(entries) - 1) // PAGE_SIZE
                current_page = min(current_page + 1, max_page)
                selected_index = min(selected_index, (current_page + 1) * PAGE_SIZE - 1)
        elif key == ord('i') and not moving_mode:
            entry = entries[selected_index]
            stdscr.addstr(PAGE_SIZE + 3, 0, f"Enter new sort value for {os.path.basename(entry['file'])}: ")
            curses.echo()
            new_sort = stdscr.getstr(PAGE_SIZE + 4, 0).decode("utf-8")
            curses.noecho()

            try:
                new_sort = float(new_sort)
                entry['sort'] = new_sort
                write_sort_value(entry['file'], new_sort)
                entries.sort(key=lambda x: (x['sort'] if x['sort'] is not None else float('inf'), os.path.basename(x['file'])))
            except ValueError:
                stdscr.addstr(PAGE_SIZE + 5, 0, "Invalid input. Press any key to continue.")
                stdscr.getch()
        elif key == ord('d'):
            # remove the sort line from the file, save file, and refresh
            entry = entries[selected_index]
            with open(entry['file'], "r") as f:
                lines = f.readlines()
            with open(entry['file'], "w") as f:
                for line in lines:
                    if not re.match(SORT_REGEX, line):
                        f.write(line)
            entries = extract_sort_values(files)
            selected_index = min(selected_index, len(entries) - 1)
        elif key == 10:  # Enter key
            if moving_mode:
                moving_mode = False
                target_index = selected_index
                original_entry = entries[original_index]

                # Determine bounds for new sort value
                if target_index == 0:  # Moved to the top of the list
                    lower_bound = 0
                    new_sort = lower_bound - 10
                elif target_index == len(entries):  # Moved to the end of the list
                    lower_bound = entries[-1]['sort'] or 0
                    new_sort = lower_bound + 10
                else:  # Moved between two entries
                    lower_bound = entries[target_index - 1]['sort'] or 0
                    upper_bound = entries[target_index]['sort'] or (lower_bound + 10)
                    new_sort = (lower_bound + upper_bound) / 2

                # Update sort value of the moved entry
                original_entry['sort'] = new_sort
                write_sort_value(original_entry['file'], new_sort)

                # Re-sort entries after modification
                entries.sort(key=lambda x: (x['sort'] if x['sort'] is not None else float('inf'), os.path.basename(x['file'])))
            else:
                moving_mode = True
                original_index = selected_index
        elif key == ord('a'):
            resort_all(entries)
            entries.sort(key=lambda x: (x['sort'] if x['sort'] is not None else float('inf'), os.path.basename(x['file'])))
        elif key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
