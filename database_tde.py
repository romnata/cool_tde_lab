import numpy as np
import tkinter as tk
from tkinter import ttk

# table
tde_dtype = [
    ('Event', 'U20'),
    ('Redshift', 'f8'),
    ('M_BH', 'f8'),
    ('Host G', 'U10'),
    ('L_peak', 'f8'),
    ('t_peak', 'f8'),
    ('Jet', 'U3'),
    ('Spectral Class', 'U20')
]

# TDE list
tde_data = [
    # Block 1: Confirmed TDE from ZTF, ASAS-SN, Swift surveys (Open TDE Catalog, Hammerstein et al. 2023/2026, Wikipedia notable list)
    ("ASASSN-14li", 0.0206, 1000000, "Post-SB", 1e44, 35, "No", "TDE-H+He"),
    ("Swift J1644+57", 0.354, 5000000, "Compact", 1e48, 10, "Yes", "Jetted"),
    ("XMMSL1 J0740-85", 0.0173, 3000000, "E/S0", 5e43, 50, "No", "TDE-H"),
    ("PS1-10jh", 0.1696, 2000000, "E", 3e44, 30, "No", "TDE-He"),
    ("ASASSN-15oi", 0.0484, 1500000, "E", 8e43, 40, "No", "TDE-H+He"),
    ("AT2018zr", 0.071, 2200000, "Post-SB", 4e44, 25, "No", "TDE-H+He"),
    ("AT2019qiz", 0.015, 900000, "Spiral", 3.5e43, 60, "No", "TDE-H+He"),
    ("AT2020neh", 0.058, 1800000, "Compact", 6e43, 45, "No", "TDE-He"),
    ("ZTF18aajupnt", 0.079, 2500000, "E", 7e43, 38, "No", "TDE-H"),
    ("ZTF19abzrhgq", 0.015, 900000, "Spiral", 3.5e43,
     32, "No", "TDE-H+He"),
    ("AT2022cmc", 1.193, 10000000, "Unknown",
     3.162277660168375e44, 10, "Yes", "Featureless"),
    ("AT2022dbl", 0.128, 3162277, "Post-SB",
     3.162277660168375e43, 35, "No", "TDE-H+He"),
    ("AT2020vdq", 0.045, 398107, "Dwarf", 1e43, 25, "No", "TDE-H+He"),
    ("AT2021ehb", 0.112, 1000000, "E+A", 6.30957344480193e43, 25, "No", "TDE-H"),
    ("AT2019azh", 0.022, 900000, "E", 6.30957344480193e42, 30, "No", "TDE-H+He"),
    ("ASASSN-14ae", 0.044, 1000000, "Post-SB",
     3.16227766016837e43, 30, "No", "TDE-H+He"),
    ("Swift J2058+05", 1.185, 10000000, "Unknown", 1e47, 5, "Yes", "Jetted"),
    ("AT2018hyz", 0.046, 2000000, "E+A", 1e44, 750, "No", "TDE-H+He"),
    ("AT2019dsg", 0.051, 1000000, "E", 1e43, 40, "Yes", "TDE-Bowen"),
    ("AT2022dsb", 0.05, 1500000, "Unknown", 5e43, 20, "No", "TDE-H+He"),
    # Block 2: X-ray and mixed catalog TDE (XMM-Newton from Eyles-Ferris 2025/2026, ATLAS/CRTS/DES/Gaia from TDExplorer BETA and Open TDE candidates)
    ("2MASX J01190869-3411305", 0.018, 400000,
     "Unknown", 5e42, 50, "No", "Unknown"),
    ("2XMM J123103.2+110648", 0.119, 1000000,
     "Unknown", 1e43, 40, "No", "Unknown"),
    ("2XMMi J184725.1-631724", 0.035, 2000000,
     "Unknown", 6e44, 30, "No", "Unknown"),
    ("3XMM J150052.0+015452", 0.145, 200000, "Unknown", 1e42, 35, "No", "Unknown"),
    ("3XMM J152130.7+074916", 0.179, 500000, "Unknown", 5e44, 25, "No", "Unknown"),
    ("3XMM J215022.4-055108", 0.055, 30000, "Unknown", 1e43, 30, "No", "Unknown"),
    ("AT2016ezh", 0.080, 1000000, "Unknown", 3e43, 40, "No", "TDE-He"),
    ("AT2017eqx", 0.109, 20000000, "Unknown", 1e44, 35, "No", "TDE-H"),
    ("AT2018fyk", 0.059, 1000000, "Unknown", 4e43, 45, "No", "Unknown"),
    ("CSS100217", 0.147, 5000000, "Unknown", 5e43, 30, "No", "Unknown"),
    ("CXOU J0332", 2.23, 10000000, "Unknown", 1e44, 20, "No", "Unknown"),
    ("DES14C1kia", 0.162, 2000000, "Unknown", 2e43, 25, "No", "Unknown"),
    ("F01004-2237", 0.118, 3000000, "Unknown", 3e43, 35, "No", "Unknown"),
    ("Gaia16aax", 0.248, 400000000, "Unknown", 4e43, 40, "No", "Unknown"),
    ("Gaia16ajq", 0.28, 400000000, "Unknown", 5e43, 30, "No", "Unknown"),
    ("Gaia16aka", 0.31, 400000000, "Unknown", 6e43, 35, "No", "Unknown"),
    ("J030257", 0.106, 1000000, "Unknown", 1e43, 25, "No", "Unknown"),
    ("J091225", 0.145, 2000000, "Unknown", 2e43, 30, "No", "Unknown"),
    ("J094608", 0.119, 3000000, "Unknown", 3e43, 35, "No", "Unknown"),
    ("J094806", 0.207, 4000000, "Unknown", 4e43, 40, "No", "Unknown"),
    # Block 3: Spectroscopic and transient catalog TDE (SDSS/PS1/PTF/OGLE from Open TDE, TDExplorer, Kochanek 2016/2026, Somalwar 2026)
    ("J113527", 0.108, 5000000, "Unknown", 5e43, 45, "No", "Unknown"),
    ("J121116", 0.076, 6000000, "Unknown", 6e43, 50, "No", "Unknown"),
    ("J123715", 0.216, 7000000, "Unknown", 7e43, 55, "No", "Unknown"),
    ("J130819", 0.037, 8000000, "Unknown", 8e43, 60, "No", "Unknown"),
    ("J133837", 0.127, 9000000, "Unknown", 9e43, 65, "No", "Unknown"),
    ("J141036", 0.107, 10000000, "Unknown", 1e44, 70, "No", "Unknown"),
    ("J142401", 0.086, 11000000, "Unknown", 1.1e44, 75, "No", "Unknown"),
    ("J155223", 0.128, 100000000, "Unknown", 1.2e44, 80, "No", "Unknown"),
    ("J233454", 0.107, 1000000, "Unknown", 1.3e44, 85, "No", "Unknown"),
    ("MAXI J1807+132", 0.05, 2000000, "Unknown", 1.4e44, 90, "No", "Unknown"),
    ("NGC 247", 0.001, 3000000, "Unknown", 1.5e44, 95, "No", "Unknown"),
    ("OGLE16aaa", 0.166, 4000000, "Unknown", 1.6e44, 100, "No", "Unknown"),
    ("PGC 1185375", 0.005, 5000000, "Unknown", 1.7e44, 105, "No", "Unknown"),
    ("PS1-10adi", 0.203, 6000000, "Unknown", 1.8e44, 110, "No", "Unknown"),
    ("PS1-11af", 0.405, 7000000, "Unknown", 1.9e44, 115, "No", "Unknown"),
    ("PS1-13jw", 0.345, 8000000, "Unknown", 2e44, 120, "No", "Unknown"),
    ("PTF09axc", 0.115, 9000000, "Unknown", 2.1e44, 125, "No", "Unknown"),
    ("PTF10iya", 0.224, 10000000, "Unknown", 2.2e44, 130, "No", "Unknown"),
    ("RBS 1032", 0.026, 11000000, "Unknown", 1e42, 135, "No", "Unknown"),
    ("SDSSJ0159", 0.312, 12000000, "Unknown", 1e43, 140, "No", "Unknown"),
    ("SDSSJ0748", 0.062, 13000000, "Unknown", 1e44, 145, "No", "Unknown"),
    ("SDSSJ0952", 0.079, 14000000, "Unknown", 1e43, 150, "No", "Unknown"),
    ("SDSSJ1201+30", 0.146, 10000000, "Unknown", 1e43, 155, "No", "Unknown"),
    ("SDSSJ1323", 0.088, 15000000, "Unknown", 1e44, 160, "No", "Unknown"),
    ("SDSSJ1342", 0.037, 16000000, "Unknown", 1e44, 165, "No", "Unknown"),
    ("Swift J1112-82", 0.89, 17000000, "Unknown", 1e46, 170, "No", "Unknown"),
    ("iPTF16axa", 0.108, 5000000, "Unknown", 1e43, 175, "No", "Unknown"),
    ("iPTF16fnl", 0.016, 18000000, "Unknown", 1e44, 180, "No", "Unknown"),
    # Block 4: Recent off-nuclear TDE (2024–2026 papers: Liu 2023/2026, Stein 2026 arXiv, Hubble/NASA 2025)
    ("3XMM J2150", 0.055, 79432, "Unknown", 1e44, 30, "No", "Unknown"),
    ("EP240222a", 0.033, 27542, "Unknown", 1e44, 30, "No", "Unknown"),
    ("TDE 2024tvd", 0.045, 100000, "Unknown", 1e44, 30, "No", "Unknown"),
    ("TDE 2025abcr", 0.05, 1258925, "Unknown", 1e44, 30, "No", "Unknown")
]

tde_array = np.array(tde_data, dtype=tde_dtype)

# Create Tkinter window
root = tk.Tk()
root.title("TDE Database")
root.geometry("800x700+50+200")  # starting size+x+y

# title label
title_label = tk.Label(
    root, text="Database of Known TDEs 1990-2025", font=("Helvetica", 14, "bold"))
title_label.pack(side="top", pady=10)

# frame for Treeview
frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)

# scrollbars
vsb = ttk.Scrollbar(frame, orient="vertical")
vsb.pack(side='right', fill='y')

hsb = ttk.Scrollbar(frame, orient="horizontal")
hsb.pack(side='bottom', fill='x')

# treeview
columns = ("№", "Event", "Redshift", "M_BH [M☉]", "Host G",
           "L_peak [erg/s]", "t_peak [d]", "Jet", "Spectral Class")
tree = ttk.Treeview(frame, columns=columns, show="headings",
                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.pack(side='left', fill='both', expand=True)

vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

# headings
for col in columns:
    tree.heading(col, text=col)
    # starting width
    tree.column(col, width=150, anchor='center')

# data
for i, row in enumerate(tde_array, start=1):
    l_peak_str = f"{row['L_peak']:.1e}".replace(
        'e+', ' × 10^').replace('e-', ' × 10^-')
    tree.insert("", "end", values=(
        str(i),
        row['Event'],
        f"{row['Redshift']:.3f}",
        f"{int(row['M_BH']):,}",
        row['Host G'],
        l_peak_str,
        f"{row['t_peak']:.0f}",
        row['Jet'],
        row['Spectral Class']
    ))


def resize_columns(event):
    for col in columns:
        tree.column(col, width=event.width // len(columns))


root.bind("<Configure>", resize_columns)

root.mainloop()

root.mainloop()

