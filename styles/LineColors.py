import pyqtgraph as pg

DATA_VIEWER_TREE_COLORS = [
    (255, 213, 102),    # Ev
    (0, 153, 255),    # Ex
    (0,0,255),      # Ey
    (0,255,255),    # Eya
    (255,255,0),    # Eyb
    (100,100,100),  # F
    (0, 102, 0),    # Pc
    (255,0,0),      # Pcu
    (112,50,255),   # Phyd
    (0,255,255),    # Pu
    (255,0,0),      # Sc
    (255,0,255),    # Sig1
    (255,0,0),      # SigD
    (0,255,0),      # Ss
    (0,255,0),      # Su
    (255,255,0),    # Sx
    (0,0,0),        # Thyd
    (255,255,0),    # Time
    (255,0,0),      # Vhyd
    (255,255,0),    # Xa
    (0,255,0),      # Ya
    (0,0,255),      # Yb
]

DYNAMIC_MODULI_COLORS = [
    (170,0,255),    # Poiss X
    (255,0,255),    # Poiss Y
    (0,0,255),      # SHear x
    (0,104,153),    # Young_x
    (255,255,0),    # Young_y
]

STATIC_MODULI_COLORS =[
    (255,0,0),       # poiss
    (0,255,0),       # young
]

TREND_PEN = pg.mkPen(color=(72, 209, 204), width=3)

MOHR_CIRCLE_PEN = pg.mkPen(color=(0, 0, 0), width=2)
