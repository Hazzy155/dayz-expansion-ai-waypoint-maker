import tkinter as tk
from tkinter import ttk, messagebox
import re

# --- Global Variables for Clipboard Monitoring ---
is_recording = False
# Stores the last text successfully inserted into the input_text widget
last_recorded_position = "" 

# --- Base config ---
BASE_CONFIG = {
        "Name": "airfield krasno",
        "Persist": 0,
        "Faction": "Mercenaries",
        "Formation": "RANDOM",
        "FormationScale": 0.0,
        "FormationLooseness": 0.0,
        "Loadout": "HumanLoadout",
        "Units": [],
        "NumberOfAI": -3,
        "Behaviour": "ALTERNATE",
        "LootingBehaviour": "",
        "Speed": "WALK",
        "UnderThreatSpeed": "SPRINT",
        "CanBeLooted": 1,
        "UnlimitedReload": 1,
        "SniperProneDistanceThreshold": 0.0,
        "AccuracyMin": -1.0,
        "AccuracyMax": -1.0,
        "ThreatDistanceLimit": -1.0,
        "NoiseInvestigationDistanceLimit": -1.0,
        "DamageMultiplier": -1.0,
        "DamageReceivedMultiplier": -1.0,
        "CanBeTriggeredByAI": 0,
        "MinDistRadius": -1.0,
        "MaxDistRadius": -1.0,
        "DespawnRadius": -1.0,
        "MinSpreadRadius": 0,
        "MaxSpreadRadius": 0,
        "Chance": 1.0,
        "DespawnTime": -1.0,
        "RespawnTime": -2.0,
        "LoadBalancingCategory": "",
        "ObjectClassName": "",
        "WaypointInterpolation": "",
        "UseRandomWaypointAsStartPoint": 1, # Default value
        "Waypoints": []
}

FACTIONS = [
    "West", "East", "Raiders", "Mercenaries", "Civilian", "Passive", "Guards",
    "InvincibleGuards", "Shamans", "Observers", "InvincibleObservers",
    "YeetBrigade", "InvincibleYeetBrigade", "Brawlers", "RANDOM"
]

BEHAVIOURS = [
    "HALT", "ONCE", "LOOP", "ALTERNATE",
    "HALT_OR_ALTERNATE", "HALT_OR_LOOP", "ROAMING"
]

SPEEDS = [
    "STATIC", "WALK", "JOG", "SPRINT", "RANDOM", "RANDOM_NONSTATIC"
]

UNLIMITED_RELOAD_OPTIONS = {
    "Off": 0,
    "All targets": 1,
    "Animals": 2,
    "Infected": 4,
    "Players": 8,
    "Vehicles": 16
}

def parse_positions(raw_text):
    pos_matches = re.findall(r"Position:\s*<([^>]+)>", raw_text)
    waypoints = []
    for match in pos_matches:
        parts = [p.strip() for p in match.split(",")]
        if len(parts) >= 3:
            try:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                waypoints.append([x, y, z])
            except ValueError:
                continue
    return waypoints

def format_json_dayz(config):
    # Indentation setup (8-space base, 4-space inner steps)
    BASE_INDENT = " " * 8  
    INNER_INDENT = " " * 4  
    WP_ARRAY_INDENT = " " * 4 
    WP_COORD_INDENT = " " * 4 
    
    lines = [f"{BASE_INDENT}{{"]
    keys = list(config.keys())
    
    for i, key in enumerate(keys):
        val = config[key]
        
        if key == "Waypoints":
            # "Waypoints": [ is at 12 spaces (8 + 4)
            lines.append(f'{BASE_INDENT}{INNER_INDENT}"{key}": [')
            
            for j, wp in enumerate(val):
                # Inner waypoint array [ is at 16 spaces (8 + 4 + 4)
                lines.append(f'{BASE_INDENT}{INNER_INDENT}{WP_ARRAY_INDENT}[')
                
                # Waypoint coordinates are at 20 spaces (8 + 4 + 4 + 4)
                lines.append(f'{BASE_INDENT}{INNER_INDENT}{WP_ARRAY_INDENT}{WP_COORD_INDENT}{wp[0]},')
                lines.append(f'{BASE_INDENT}{INNER_INDENT}{WP_ARRAY_INDENT}{WP_COORD_INDENT}{wp[1]},')
                lines.append(f'{BASE_INDENT}{INNER_INDENT}{WP_ARRAY_INDENT}{WP_COORD_INDENT}{wp[2]}')
                
                # Close inner array ] is at 16 spaces
                close_bracket = f'{BASE_INDENT}{INNER_INDENT}{WP_ARRAY_INDENT}]'
                if j < len(val) - 1:
                    close_bracket += ","
                lines.append(close_bracket) 
                
            # Close Waypoints array ] is at 12 spaces
            close_array = f'{BASE_INDENT}{INNER_INDENT}]'
            lines.append(close_array)
            
        else:
            # All regular key-value pairs are at 12 spaces
            comma = ","
            
            if isinstance(val, str):
                lines.append(f'{BASE_INDENT}{INNER_INDENT}"{key}": "{val}"{comma}')
            else:
                value_str = str(val).lower() if isinstance(val, bool) else str(val)
                lines.append(f'{BASE_INDENT}{INNER_INDENT}"{key}": {value_str}{comma}')

    # Close object wrapper } is at 8 spaces, with trailing comma
    lines.append(f"{BASE_INDENT}}},")
    return "\n".join(lines)


def generate_config():
    raw_text = input_text.get("1.0", tk.END)
    name = name_entry.get().strip() or BASE_CONFIG["Name"]
    
    try:
        chance = float(chance_entry.get().strip() or BASE_CONFIG["Chance"])
    except ValueError:
        messagebox.showwarning("Invalid Input", "Chance must be a number.")
        return
        
    can_be_looted = 1 if loot_var.get() else 0
    faction = faction_var.get() or BASE_CONFIG["Faction"]
    loadout = loadout_entry.get().strip() or BASE_CONFIG["Loadout"]
    behaviour = behaviour_var.get() or BASE_CONFIG["Behaviour"]
    speed = speed_var.get() or BASE_CONFIG["Speed"]
    under_threat_speed = uts_var.get() or BASE_CONFIG["UnderThreatSpeed"]
    
    # Read the checkbox state
    use_random_wp = 1 if random_wp_var.get() else 0

    selected_indices = ur_listbox.curselection()
    unlimited_reload = sum(list(UNLIMITED_RELOAD_OPTIONS.values())[i] for i in selected_indices)

    try:
        number_of_ai = int(num_ai_entry.get().strip())
    except ValueError:
        messagebox.showwarning("Invalid Input", "NumberOfAI must be an integer.")
        return

    waypoints = parse_positions(raw_text)
    if not waypoints:
        messagebox.showwarning("No Positions", "No valid Position lines found in input.")
        return

    config = BASE_CONFIG.copy()
    config["Name"] = name
    config["Chance"] = chance
    config["CanBeLooted"] = can_be_looted
    config["Faction"] = faction
    config["Loadout"] = loadout
    config["NumberOfAI"] = number_of_ai
    config["Behaviour"] = behaviour
    config["Speed"] = speed
    config["UnderThreatSpeed"] = under_threat_speed
    config["UnlimitedReload"] = unlimited_reload
    config["UseRandomWaypointAsStartPoint"] = use_random_wp # Apply the checkbox value
    config["Waypoints"] = waypoints

    formatted = format_json_dayz(config)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, formatted)

# --- Clipboard Monitoring Functions ---

def start_clipboard_monitor():
    """Checks the clipboard every 100ms for new position data and inserts it."""
    global last_recorded_position
    global is_recording
    
    if not is_recording:
        return

    current_clipboard = ""
    try:
        # Get and clean the clipboard content
        current_clipboard = root.clipboard_get().strip()
    except tk.TclError:
        pass

    # 1. Check if the clipboard contains valid position data
    is_position_data = re.search(r"Position:\s*<", current_clipboard)

    # 2. Check if the current clipboard content is DIFFERENT from the last one we recorded
    if is_position_data and current_clipboard != last_recorded_position:
        
        # We need to insert a newline only if the textbox isn't currently empty
        if input_text.get("1.0", "end-1c").strip():
            input_text.insert(tk.END, "\n" + current_clipboard)
        else:
            input_text.insert(tk.END, current_clipboard)
            
        # Ensure the text box scrolls to the bottom
        input_text.see(tk.END)
        
        # Update the last recorded position
        last_recorded_position = current_clipboard 
            
    # Schedule the next check in 100 milliseconds (0.1 seconds)
    root.after(100, start_clipboard_monitor)

def toggle_recording():
    """Starts or stops clipboard monitoring and updates the button text."""
    global is_recording
    global last_recorded_position

    is_recording = not is_recording
    
    if is_recording:
        recording_button.config(text="Stop Recording (Active) 🔴", bg="#e34a4a")
        
        # Read the current clipboard on startup to prevent it from being recorded immediately
        current_clipboard = ""
        try:
            current_clipboard = root.clipboard_get().strip()
        except tk.TclError:
            pass
            
        # Set the current clipboard content as the last recorded position
        last_recorded_position = current_clipboard
            
        start_clipboard_monitor()
    else:
        recording_button.config(text="Start Recording", bg="#4a4a4a")

def clear_recording_data():
    """Clears all text from the Paste Position Data area."""
    input_text.delete("1.0", tk.END)
    global last_recorded_position
    last_recorded_position = "" # Reset the last recorded position after clearing

# --- GUI ---
root = tk.Tk()
root.title("DayZ Waypoint Formatter")
root.geometry("1200x750")

# Dark Mode Colors
BG_COLOR = "#2e2e2e"
FG_COLOR = "#e0e0e0"
ENTRY_BG = "#3c3c3c"
ENTRY_FG = "#e0e0e0"
BUTTON_BG = "#4a4a4a"
BUTTON_FG = "#ffffff"
CLEAR_BUTTON_BG = "#5b5b5b"

root.configure(bg=BG_COLOR)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

left_frame = tk.Frame(main_frame, bg=BG_COLOR)
left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
right_frame = tk.Frame(main_frame, bg=BG_COLOR)
right_frame.grid(row=0, column=1, sticky="nsew")

main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=2)
main_frame.grid_rowconfigure(0, weight=1)

# Set a minimum width for the label column to fit the long checkbox text
left_frame.grid_columnconfigure(0, minsize=200)

def create_dark_label(parent, text, row, col):
    label = tk.Label(parent, text=text, bg=BG_COLOR, fg=FG_COLOR)
    label.grid(row=row, column=col, sticky="e", pady=2)
    return label

def create_dark_entry(parent, text="", row=0, col=1, width=20):
    entry = tk.Entry(parent, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG, width=width)
    entry.insert(0, text)
    entry.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
    return entry

# Start Row Indexing
row_index = 0

create_dark_label(left_frame, "Name:", row_index, 0)
name_entry = create_dark_entry(left_frame, BASE_CONFIG["Name"], row_index, 1)
row_index += 1

create_dark_label(left_frame, "Chance:", row_index, 0)
chance_entry = create_dark_entry(left_frame, str(BASE_CONFIG["Chance"]), row_index, 1, width=8)
row_index += 1

create_dark_label(left_frame, "CanBeLooted:", row_index, 0)
loot_var = tk.BooleanVar(value=bool(BASE_CONFIG["CanBeLooted"]))
tk.Checkbutton(left_frame, variable=loot_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).grid(row=row_index, column=1, sticky="w")
row_index += 1

create_dark_label(left_frame, "Faction:", row_index, 0)
faction_var = tk.StringVar(value=BASE_CONFIG["Faction"])
ttk.OptionMenu(left_frame, faction_var, BASE_CONFIG["Faction"], *FACTIONS).grid(row=row_index, column=1, sticky="ew")
row_index += 1

create_dark_label(left_frame, "Behaviour:", row_index, 0)
behaviour_var = tk.StringVar(value=BASE_CONFIG["Behaviour"])
ttk.OptionMenu(left_frame, behaviour_var, BASE_CONFIG["Behaviour"], *BEHAVIOURS).grid(row=row_index, column=1, sticky="ew")
row_index += 1

create_dark_label(left_frame, "Loadout:", row_index, 0)
loadout_entry = create_dark_entry(left_frame, BASE_CONFIG["Loadout"], row_index, 1)
row_index += 1

create_dark_label(left_frame, "NumberOfAI:", row_index, 0)
num_ai_entry = create_dark_entry(left_frame, str(BASE_CONFIG["NumberOfAI"]), row_index, 1, width=8)
row_index += 1

create_dark_label(left_frame, "Speed:", row_index, 0)
speed_var = tk.StringVar(value=BASE_CONFIG["Speed"])
ttk.OptionMenu(left_frame, speed_var, BASE_CONFIG["Speed"], *SPEEDS).grid(row=row_index, column=1, sticky="ew")
row_index += 1

create_dark_label(left_frame, "UnderThreatSpeed:", row_index, 0)
uts_var = tk.StringVar(value=BASE_CONFIG["UnderThreatSpeed"])
ttk.OptionMenu(left_frame, uts_var, BASE_CONFIG["UnderThreatSpeed"], *SPEEDS).grid(row=row_index, column=1, sticky="ew")
row_index += 1

# --- Random Waypoint Start Checkbox (Text Changed) ---
create_dark_label(left_frame, "Use Random Waypoint As Start Point:", row_index, 0)
random_wp_var = tk.BooleanVar(value=bool(BASE_CONFIG["UseRandomWaypointAsStartPoint"]))
tk.Checkbutton(left_frame, variable=random_wp_var, bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR).grid(row=row_index, column=1, sticky="w")
row_index += 1
# --- End Checkbox ---

create_dark_label(left_frame, "UnlimitedReload:", row_index, 0)
ur_listbox = tk.Listbox(left_frame, selectmode=tk.MULTIPLE, height=len(UNLIMITED_RELOAD_OPTIONS),
                         bg=ENTRY_BG, fg=ENTRY_FG, selectbackground="#555555", selectforeground=ENTRY_FG)
for option in UNLIMITED_RELOAD_OPTIONS.keys():
    ur_listbox.insert(tk.END, option)
default_index = list(UNLIMITED_RELOAD_OPTIONS.keys()).index("All targets")
ur_listbox.selection_set(default_index)
ur_listbox.grid(row=row_index, column=1, sticky="ew", pady=2)
row_index += 1 # Advance row index past the listbox

# --- Button Frame for layout ---
button_frame = tk.Frame(left_frame, bg=BG_COLOR)
button_frame.grid(row=row_index, column=0, columnspan=2, pady=(10, 5), sticky="ew")
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)

# --- Recording Button ---
recording_button = tk.Button(button_frame, text="Start Recording", command=toggle_recording,
                             bg=BUTTON_BG, fg=BUTTON_FG)
recording_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

# --- Clear Recording Button ---
clear_button = tk.Button(button_frame, text="Clear Recording", command=clear_recording_data,
                         bg=CLEAR_BUTTON_BG, fg=BUTTON_FG)
clear_button.grid(row=0, column=1, padx=5, sticky="ew")

# --- Original Generate Button ---
generate_button = tk.Button(button_frame, text="Generate Config", command=generate_config,
                             bg=BUTTON_BG, fg=BUTTON_FG)
generate_button.grid(row=0, column=2, padx=(5, 0), sticky="ew")
row_index += 1 # Advance row index past the button frame

tk.Label(right_frame, text="Paste Position Data (Position: <x, y, z> per line):",
          bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
input_text = tk.Text(right_frame, height=10, width=70, bg=ENTRY_BG, fg=ENTRY_FG,
                      insertbackground=ENTRY_FG, font=("Consolas", 10))
input_text.pack(fill="both", expand=False, pady=5)

tk.Label(right_frame, text="Formatted Config Output:", bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w")
output_text = tk.Text(right_frame, height=25, width=70, bg=ENTRY_BG, fg=ENTRY_FG,
                      insertbackground=ENTRY_FG, font=("Consolas", 10))
output_text.pack(fill="both", expand=True, pady=5)

root.mainloop()