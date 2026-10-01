import klayout.db as db
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch

ly = db.Layout()
ly.read("results/uart_tx.gds")
top = ly.top_cell()
dbu = ly.dbu

layers = [
    (64, 20, "nwell", "#c8b88a"),
    (65, 20, "diff",  "#4caf50"),
    (66, 20, "poly",  "#e53935"),
    (67, 20, "li1",   "#fb8c00"),
    (68, 20, "met1",  "#1e88e5"),
    (69, 20, "met2",  "#8e24aa"),
    (70, 20, "met3",  "#00acc1"),
    (71, 20, "met4",  "#fdd835"),
]

fig, ax = plt.subplots(figsize=(10, 11.5))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
handles = []

for lnum, dt, name, color in layers:
    idx = ly.find_layer(lnum, dt)
    if idx is None:
        print(name, "not found")
        continue
    region = db.Region(top.begin_shapes_rec(idx))
    region.merge()
    n = 0
    for poly in region.each():
        pts = [(p.x * dbu, p.y * dbu) for p in poly.each_point_hull()]
        ax.add_patch(Polygon(pts, closed=True, facecolor=color,
                             edgecolor="none", alpha=0.55))
        n += 1
    print(name, n, "polygons")
    handles.append(Patch(facecolor=color, label=name))

bb = top.dbbox()
ax.set_xlim(bb.left, bb.right)
ax.set_ylim(bb.bottom, bb.top)
ax.set_aspect("equal")
ax.axis("off")
ax.legend(handles=handles, loc="lower right", facecolor="black",
          labelcolor="white", fontsize=8)
fig.savefig("results/uart_tx_layout.png", dpi=150,
            facecolor="black", bbox_inches="tight")
print("saved")