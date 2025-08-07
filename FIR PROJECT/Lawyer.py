import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk  # Import themed Tkinter widgets
import re
import random
import json
import os
import datetime

# --- Configuration ---
FIR_DATA_FILE = 'fir_data.json'    # File path for saving/loading FIR data
INITIAL_DUMMY_CNICS = 50           # Reduced for faster dummy data generation
MAX_RANDOM_FIRS_PER_CNIC = 3       # Max FIR sections to assign randomly

# --- Expanded Pakistan Laws Dictionary (as provided) ---
laws = {
    # --- Pakistan Penal Code (PPC) ---
    "302": {"act": "PPC", "title": "Murder", "punishment": "Death, life imprisonment, and fine"},
    "324": {"act": "PPC", "title": "Attempt to Murder", "punishment": "Up to 10 years or life imprisonment, and/or fine"},
    "337A": {"act": "PPC", "title": "Hurt (Simple)", "punishment": "Up to 1 year imprisonment or fine"},
    "337L(2)": {"act": "PPC", "title": "Rash or Negligent Act Causing Hurt", "punishment": "Up to 2 years imprisonment or fine"},
    "382": {"act": "PPC", "title": "Theft after preparation for causing death/hurt/restraint", "punishment": "Up to 10 years and fine"},
    "392": {"act": "PPC", "title": "Robbery", "punishment": "Up to 10 years and fine; if committed on highway, up to 14 years and fine"},
    "406": {"act": "PPC", "title": "Criminal Breach of Trust", "punishment": "Up to 7 years and fine"},
    "420": {"act": "PPC", "title": "Cheating and dishonestly inducing delivery of property", "punishment": "Up to 7 years and fine"},
    "447": {"act": "PPC", "title": "Criminal Trespass", "punishment": "Up to 3 months or fine"},
    "452": {"act": "PPC", "title": "House-trespass after preparation for hurt, assault or wrongful restraint", "punishment": "Up to 10 years and fine"},
    "506": {"act": "PPC", "title": "Criminal Intimidation", "punishment": "Up to 2 years or fine"},
    "186": {"act": "PPC", "title": "Obstructing Public Servant", "punishment": "Up to 3 months or fine up to PKR 50,000"},
    "147": {"act": "PPC", "title": "Rioting", "punishment": "Up to 2 years or fine"},
    "109": {"act": "PPC", "title": "Abetment", "punishment": "Same as for the main offence, and fine"},
    "295C": {"act": "PPC", "title": "Blasphemy (Defiling Holy Prophet)", "punishment": "Death or life imprisonment, and fine"},
    "295A": {"act": "PPC", "title": "Deliberate and malicious acts intended to outrage religious feelings", "punishment": "Up to 10 years or fine"},
    "298C": {"act": "PPC", "title": "Qadiani/Ahmadi posing as Muslim", "punishment": "Imprisonment up to 3 years and fine"},
    "365": {"act": "PPC", "title": "Kidnapping or abducting with intent secretly and wrongfully to confine person", "punishment": "Up to 7 years and fine"},
    "376": {"act": "PPC", "title": "Rape", "punishment": "Death or imprisonment for life or rigorous imprisonment up to 25 years, and fine"},

    # --- Anti-Terrorism Act (ATA) ---
    "6ATA": {"act": "ATA", "title": "Definition of Terrorism", "punishment": "Varies by act; includes death, life imprisonment, and confiscation of property"},
    "7ATA": {"act": "ATA", "title": "Punishment for Terrorist Act", "punishment": "Death, life imprisonment or confiscation, and fine"},
    "11EATA": {"act": "ATA", "title": "Proscription of organizations", "punishment": "Strict penalties for membership/support, and fine"},
    "11WATA": {"act": "ATA", "title": "Hate Speech", "punishment": "Up to 7 years, fine, and forfeiture of property"},
    "21ATA": {"act": "ATA", "title": "Collection of funds for terrorist purposes", "punishment": "Up to 14 years and fine"},

    # --- Prevention of Electronic Crimes Act (PECA) ---
    "3PECA": {"act": "PECA", "title": "Unauthorized Access (Hacking)", "punishment": "Up to 3 years or fine or both"},
    "4PECA": {"act": "PECA", "title": "Unauthorized Copying or Transmission of Data", "punishment": "Up to 2 years or fine or both"},
    "11PECA": {"act": "PECA", "title": "Cyberstalking", "punishment": "3 years imprisonment and/or fine"},
    "14PECA": {"act": "PECA", "title": "Electronic Fraud", "punishment": "Up to 7 years imprisonment or fine or both"},
    "20PECA": {"act": "PECA", "title": "Offences against dignity of a natural person (Defamation)", "punishment": "3 years + 1 million fine"},
    "21PECA": {"act": "PECA", "title": "Offences against modesty of a natural person and minor", "punishment": "Up to 7 years, fine, and confiscation"},
    "24PECA": {"act": "PECA", "title": "Spoofing (SMS/Email)", "punishment": "Up to 3 years or fine or both"},
    "37PECA": {"act": "PECA", "title": "Unlawful Online Content", "punishment": "Removal, blocking, and potential legal action, and fine"},

    # --- Code of Criminal Procedure (CrPC) ---
    "54CrPC": {"act": "CrPC", "title": "Arrest without warrant (Cognizable Offence)", "punishment": "Procedure for arrest, not a crime in itself"},
    "61CrPC": {"act": "CrPC", "title": "Detention Limit", "punishment": "Cannot detain beyond 24 hrs without magistrate's order"},
    "154CrPC": {"act": "CrPC", "title": "Recording of FIR", "punishment": "Police must record FIR for cognizable offense"},
    "164CrPC": {"act": "CrPC", "title": "Recording of Confession/Statement", "punishment": "Procedure for recording evidence"},
    "173CrPC": {"act": "CrPC", "title": "Police Report (Challan)", "punishment": "Procedure for submitting investigation report"},

    # --- Control of Narcotic Substances Act (CNSA) ---
    "6CNSA": {"act": "CNSA", "title": "Prohibition of possession of narcotic drugs, etc.", "punishment": "Varies significantly by quantity/type, from 2 years to death, and heavy fine"},
    "9CNSA": {"act": "CNSA", "title": "Drug Possession (General)", "punishment": "Imprisonment up to lifetime + fine, varies by quantity"},
    "8CNSA": {"act": "CNSA", "title": "Trafficking or financing trafficking of narcotic substances", "punishment": "Minimum 2 years to death depending on quantity, and heavy fine"},

    # --- Foreigners Act (FA) ---
    "3FA": {"act": "Foreigners Act", "title": "Restriction of entry, stay and departure", "punishment": "Deportation, imprisonment, and fine"},
    "14FA": {"act": "Foreigners Act", "title": "Illegal Entry/Overstay", "punishment": "Deportation or 3 years jail and/or fine up to PKR 10,000"},

    # --- NAB Ordinance (National Accountability Ordinance) ---
    "9NAB": {"act": "NAB Ordinance", "title": "Corruption & Corrupt Practices (General)", "punishment": "Up to 14 years max + fine, and disqualification from public office"},
    "10NAB": {"act": "NAB Ordinance", "title": "Reference for investigation/trial", "punishment": "Procedure, not a punishment itself"},

    # --- Motor Vehicle Ordinance (MVO) ---
    "279MVO": {"act": "MVO", "title": "Rash Driving or Riding on a Public Way", "punishment": "Up to 2 years + fine"},
    "99MVO": {"act": "MVO", "title": "Driving without License", "punishment": "Fine up to PKR 5000 and/or short imprisonment"},
    "116MVO": {"act": "MVO", "title": "Disobedience of orders", "punishment": "Fine and/or short imprisonment"},

    # --- Arms Ordinance (AO) ---
    "13AO": {"act": "Arms Ordinance", "title": "Possession of illicit arms", "punishment": "Up to 7 years imprisonment or fine or both"},
    "13AOA": {"act": "Arms Ordinance", "title": "Prohibition of automatic weapons", "punishment": "Strict penalties, and fine"},

    #  Maintenance of Public Order (MPO) ---
    "3MPO": {"act": "MPO", "title": "Power to arrest and detain suspected persons", "punishment": "Up to 3 months detention (extendable)"},
    "16MPO": {"act": "MPO", "title": "Disobedience to order duly promulgated by public servant", "punishment": "Up to 6 months or fine"},

    #  Prevention of Corruption Act (PCA) ---
    "5PCA": {"act": "PCA", "title": "Criminal misconduct by public servant", "punishment": "Up to 7 years and/or fine"},

    #  Qanun-e-Shahadat Order (QSO - Law of Evidence) ---
    "3QSO": {"act": "QSO", "title": "Competency of Witnesses", "punishment": "Admissibility of evidence, not a crime"},
    "129QSO": {"act": "QSO", "title": "Estoppel", "punishment": "Legal principle, not a crime"},
    "163QSO": {"act": "QSO", "title": "Electronic Evidence", "punishment": "Admissibility of electronic records"},

    # Customs Act (CA)
    "156CA": {"act": "Customs Act", "title": "Offences and Penalties (Smuggling)", "punishment": "Imprisonment, fine, and confiscation of goods"},

    #  Anti-Money Laundering Act (AMLA)
    "3AMLA": {"act": "AMLA", "title": "Offence of Money Laundering", "punishment": "3 to 10 years imprisonment and fine up to 100 million rupees"},
}

# --- Data Persistence Functions ---
def load_fir_data():
    """Loads FIR data from the JSON file."""
    if os.path.exists(FIR_DATA_FILE):
        try:
            with open(FIR_DATA_FILE, 'r') as f:
                data = json.load(f)
                # Ensure the loaded data matches the new structure (dict of lists of dicts)
                if isinstance(data, dict) and all(isinstance(v, list) and all(isinstance(item, dict) for item in v) for v in data.values()):
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Loaded {sum(len(v) for v in data.values())} FIRs across {len(data)} CNIC entries from {FIR_DATA_FILE}.")
                    return data
                else:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Warning: {FIR_DATA_FILE} content is invalid or old format. Starting with empty data.")
                    return {}
        except json.JSONDecodeError as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error decoding {FIR_DATA_FILE}: {e}. Starting with empty data.")
            return {}
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] An unexpected error occurred while loading {FIR_DATA_FILE}: {e}. Starting with empty data.")
            return {}
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {FIR_DATA_FILE} not found. Starting with empty data.")
    return {}

def save_fir_data(data):
    """Saves FIR data to the JSON file."""
    try:
        with open(FIR_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Data successfully saved to {FIR_DATA_FILE}.")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Error saving data to {FIR_DATA_FILE}: {e}")

# --- Initial Load of FIR Data ---
fir_data = load_fir_data()

# --- Utility Functions ---
def generate_random_cnic():
    """Generates a random valid Pakistani CNIC format."""
    part1 = str(random.randint(10000, 99999))
    part2 = str(random.randint(1000000, 9999997))
    part3 = str(random.randint(0, 7))
    return f"{part1}-{part2}-{part3}"

def generate_fir_number():
    """Generates a unique FIR number (e.g., Year/District/Sequence)."""
    year = datetime.datetime.now().year
    # This is a very basic sequential number; in a real system, it would be much more robust
    # and likely come from a database sequence. For now, find the highest existing.
    max_seq = 0
    for cnic_firs in fir_data.values():
        for fir_detail in cnic_firs:
            fir_num = fir_detail.get('fir_number', '')
            match = re.match(r'^\d{4}/[A-Z]{3}/(\d+)$', fir_num) # e.g., 2024/LHR/0001
            if match:
                max_seq = max(max_seq, int(match.group(1)))
    new_seq = max_seq + 1
    # Example District Code, could be user input later
    district_code = "LHR"
    return f"{year}/{district_code}/{new_seq:04d}" # Pad with leading zeros to 4 digits

# --- Generate Dummy FIR Data if file is empty or in old format ---
if not fir_data:
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Generating initial dummy FIR data with new structure...")
    all_sections = list(laws.keys())
    dummy_names = ["Ali", "Sara", "Ahmed", "Fatima", "Usman", "Ayesha", "Bilal", "Zainab"]
    dummy_father_names = ["Muhammad", "Akram", "Hussain", "Javed", "Iqbal"]
    dummy_reasons = [
        "Personal dispute leading to physical altercation.",
        "Attempted theft from a convenience store.",
        "Cyberbullying on social media platform.",
        "Traffic violation resulting in minor accident.",
        "Unauthorized access to private property.",
        "Possession of small quantity of contraband.",
        "Verbal threat and intimidation."
    ]
    bail_statuses = ["Granted", "Denied", "Pending", "N/A"]
    punishments = ["Case ongoing", "Acquitted", "Sentenced to 1 year imprisonment", "Fine imposed", "Community service ordered", "Case dismissed"]

    for _ in range(INITIAL_DUMMY_CNICS):
        cnic = generate_random_cnic()
        while cnic in fir_data: # Ensure unique CNIC for dummy data
            cnic = generate_random_cnic()

        num_firs_for_cnic = random.randint(0, MAX_RANDOM_FIRS_PER_CNIC)
        fir_data[cnic] = [] # Initialize list for FIRs for this CNIC

        for _ in range(num_firs_for_cnic):
            fir_num = generate_fir_number() # Generate a new FIR number
            complainant = random.choice(dummy_names)
            complainant_father = random.choice(dummy_father_names)
            accused_name = random.choice(dummy_names) # Assign a dummy accused name
            accused_father = random.choice(dummy_father_names)
            reason = random.choice(dummy_reasons)
            fir_date = (datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
            bail_status = random.choice(bail_statuses)
            punishment = random.choice(punishments)

            assigned_sections = random.sample(all_sections, random.randint(1, min(3, len(all_sections))))

            fir_entry = {
                "fir_number": fir_num,
                "complainant_name": complainant,
                "complainant_father_name": complainant_father,
                "accused_name": accused_name,
                "accused_father_name": accused_father,
                "cnic": cnic, # Store CNIC within FIR entry for easier lookup
                "reason": reason,
                "fir_date": fir_date,
                "sections": assigned_sections,
                "bail_status": bail_status,
                "punishment": punishment
            }
            fir_data[cnic].append(fir_entry)
    save_fir_data(fir_data)
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Generated and saved {sum(len(v) for v in fir_data.values())} dummy FIR entries.")


# --- Validation Functions ---
def is_valid_cnic(cnic):
    """Checks if the CNIC format is valid (XXXXX-XXXXXXX-X)."""
    return re.fullmatch(r'\d{5}-\d{7}-\d{1}', cnic)

def is_valid_fir_number(fir_num):
    """Checks if the FIR number format is valid (YYYY/DDD/NNNN)."""
    return re.fullmatch(r'\d{4}/[A-Z]{3}/\d{4,}', fir_num) # Allows for more than 4 digits for sequence

# --- GUI Application Class ---
class FIRApp:
    def __init__(self, master):
        self.master = master
        master.title("Pakistan FIR Context  System") # Updated title
        master.geometry("1100x850") # Wider and taller window
        master.resizable(True, True) # Allow resizing

        # --- Theme and Style Configuration (as provided) ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.master.tk_setPalette(background='#F0F8FF', foreground='#333333')
        self.style.configure('.', font=('Segoe UI', 10), background='#F0F8FF', foreground='#333333')

        self.style.configure('TLabel', font=('Segoe UI', 10), foreground='#333333', background='#F0F8FF')
        self.style.configure('TEntry', font=('Arial', 12), padding=5, relief='flat', borderwidth=1,
                             fieldbackground='white', foreground='#333333', bordercolor='#CCCCCC')
        self.style.map('TEntry', fieldbackground=[('focus', '#E8F0FE')],
                                  bordercolor=[('focus', '#4682B4'), ('!focus', '#CCCCCC')])

        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=10, relief='flat', borderwidth=0,
                             foreground='white')
        self.style.configure('Blue.TButton', background='#4682B4')
        self.style.map('Blue.TButton', background=[('active', '#36648B')], foreground=[('active', 'white')], cursor=[('active', 'hand2')])
        self.style.configure('Orange.TButton', background='#FFA500')
        self.style.map('Orange.TButton', background=[('active', '#CD8500')], foreground=[('active', 'white')], cursor=[('active', 'hand2')])
        self.style.configure('Green.TButton', background='#3CB371')
        self.style.map('Green.TButton', background=[('active', '#2E8B57')], foreground=[('active', 'white')], cursor=[('active', 'hand2')])
        self.style.configure('Red.TButton', background='#DC143C')
        self.style.map('Red.TButton', background=[('active', '#B22222')], foreground=[('active', 'white')], cursor=[('active', 'hand2')])
        self.style.configure('Purple.TButton', background='#8A2BE2')
        self.style.map('Purple.TButton', background=[('active', '#6A1AAB')], foreground=[('active', 'white')], cursor=[('active', 'hand2')])

        self.style.configure('TLabelFrame', font=('Segoe UI', 12, 'bold'), foreground='#0056b3', padding=(15, 10),
                             background='#E0E8F0')
        self.style.configure('TLabelFrame.Label', background='#E0E8F0', foreground='#0056b3')

        self.style.configure('TScrolledText', relief='flat', borderwidth=1, background='white', foreground='#333333',
                             font=('Arial', 12))
        self.style.map('TScrolledText', background=[('readonly', '#F0F0F0')])

        # --- Main Frame for overall padding ---
        self.main_frame = ttk.Frame(master, padding="20 20 20 20", style='TFrame')
        self.main_frame.pack(fill="both", expand=True)

        # --- Frames for layout ---
        self.search_frame = ttk.LabelFrame(self.main_frame, text=" Search & Delete FIR") # Generic title
        self.search_frame.pack(padx=10, pady=10, fill="x", expand=False)

        self.add_update_frame = ttk.LabelFrame(self.main_frame, text=" Register New FIR / Update Existing") # Updated title
        self.add_update_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Configure grid for search_frame
        self.search_frame.columnconfigure(1, weight=1) # CNIC Entry expands
        self.search_frame.columnconfigure(3, weight=1) # FIR Number Entry expands
        self.search_frame.rowconfigure(3, weight=1)    # Output area expands

        # Configure grid for add_update_frame
        # Make some columns expandable for better layout
        self.add_update_frame.columnconfigure(1, weight=1)
        self.add_update_frame.columnconfigure(3, weight=1)
        self.add_update_frame.rowconfigure(8, weight=1) # FIR details output area

        # --- Search Section Widgets ---
        # Search by CNIC
        ttk.Label(self.search_frame, text="Accused CNIC:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.search_cnic_entry = ttk.Entry(self.search_frame, font=('Arial', 12))
        self.search_cnic_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.search_cnic_placeholder = "e.g. 35201-1234567-1"
        self._set_placeholder(self.search_cnic_entry, self.search_cnic_placeholder)

        # Search by FIR Number
        ttk.Label(self.search_frame, text="FIR Number:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.search_fir_num_entry = ttk.Entry(self.search_frame, font=('Arial', 12))
        self.search_fir_num_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        self.search_fir_num_placeholder = "e.g. 2024/LHR/0001"
        self._set_placeholder(self.search_fir_num_entry, self.search_fir_num_placeholder)

        # Search by Accused Name
        ttk.Label(self.search_frame, text="Accused Name:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.search_accused_name_entry = ttk.Entry(self.search_frame, font=('Arial', 12))
        self.search_accused_name_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.search_accused_name_placeholder = "e.g.Accused Name"
        self._set_placeholder(self.search_accused_name_entry, self.search_accused_name_placeholder)

        # Search by Accused Father's Name
        ttk.Label(self.search_frame, text="Accused Father's Name :").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.search_accused_father_entry = ttk.Entry(self.search_frame, font=('Arial', 12))
        self.search_accused_father_entry.grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        self.search_accused_father_placeholder = "e.g. Muhammad Iqbal"
        self._set_placeholder(self.search_accused_father_entry, self.search_accused_father_placeholder)


        # Buttons for Search Section
        self.check_button = ttk.Button(self.search_frame, text="Search FIR", command=self.check_fir_gui, style='Blue.TButton')
        self.check_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        self.clear_search_button = ttk.Button(self.search_frame, text="Clear Search Fields", command=self.clear_search_fields_gui, style='Orange.TButton')
        self.clear_search_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.delete_fir_button = ttk.Button(self.search_frame, text="Delete Selected FIR", command=self.delete_fir_gui, style='Red.TButton')
        self.delete_fir_button.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        self.view_all_firs_button = ttk.Button(self.search_frame, text="View All FIRs", command=self.view_all_firs, style='Purple.TButton')
        self.view_all_firs_button.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # Output area for search results
        self.output_area_search = scrolledtext.ScrolledText(self.search_frame, wrap=tk.WORD, height=12, state='disabled',
                                                             relief=tk.FLAT, bd=1, background='white', foreground='#333333', font=('Arial', 12))
        self.output_area_search.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Configure tags for output_area_search
        self.output_area_search.tag_configure('red', foreground='red')
        self.output_area_search.tag_configure('green', foreground='green')
        self.output_area_search.tag_configure('darkred', foreground='#8B0000')
        self.output_area_search.tag_configure('crimson', foreground='#DC143C')
        self.output_area_search.tag_configure('header', font=('Arial', 14, 'bold'), foreground='#0056b3') # Main header for FIR details
        self.output_area_search.tag_configure('fir_detail_label', font=('Arial', 12, 'bold'), foreground='#4682B4') # Labels for details
        self.output_area_search.tag_configure('fir_detail_value', font=('Arial', 12), foreground='#333333') # Values for details
        self.output_area_search.tag_configure('section_info', font=('Arial', 12, 'italic'), foreground='#2F4F4F') # For law sections
        self.output_area_search.tag_configure('complainant_section_header', font=('Arial', 13, 'bold', 'underline'), foreground='#006400') # Dark Green for Complainant
        self.output_area_search.tag_configure('accused_section_header', font=('Arial', 13, 'bold', 'underline'), foreground='#8B0000') # Dark Red for Accused


        # --- Add/Update Section Widgets ---
        # Row 0
        ttk.Label(self.add_update_frame, text="Accused CNIC:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.add_cnic_entry = ttk.Entry(self.add_update_frame)
        self.add_cnic_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.add_cnic_placeholder = "e.g. 35201-1234567-1"
        self._set_placeholder(self.add_cnic_entry, self.add_cnic_placeholder)

        ttk.Label(self.add_update_frame, text="FIR Number (Optional):").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.add_fir_num_entry = ttk.Entry(self.add_update_frame)
        self.add_fir_num_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        self.add_fir_num_placeholder = "Leave empty to auto-generate or enter existing"
        self._set_placeholder(self.add_fir_num_entry, self.add_fir_num_placeholder)

        # Row 1
        ttk.Label(self.add_update_frame, text="Complainant Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.add_complainant_name_entry = ttk.Entry(self.add_update_frame)
        self.add_complainant_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.add_complainant_name_placeholder = "e.g. Ahmed Ali"
        self._set_placeholder(self.add_complainant_name_entry, self.add_complainant_name_placeholder)

        ttk.Label(self.add_update_frame, text="Complainant Father's Name:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.add_complainant_father_entry = ttk.Entry(self.add_update_frame)
        self.add_complainant_father_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")
        self.add_complainant_father_placeholder = "e.g. Zulfiqar Ali"
        self._set_placeholder(self.add_complainant_father_entry, self.add_complainant_father_placeholder)

        # Row 2
        ttk.Label(self.add_update_frame, text="Accused Name:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.add_accused_name_entry = ttk.Entry(self.add_update_frame)
        self.add_accused_name_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.add_accused_name_placeholder = "e.g. Asif Mehmood"
        self._set_placeholder(self.add_accused_name_entry, self.add_accused_name_placeholder)

        ttk.Label(self.add_update_frame, text="Accused Father's Name:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.add_accused_father_entry = ttk.Entry(self.add_update_frame)
        self.add_accused_father_entry.grid(row=2, column=3, padx=10, pady=5, sticky="ew")
        self.add_accused_father_placeholder = "e.g. Pervez Akhtar"
        self._set_placeholder(self.add_accused_father_entry, self.add_accused_father_placeholder)

        # Row 3
        ttk.Label(self.add_update_frame, text="FIR Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.add_fir_date_entry = ttk.Entry(self.add_update_frame)
        self.add_fir_date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.add_fir_date_placeholder = datetime.date.today().strftime("%Y-%m-%d") # Default to today's date
        self._set_placeholder(self.add_fir_date_entry, self.add_fir_date_placeholder)

        ttk.Label(self.add_update_frame, text="Reason for FIR:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.add_reason_entry = ttk.Entry(self.add_update_frame)
        self.add_reason_entry.grid(row=3, column=3, padx=10, pady=5, sticky="ew")
        self.add_reason_placeholder = "e.g. Theft of electronics from residence"
        self._set_placeholder(self.add_reason_entry, self.add_reason_placeholder)

        # Row 4
        ttk.Label(self.add_update_frame, text="Applied Sections:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.add_sections_entry = ttk.Entry(self.add_update_frame)
        self.add_sections_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.add_sections_placeholder = "e.g. 302, 7ATA, 11PECA (comma-separated)"
        self._set_placeholder(self.add_sections_entry, self.add_sections_placeholder)

        ttk.Label(self.add_update_frame, text="Bail Status:").grid(row=4, column=2, padx=10, pady=5, sticky="w")
        self.add_bail_status_combobox = ttk.Combobox(self.add_update_frame, values=["N/A", "Granted", "Denied", "Pending"])
        self.add_bail_status_combobox.grid(row=4, column=3, padx=10, pady=5, sticky="ew")
        self.add_bail_status_combobox.set("N/A") # Default value

        # Row 5
        ttk.Label(self.add_update_frame, text="Punishment Details:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.add_punishment_entry = ttk.Entry(self.add_update_frame)
        self.add_punishment_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=5, sticky="ew")
        self.add_punishment_placeholder = "e.g. Sentenced to 5 years rigorous imprisonment and PKR 100,000 fine"
        self._set_placeholder(self.add_punishment_entry, self.add_punishment_placeholder)

        # Row 6 - Buttons for Add/Update Section
        self.add_update_button = ttk.Button(self.add_update_frame, text="Register / Update FIR", command=self.add_update_fir_gui, style='Green.TButton')
        self.add_update_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.clear_add_button = ttk.Button(self.add_update_frame, text="Clear Entry Fields", command=self.clear_add_fields_gui, style='Orange.TButton')
        self.clear_add_button.grid(row=6, column=2, columnspan=2, padx=5, pady=10, sticky="ew")

        # Row 7 - Output area for Add/Update results
        self.add_output_area = scrolledtext.ScrolledText(self.add_update_frame, wrap=tk.WORD, height=10, state='disabled',
                                                         relief=tk.FLAT, bd=1, background='white', foreground='#333333', font=('Arial', 12))
        self.add_output_area.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")


    # --- Placeholder logic for Entry fields ---
    def _set_placeholder(self, entry_widget, placeholder_text):
        # Clear existing bindings to prevent multiple callbacks
        entry_widget.unbind("<FocusIn>")
        entry_widget.unbind("<FocusOut>")

        entry_widget.insert(0, placeholder_text)
        entry_widget.configure(foreground='gray')
        entry_widget.bind("<FocusIn>", lambda event: self._on_entry_focus_in(event, entry_widget, placeholder_text))
        entry_widget.bind("<FocusOut>", lambda event: self._on_entry_focus_out(event, entry_widget, placeholder_text))

    def _on_entry_focus_in(self, event, entry_widget, placeholder_text):
        if entry_widget.get() == placeholder_text:
            entry_widget.delete(0, tk.END)
            entry_widget.configure(foreground='#333333')
        self.style.configure('TEntry', bordercolor='#CCCCCC') # Reset to default border
        entry_widget.config(style='TEntry')


    def _on_entry_focus_out(self, event, entry_widget, placeholder_text):
        if not entry_widget.get():
            entry_widget.insert(0, placeholder_text)
            entry_widget.configure(foreground='gray')
        self.style.configure('TEntry', bordercolor='#CCCCCC') # Ensure default border when unfocused
        entry_widget.config(style='TEntry')

    # --- Helper to update ScrolledText widgets ---
    def update_output(self, output_widget, message, append=False, color=None, font_tag=None):
        output_widget.config(state='normal')
        if not append:
            output_widget.delete(1.0, tk.END)

        tags = []
        if color:
            tags.append(color)
        if font_tag:
            tags.append(font_tag)

        output_widget.insert(tk.END, message + "\n", tuple(tags) if tags else ())
        output_widget.see(tk.END)
        output_widget.config(state='disabled')

    # --- Temporary Message for Success/Error ---
    def show_temp_message(self, entry_widget, message, color='green', duration=2000):
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() - 30
        temp_label = tk.Label(self.master, text=message, bg=self.master.cget('bg'), fg=color, font=('Segoe UI', 9, 'bold'))
        temp_label.wm_overrideredirect(True)
        temp_label.wm_geometry(f"+{x}+{y}")
        temp_label.lift()
        temp_label.after(duration, temp_label.destroy)

    # --- Core Logic Functions ---
    def check_fir_gui(self):
        cnic_search = self.search_cnic_entry.get().strip()
        fir_num_search = self.search_fir_num_entry.get().strip()
        accused_name_search = self.search_accused_name_entry.get().strip()
        accused_father_search = self.search_accused_father_entry.get().strip()

        # Treat placeholders as empty
        if cnic_search == self.search_cnic_placeholder:
            cnic_search = ""
        if fir_num_search == self.search_fir_num_placeholder:
            fir_num_search = ""
        if accused_name_search == self.search_accused_name_placeholder:
            accused_name_search = ""
        if accused_father_search == self.search_accused_father_placeholder:
            accused_father_search = ""

        if not cnic_search and not fir_num_search and not accused_name_search and not accused_father_search:
            self.update_output(self.output_area_search, "Please enter at least one search criterion (CNIC, FIR Number, Accused Name, or Accused Father's Name).", 'red')
            return

        found_firs = []
        for cnic_key, fir_list in fir_data.items():
            if cnic_search and cnic_search != cnic_key:
                continue # Skip if searching by CNIC and it doesn't match

            for fir_detail in fir_list:
                match_cnic = not cnic_search or (cnic_search == cnic_key)
                match_fir_num = not fir_num_search or (fir_num_search.lower() == fir_detail.get('fir_number', '').lower())
                match_accused_name = not accused_name_search or (accused_name_search.lower() in fir_detail.get('accused_name', '').lower())
                match_accused_father = not accused_father_search or (accused_father_search.lower() in fir_detail.get('accused_father_name', '').lower())

                if match_cnic and match_fir_num and match_accused_name and match_accused_father:
                    found_firs.append(fir_detail)

        self.update_output(self.output_area_search, "", append=False) # Clear previous results

        if found_firs:
            self.update_output(self.output_area_search, f"Found {len(found_firs)} FIR(s):", 'green', 'header')
            for i, fir in enumerate(found_firs):
                self.update_output(self.output_area_search, f"\n--- FIR Details {i+1} ---", True, 'darkred', 'header')
                self.update_output(self.output_area_search, f"FIR Number: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('fir_number', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Complainant Details ---", True, 'complainant_section_header')
                self.update_output(self.output_area_search, f"Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('complainant_name', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Father's Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('complainant_father_name', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Accused Details ---", True, 'accused_section_header')
                self.update_output(self.output_area_search, f"CNIC: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('cnic', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('accused_name', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Father's Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('accused_father_name', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Case Details ---", True, 'darkred', 'header')
                self.update_output(self.output_area_search, f"Date: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('fir_date', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Reason: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('reason', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Bail Status: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('bail_status', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Punishment: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('punishment', 'N/A')}", True, font_tag='fir_detail_value')

                sections_applied = fir.get('sections', [])
                if sections_applied:
                    self.update_output(self.output_area_search, f"Applied Sections:", True, font_tag='fir_detail_label')
                    for section in sections_applied:
                        law_info = laws.get(section, {})
                        title = law_info.get('title', 'Unknown Title')
                        act = law_info.get('act', 'Unknown Act')
                        punishment = law_info.get('punishment', 'N/A')
                        self.update_output(self.output_area_search, f"  - {section} ({act}): {title} (Punishment: {punishment})", True, font_tag='section_info')
                else:
                    self.update_output(self.output_area_search, f"Applied Sections: N/A", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, "\n" + "-"*50, True, 'gray') # Separator


        else:
            self.update_output(self.output_area_search, "No FIR found matching the criteria.", 'crimson')

    def add_update_fir_gui(self):
        cnic = self.add_cnic_entry.get().strip()
        fir_num = self.add_fir_num_entry.get().strip()
        complainant_name = self.add_complainant_name_entry.get().strip()
        complainant_father_name = self.add_complainant_father_entry.get().strip()
        accused_name = self.add_accused_name_entry.get().strip()
        accused_father_name = self.add_accused_father_entry.get().strip()
        fir_date = self.add_fir_date_entry.get().strip()
        reason = self.add_reason_entry.get().strip()
        sections_str = self.add_sections_entry.get().strip()
        bail_status = self.add_bail_status_combobox.get().strip()
        punishment = self.add_punishment_entry.get().strip()

        # Treat placeholders as empty input
        if cnic == self.add_cnic_placeholder: cnic = ""
        if fir_num == self.add_fir_num_placeholder: fir_num = ""
        if complainant_name == self.add_complainant_name_placeholder: complainant_name = ""
        if complainant_father_name == self.add_complainant_father_name_placeholder: complainant_father_name = ""
        if accused_name == self.add_accused_name_placeholder: accused_name = ""
        if accused_father_name == self.add_accused_father_name_placeholder: accused_father_name = ""
        if fir_date == self.add_fir_date_placeholder: fir_date = datetime.date.today().strftime("%Y-%m-%d") # Use actual date
        if reason == self.add_reason_placeholder: reason = ""
        if sections_str == self.add_sections_placeholder: sections_str = ""
        if punishment == self.add_punishment_placeholder: punishment = ""

        # Validation
        if not cnic or not is_valid_cnic(cnic):
            self.update_output(self.add_output_area, "Invalid or missing Accused CNIC. Format: XXXXX-XXXXXXX-X", 'red')
            self.show_temp_message(self.add_cnic_entry, "Invalid CNIC!", 'red')
            return
        if not complainant_name:
            self.update_output(self.add_output_area, "Complainant Name is required.", 'red')
            self.show_temp_message(self.add_complainant_name_entry, "Required!", 'red')
            return
        if not accused_name:
            self.update_output(self.add_output_area, "Accused Name is required.", 'red')
            self.show_temp_message(self.add_accused_name_entry, "Required!", 'red')
            return
        if not fir_date or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fir_date):
            self.update_output(self.add_output_area, "Invalid FIR Date. Format: YYYY-MM-DD", 'red')
            self.show_temp_message(self.add_fir_date_entry, "Invalid Date!", 'red')
            return
        if not reason:
            self.update_output(self.add_output_area, "Reason for FIR is required.", 'red')
            self.show_temp_message(self.add_reason_entry, "Required!", 'red')
            return

        sections = [s.strip() for s in sections_str.split(',') if s.strip()]
        for section in sections:
            if section not in laws:
                self.update_output(self.add_output_area, f"Invalid Law Section: {section}. Please enter valid sections from the predefined list.", 'red')
                self.show_temp_message(self.add_sections_entry, f"Invalid Section: {section}!", 'red')
                return

        operation_type = "registered"
        existing_fir_index = -1
        # If FIR number is provided, check if it exists for update
        if fir_num and is_valid_fir_number(fir_num):
            if cnic in fir_data:
                for i, fir in enumerate(fir_data[cnic]):
                    if fir.get('fir_number') == fir_num:
                        existing_fir_index = i
                        operation_type = "updated"
                        break
            if existing_fir_index == -1: # FIR number provided but not found for this CNIC
                self.update_output(self.add_output_area, f"FIR Number '{fir_num}' not found for CNIC '{cnic}'. A new FIR will be registered.", 'orange')
                fir_num = generate_fir_number() # Generate new if not found
                operation_type = "registered"
        else:
            fir_num = generate_fir_number() # Auto-generate for new FIR

        new_fir_entry = {
            "fir_number": fir_num,
            "complainant_name": complainant_name,
            "complainant_father_name": complainant_father_name,
            "accused_name": accused_name,
            "accused_father_name": accused_father_name,
            "cnic": cnic,
            "reason": reason,
            "fir_date": fir_date,
            "sections": sections,
            "bail_status": bail_status,
            "punishment": punishment
        }

        if cnic not in fir_data:
            fir_data[cnic] = []

        if existing_fir_index != -1:
            fir_data[cnic][existing_fir_index] = new_fir_entry
            self.update_output(self.add_output_area, f"FIR '{fir_num}' for CNIC '{cnic}' successfully updated!", 'green')
            self.show_temp_message(self.add_update_button, "FIR Updated!", 'green')
        else:
            fir_data[cnic].append(new_fir_entry)
            self.update_output(self.add_output_area, f"New FIR '{fir_num}' for CNIC '{cnic}' successfully registered!", 'green')
            self.show_temp_message(self.add_update_button, "FIR Registered!", 'green')

        save_fir_data(fir_data)
        self.clear_add_fields_gui(keep_cnic=True) # Keep CNIC for possible rapid entry

    def delete_fir_gui(self):
        cnic_to_delete = self.search_cnic_entry.get().strip()
        fir_num_to_delete = self.search_fir_num_entry.get().strip()

        if cnic_to_delete == self.search_cnic_placeholder: cnic_to_delete = ""
        if fir_num_to_delete == self.search_fir_num_placeholder: fir_num_to_delete = ""

        if not cnic_to_delete:
            self.update_output(self.output_area_search, "Please enter the Accused CNIC to delete an FIR.", 'red')
            self.show_temp_message(self.search_cnic_entry, "CNIC Required!", 'red')
            return
        if not fir_num_to_delete:
            self.update_output(self.output_area_search, "Please enter the FIR Number to delete a specific FIR.", 'red')
            self.show_temp_message(self.search_fir_num_entry, "FIR Number Required!", 'red')
            return
        if not is_valid_cnic(cnic_to_delete):
            self.update_output(self.output_area_search, "Invalid Accused CNIC format for deletion.", 'red')
            self.show_temp_message(self.search_cnic_entry, "Invalid CNIC!", 'red')
            return
        if not is_valid_fir_number(fir_num_to_delete):
            self.update_output(self.output_area_search, "Invalid FIR Number format for deletion.", 'red')
            self.show_temp_message(self.search_fir_num_entry, "Invalid FIR Number!", 'red')
            return

        if cnic_to_delete in fir_data:
            initial_count = len(fir_data[cnic_to_delete])
            fir_data[cnic_to_delete] = [
                fir for fir in fir_data[cnic_to_delete]
                if fir.get('fir_number') != fir_num_to_delete
            ]
            if len(fir_data[cnic_to_delete]) < initial_count:
                if not fir_data[cnic_to_delete]: # If no FIRs left for this CNIC, remove the CNIC entry
                    del fir_data[cnic_to_delete]
                save_fir_data(fir_data)
                self.update_output(self.output_area_search, f"FIR '{fir_num_to_delete}' for CNIC '{cnic_to_delete}' successfully deleted.", 'green')
                self.show_temp_message(self.delete_fir_button, "FIR Deleted!", 'green')
                self.clear_search_fields_gui() # Clear fields after successful deletion
            else:
                self.update_output(self.output_area_search, f"FIR '{fir_num_to_delete}' not found for CNIC '{cnic_to_delete}'.", 'crimson')
        else:
            self.update_output(self.output_area_search, f"No FIRs found for CNIC '{cnic_to_delete}'.", 'crimson')

    def view_all_firs(self):
        self.update_output(self.output_area_search, "", append=False) # Clear previous results
        if not fir_data:
            self.update_output(self.output_area_search, "No FIRs currently registered in the system.", 'crimson')
            return

        self.update_output(self.output_area_search, "--- All Registered FIRs ---", False, 'header')
        fir_count = 0
        for cnic, fir_list in fir_data.items():
            for fir in fir_list:
                fir_count += 1
                self.update_output(self.output_area_search, f"\n--- FIR Details {fir_count} ---", True, 'darkred', 'header')
                self.update_output(self.output_area_search, f"FIR Number: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('fir_number', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Complainant Details ---", True, 'complainant_section_header')
                self.update_output(self.output_area_search, f"Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('complainant_name', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Father's Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('complainant_father_name', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Accused Details ---", True, 'accused_section_header')
                self.update_output(self.output_area_search, f"CNIC: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('cnic', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('accused_name', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Father's Name: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('accused_father_name', 'N/A')}", True, font_tag='fir_detail_value')

                self.update_output(self.output_area_search, f"\n--- Case Details ---", True, 'darkred', 'header')
                self.update_output(self.output_area_search, f"Date: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('fir_date', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Reason: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('reason', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Bail Status: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('bail_status', 'N/A')}", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, f"Punishment: ", True, font_tag='fir_detail_label')
                self.update_output(self.output_area_search, f"{fir.get('punishment', 'N/A')}", True, font_tag='fir_detail_value')

                sections_applied = fir.get('sections', [])
                if sections_applied:
                    self.update_output(self.output_area_search, f"Applied Sections:", True, font_tag='fir_detail_label')
                    for section in sections_applied:
                        law_info = laws.get(section, {})
                        title = law_info.get('title', 'Unknown Title')
                        act = law_info.get('act', 'Unknown Act')
                        punishment_info = law_info.get('punishment', 'N/A')
                        self.update_output(self.output_area_search, f"  - {section} ({act}): {title} (Punishment: {punishment_info})", True, font_tag='section_info')
                else:
                    self.update_output(self.output_area_search, f"Applied Sections: N/A", True, font_tag='fir_detail_value')
                self.update_output(self.output_area_search, "\n" + "="*70 + "\n", True, 'gray') # Stronger separator between FIRs

        self.update_output(self.output_area_search, f"\nTotal FIRs: {fir_count}", True, 'green', 'header')


    def clear_search_fields_gui(self):
        self.search_cnic_entry.delete(0, tk.END)
        self._set_placeholder(self.search_cnic_entry, self.search_cnic_placeholder)
        self.search_fir_num_entry.delete(0, tk.END)
        self._set_placeholder(self.search_fir_num_entry, self.search_fir_num_placeholder)
        self.search_accused_name_entry.delete(0, tk.END)
        self._set_placeholder(self.search_accused_name_entry, self.search_accused_name_placeholder)
        self.search_accused_father_entry.delete(0, tk.END)
        self._set_placeholder(self.search_accused_father_entry, self.search_accused_father_placeholder)
        self.update_output(self.output_area_search, "")

    def clear_add_fields_gui(self, keep_cnic=False):
        if not keep_cnic:
            self.add_cnic_entry.delete(0, tk.END)
            self._set_placeholder(self.add_cnic_entry, self.add_cnic_placeholder)
        self.add_fir_num_entry.delete(0, tk.END)
        self._set_placeholder(self.add_fir_num_entry, self.add_fir_num_placeholder)
        self.add_complainant_name_entry.delete(0, tk.END)
        self._set_placeholder(self.add_complainant_name_entry, self.add_complainant_name_placeholder)
        self.add_complainant_father_entry.delete(0, tk.END)
        self._set_placeholder(self.add_complainant_father_entry, self.add_complainant_father_placeholder)
        self.add_accused_name_entry.delete(0, tk.END)
        self._set_placeholder(self.add_accused_name_entry, self.add_accused_name_placeholder)
        self.add_accused_father_entry.delete(0, tk.END)
        self._set_placeholder(self.add_accused_father_entry, self.add_accused_father_placeholder)
        self.add_fir_date_entry.delete(0, tk.END)
        self._set_placeholder(self.add_fir_date_entry, self.add_fir_date_placeholder)
        self.add_reason_entry.delete(0, tk.END)
        self._set_placeholder(self.add_reason_entry, self.add_reason_placeholder)
        self.add_sections_entry.delete(0, tk.END)
        self._set_placeholder(self.add_sections_entry, self.add_sections_placeholder)
        self.add_bail_status_combobox.set("N/A")
        self.add_punishment_entry.delete(0, tk.END)
        self._set_placeholder(self.add_punishment_entry, self.add_punishment_placeholder)
        self.update_output(self.add_output_area, "")

# --- Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = FIRApp(root)
    root.mainloop()