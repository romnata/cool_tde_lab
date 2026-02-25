import numpy as np
import matplotlib.pyplot as plt

# last 10 TDE
tde_dtype = [
    ('Event', 'U20'),
    ('Redshift', 'f8'),
    ('M_BH', 'f8'),
    ('Host', 'U10'),
    ('L_peak', 'f8'),
    ('t_peak', 'f8'),
    ('Jet', 'U3')
]

tde_data = [
    ("ASASSN-14li", 0.0206, 1e6, "E", 1e44, 35, "No"),
    ("Swift J1644+57", 0.354, 5e6, "Unknown", 1e48, 10, "Yes"),
    ("XMMSL1 J0740-85", 0.0173, 3e6, "E/S0", 5e43, 50, "No"),
    ("PS1-10jh", 0.1696, 2e6, "E", 3e44, 30, "No"),
    ("ASASSN-15oi", 0.0484, 1.5e6, "E", 8e43, 40, "No"),
    ("AT2018zr", 0.071, 2.2e6, "S0", 4e44, 25, "No"),
    ("AT2019qiz", 0.015, 9e5, "E", 3.5e43, 60, "No"),
    ("AT2020neh", 0.058, 1.8e6, "S0", 6e43, 45, "No"),
    ("ZTF18aajupnt", 0.079, 2.5e6, "E", 7e43, 38, "No"),
    ("ZTF19abzrhgq", 0.102, 3.1e6, "E", 9e43, 32, "No")
]

tde_array = np.array(tde_data, dtype=tde_dtype)


# data matplotlib.table
columns = ["Event", "z", "M_BH [M☉]", "Host",
           "L_peak [erg/s]", "t_peak [d]", "Jet"]

cell_text = []
for row in tde_array:
    cell_text.append([
        row['Event'],
        f"{row['Redshift']:.3f}",
        f"{row['M_BH']:.2e}",
        row['Host'],
        f"{row['L_peak']:.2e}",
        f"{row['t_peak']:.0f}",
        row['Jet']
    ])


# painting the table
fig, ax = plt.subplots(figsize=(4.2, 4))
ax.axis('off')

table = ax.table(cellText=cell_text, colLabels=columns,
                 cellLoc='center', loc='center')

table.auto_set_font_size(False)
table.set_fontsize(9)
table.auto_set_column_width(col=list(range(len(columns))))

table.scale(1.05, 1.45)

plt.subplots_adjust(left=0.005,
                    right=0.995,
                    top=0.88,
                    bottom=0.06)

# title
fig.suptitle("10 most recent observable TDEs",
             fontsize=14, fontweight='bold',
             y=0.85)

# styles
for i in range(len(cell_text) + 1):
    for j in range(len(columns)):
        cell = table[(i, j)]
        if i == 0:
            cell.set_facecolor('lightgray')
            cell.set_text_props(weight='bold')
        elif i % 2 == 0:
            cell.set_facecolor('#f0f0f0')

manager = plt.get_current_fig_manager()
manager.window.setGeometry(600, 600, 500, 350)   # x, y, width, height

# window
fig.tight_layout(pad=3.0)
plt.show()
