import tkinter as tk
from tkinter import ttk


root = tk.Tk()
root.title("TDE Database Manual")
root.geometry("600x600+900+200")   # starting size+x+y

# title
title_label = tk.Label(root,
                       text="TDE Database Manual",
                       font=("Helvetica", 14, "bold"))
title_label.pack(side="top", pady=10)

frame = ttk.Frame(root)
frame.pack(fill='both', expand=True)

# scrollbars
vsb = ttk.Scrollbar(frame, orient="vertical")
vsb.pack(side='right', fill='y')
hsb = ttk.Scrollbar(frame, orient="horizontal")
hsb.pack(side='bottom', fill='x')

# treeview
columns = ("Parameter", "Description")
tree = ttk.Treeview(frame, columns=columns, show="headings",
                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.pack(side='left', fill='both', expand=True)

vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

# styles
style = ttk.Style()


style.configure("Treeview",
                font=("Helvetica", 9),
                rowheight=135)

style.configure("Treeview.Heading",

                font=("Helvetica", 11, "bold"),
                anchor="center")

# columns
tree.column("Parameter",   width=50, anchor='center',
            minwidth=50)
tree.column("Description", width=1050, anchor='w',
            minwidth=800)

tree.heading("Parameter",   text="Parameter",   anchor="w")
tree.heading("Description", text="Description", anchor="w")


# data
manual_data = [
    ("Event",
     "Name of the Tidal Disruption Event."),

    ("Redshift",
     "Measure of the distance to the host galaxy.\n"
     "Higher z = farther away and earlier the TDE happened."),

    ("M_BH \n[M☉]",
     "Estimated mass of the Black Hole that disrupted the star.\n"
     "In solar masses (M☉). Typical range: 10^5 – 10^8 M☉."),

    ("Host",
     "Morphological type of the host galaxy:\n"
     "• E = Elliptical (oval, no spiral arms, little gas/star formation)\n"
     "• S0 = Lenticular (transition between elliptical and spiral\n"
     "• Post-SB / E+A = Post-Starburst (E — elliptical-like, A — A-type stars from recent burst)\n"
     "• Spiral = Spiral (Milky-Way-like, with arms)\n"
     "• Dwarf / Compact = Small or dense\n"
     "• Unknown = Type not identified (no data or galaxy not classified)"),

    ("L_peak \n[erg/s]",
     "Peak bolometric luminosity of the TDE flare.\n"
     "Typical range: 10^42 – 10^45 erg/s\n"
     "up to 10^48 erg/s (jetted events)"),

    ("t_peak \n[d]",
     "Time from discovery to peak brightness, in days.\n"
     "(usually 10–100 days)"),

    ("Jet",
     "Yes / No — whether relativistic jets were detected.\n"
     "Jets appear in only ~1–10% of all TDE."),

    ("Spectral \nClass",
     "Optical spectroscopic classification:\n"
     "• TDE-H = broad hydrogen lines\n"
     "• TDE-He = helium only\n"
     "• TDE-H+He = both H and He (often Bowen)\n"
     "• Featureless = no lines, blue continuum\n"
     "• TDE-Bowen = strong Bowen fluorescence\n"
     "• Jetted = X-ray / radio dominated\n"
     "• Unknown = not classified")
]

# table
for param, desc in manual_data:
    tree.insert("", "end", values=(param, desc))


def resize_columns(event):
    param_w = max(50, event.width // 7)
    desc_w = max(800, event.width - param_w - 40)
    tree.column("Parameter",   width=param_w)
    tree.column("Description", width=desc_w)


root.bind("<Configure>", resize_columns)

root.mainloop()
