"""Render a GDS layout to a PNG with KLayout (headless, no GUI needed).

Usage (from the repo root, with the repo's .venv active):
    python designs/matrix_mult/plot_layout.py
    python designs/matrix_mult/plot_layout.py <input.gds> <output.png>
"""
import sys
from pathlib import Path

import klayout.db as kdb
import klayout.lay as klay

HERE = Path(__file__).resolve().parent
DEFAULT_GDS = HERE / "results" / "matrix_mult.gds"
DEFAULT_PNG = HERE / "results" / "matrix_mult_layout.png"
IMAGE_SIZE = 2400  # pixels (square)

# (GDS layer, datatype, name, RGB colour) in drawing order, bottom to top
LAYERS = [
    (235, 4, "die boundary", 0xFFFFFF),
    (64, 20, "nwell",  0x2E4A2E),
    (65, 20, "diff",   0x3A7D44),
    (66, 20, "poly",   0xC0392B),
    (67, 20, "li1",    0xB8860B),
    (68, 20, "met1",   0x3B6FD4),
    (69, 20, "met2",   0xD4A017),
    (70, 20, "met3",   0x2EAD6B),
    (71, 20, "met4",   0xA64DD1),
    (72, 20, "met5",   0xE0E0E0),
]


def main():
    gds = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GDS
    png = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PNG
    if not gds.exists():
        sys.exit(f"GDS not found: {gds}")

    view = klay.LayoutView()
    view.load_layout(str(gds), True)

    for layer, datatype, name, rgb in LAYERS:
        node = klay.LayerPropertiesNode()
        node.source = f"{layer}/{datatype}@1"
        node.name = name
        node.fill_color = rgb
        node.frame_color = rgb
        node.dither_pattern = 0 if layer != 235 else 1
        view.insert_layer(view.end_layers(), node)

    view.max_hier()     # show all hierarchy levels (the cells, not just boxes)
    view.zoom_fit()
    view.set_config("background-color", "#101010")
    view.set_config("grid-visible", "false")
    view.save_image(str(png), IMAGE_SIZE, IMAGE_SIZE)
    print(f"Wrote {png}")


if __name__ == "__main__":
    main()
