"""genere les maillages colores (.dae) du robot, dans le repere de chaque lien de l'urdf

mat : fourreau fixe dans le corps + 2 segments emboites (tubes carres creux)
chaque segment porte a son sommet une tete, d'ou descend un rail de chaque cote
rails du segment 1 en x = -0.05, rails du segment 2 en x = +0.05 : ils ne se croisent jamais
"""
from pathlib import Path

import collada
import numpy as np
import trimesh
from collada import asset, geometry, material, scene, source
from shapely.geometry import box as rect

SORTIE = Path(__file__).resolve().parent.parent / "meshes"

BLANC = (238, 239, 241)
SOCLE = (62, 64, 70)
NOIR = (26, 26, 28)
ANTHRACITE = (48, 50, 55)
ALU = (190, 194, 200)
ORANGE = (240, 110, 20)
JAUNE = (245, 200, 20)
ROUGE = (210, 30, 30)
VERT = (40, 190, 70)
LED = (250, 250, 232)
JANTE = (150, 152, 158)
VERRE = (25, 35, 70)

# ---------- cotes du mat (repere base_link, en m) ----------
FOURREAU = dict(cote=0.20, ep=0.006, z0=0.10, z1=1.49)
S1 = dict(cote=0.16, ep=0.006, long=1.55, tete=0.19)
S2 = dict(cote=0.12, ep=0.006, long=1.47, tete=0.15)
RAIL_Y = 0.12          # axe des rails, hors du fourreau
RAIL_X1, RAIL_X2 = -0.05, 0.05
RAIL1 = (0.82, 1.50)   # bas, haut du rail du segment 1 (repere segment)
RAIL2 = (0.50, 1.42)


# ---------- formes de base ----------

def prisme(lx, ly, z0, z1, r, cx=0.0, cy=0.0):
    """boite aux aretes verticales arrondies"""
    r = min(r, lx / 2 - 1e-4, ly / 2 - 1e-4)
    p = rect(cx - lx / 2 + r, cy - ly / 2 + r, cx + lx / 2 - r, cy + ly / 2 - r).buffer(r, resolution=10)
    m = trimesh.creation.extrude_polygon(p, z1 - z0)
    m.apply_translation((0, 0, z0))
    return m


def tube(cote, ep, z0, z1, r=0.01):
    return moins(prisme(cote, cote, z0, z1, r), prisme(cote - 2 * ep, cote - 2 * ep, z0 - 0.01, z1 + 0.01, r - ep / 2))


def boite(sx, sy, sz, x=0.0, y=0.0, z=0.0):
    m = trimesh.creation.box((sx, sy, sz))
    m.apply_translation((x, y, z))
    return m


def cylindre(r, h, axe="z", x=0.0, y=0.0, z=0.0):
    m = trimesh.creation.cylinder(radius=r, height=h, sections=48)
    if axe == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0)))
    elif axe == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, (0, 1, 0)))
    m.apply_translation((x, y, z))
    return m


def moins(a, *b):
    return trimesh.boolean.difference([a, *b], engine="manifold")


def union(*m):
    return trimesh.boolean.union(list(m), engine="manifold")


# ---------- export collada ----------

def exporter(parties, nom):
    doc = collada.Collada()
    doc.assetInfo.upaxis = asset.UP_AXIS.Z_UP
    noeuds = []
    for i, (m, rgb) in enumerate(parties):
        m = m.copy()
        m.fix_normals()
        c = tuple(v / 255 for v in rgb)
        # gazebo s'appuie sur l'ambiante : on la met proche de la diffuse
        eff = material.Effect(f"eff{i}", [], "phong",
                              diffuse=c + (1.0,), ambient=tuple(0.8 * v for v in c) + (1.0,),
                              specular=(0.2, 0.2, 0.2, 1.0), shininess=25.0)
        mat = material.Material(f"mat{i}", f"mat{i}", eff)
        doc.effects.append(eff)
        doc.materials.append(mat)
        vs = source.FloatSource(f"v{i}", m.vertices.flatten(), ("X", "Y", "Z"))
        ns = source.FloatSource(f"n{i}", m.face_normals.flatten(), ("X", "Y", "Z"))
        g = geometry.Geometry(doc, f"g{i}", f"g{i}", [vs, ns])
        entrees = source.InputList()
        entrees.addInput(0, "VERTEX", f"#v{i}")
        entrees.addInput(1, "NORMAL", f"#n{i}")
        idx = np.zeros((len(m.faces), 3, 2), dtype=int)
        idx[:, :, 0] = m.faces
        idx[:, :, 1] = np.arange(len(m.faces))[:, None]
        g.primitives.append(g.createTriangleSet(idx.flatten(), entrees, f"m{i}"))
        doc.geometries.append(g)
        noeuds.append(scene.GeometryNode(g, [scene.MaterialNode(f"m{i}", mat, inputs=[])]))
    sc = scene.Scene("scene", [scene.Node("piece", children=noeuds)])
    doc.scenes.append(sc)
    doc.scene = sc
    SORTIE.mkdir(exist_ok=True)
    doc.write(str(SORTIE / f"{nom}.dae"))


# ---------- corps ----------

L, W, H = 0.80, 0.60, 1.50
R_PLAN = 0.17           # grands arrondis en plan
R_HAUT = 0.06           # conge du dessus
Z_SOCLE = 0.30
OUVERTURE = (0.20, 0.36)  # passage du mat et de ses rails dans le capot


def coque_pleine(retrait=0.0, z_bas=Z_SOCLE, z_haut=H):
    """coque blanche, conge du dessus approche par couches"""
    morceaux = [prisme(L - 2 * retrait, W - 2 * retrait, z_bas, z_haut - R_HAUT, R_PLAN - retrait)]
    n = 8
    for k in range(1, n + 1):
        t0, t1 = (k - 1) / n * np.pi / 2, k / n * np.pi / 2
        za = z_haut - R_HAUT + R_HAUT * np.sin(t0)
        zb = z_haut - R_HAUT + R_HAUT * np.sin(t1)
        off = R_HAUT * (1 - np.cos(t1)) + retrait
        morceaux.append(prisme(L - 2 * off, W - 2 * off, za, zb, R_PLAN - off))
    return union(*morceaux)


def passages_roues():
    return [cylindre(0.135, 0.24, "y", 0, s * 0.31, 0.05) for s in (1, -1)]


def corps():
    ext = coque_pleine()
    interieur = coque_pleine(retrait=0.012, z_bas=Z_SOCLE - 0.01, z_haut=H - 0.012)
    trou = prisme(*OUVERTURE, H - 0.1, H + 0.1, 0.04)
    coque = moins(ext, interieur, trou)

    socle = moins(prisme(L + 0.02, W + 0.02, 0.0, Z_SOCLE - 0.01, R_PLAN + 0.01),
                  *passages_roues(),
                  boite(0.24, 0.24, 0.3, 0, 0, 0.25))           # puits du fourreau
    pare_chocs = moins(prisme(L + 0.05, W + 0.05, 0.02, 0.10, R_PLAN + 0.025), *passages_roues())
    joint = moins(prisme(L - 0.01, W - 0.01, Z_SOCLE - 0.01, Z_SOCLE + 0.005, R_PLAN - 0.005),
                  prisme(L - 0.06, W - 0.06, Z_SOCLE - 0.02, Z_SOCLE + 0.02, R_PLAN - 0.03))
    support_lidar = boite(0.08, 0.10, 0.06, 0.42, 0, 0.15)

    fourreau = tube(FOURREAU["cote"], FOURREAU["ep"], FOURREAU["z0"], FOURREAU["z1"])
    cadre = moins(prisme(0.36, 0.52, H - 0.004, H + 0.004, 0.06), prisme(*OUVERTURE, H - 0.1, H + 0.1, 0.04))

    parties = [(coque, BLANC), (socle, SOCLE), (pare_chocs, NOIR), (joint, NOIR),
               (support_lidar, NOIR), (fourreau, ANTHRACITE), (cadre, ANTHRACITE)]

    for s in (1, -1):
        # platines noires des cameras du corps et bandeau led vertical
        for z in (0.45, 1.22):
            parties.append((boite(0.07, 0.004, 0.12, 0.22, s * (W / 2 + 0.002), z), NOIR))
        parties.append((boite(0.015, 0.006, 0.95, 0.30, s * (W / 2 + 0.003), 0.87), LED))
        # arrets d'urgence sur le dessus, coins arriere
        parties.append((cylindre(0.035, 0.012, "z", -0.28, s * 0.20, H + 0.006), JAUNE))
        parties.append((cylindre(0.028, 0.03, "z", -0.28, s * 0.20, H + 0.027), ROUGE))

    # face avant : platine de la camera avant et bandeau led
    parties.append((boite(0.004, 0.12, 0.06, L / 2 + 0.002, 0, 1.40), NOIR))
    parties.append((boite(0.006, 0.30, 0.012, L / 2 + 0.003, 0, 1.32), LED))

    # colonne lumineuse a l'arriere du capot
    z = H
    for h, r, c in [(0.03, 0.025, ANTHRACITE), (0.045, 0.022, VERT),
                    (0.045, 0.022, JAUNE), (0.045, 0.022, ROUGE), (0.01, 0.02, ANTHRACITE)]:
        parties.append((cylindre(r, h, "z", -0.30, 0, z + h / 2), c))
        z += h
    exporter(parties, "corps")
    return parties


# ---------- mat ----------

def segment(nom, s, rail_x, rail):
    long, cote, tete = s["long"], s["cote"], s["tete"]
    parties = [(tube(cote, s["ep"], 0, long), ALU),
               # tete : bague autour du sommet du tube
               (tube(tete, (tete - cote) / 2 + s["ep"], long - 0.06, long), ANTHRACITE)]
    if nom == "mat_2":
        parties.append((prisme(tete, tete, long, long + 0.01, 0.01), ANTHRACITE))   # chapeau
    for sg in (1, -1):
        # potence de la tete jusqu'au rail, puis le rail qui descend
        y_int = tete / 2 - 0.005
        parties.append((boite(0.03, RAIL_Y + 0.01 - y_int, 0.05,
                              rail_x, sg * (y_int + RAIL_Y + 0.01) / 2, long - 0.03), ORANGE))
        parties.append((boite(0.02, 0.02, rail[1] - rail[0], rail_x, sg * RAIL_Y,
                              (rail[0] + rail[1]) / 2), ORANGE))
        parties.append((boite(0.026, 0.026, 0.01, rail_x, sg * RAIL_Y, rail[0] - 0.005), NOIR))
    exporter(parties, nom)
    return parties


def roue():
    exporter([(cylindre(0.1, 0.05, "y"), NOIR),
              (cylindre(0.065, 0.052, "y"), JANTE),
              (cylindre(0.025, 0.056, "y"), ANTHRACITE)], "roue")


def camera():
    b = prisme(0.09, 0.03, -0.0125, 0.0125, 0.008)
    b.apply_transform(np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]))
    parties = [(b, NOIR)]
    for y, r in [(-0.03, 0.006), (0.0, 0.007), (0.03, 0.006)]:
        parties.append((cylindre(r, 0.004, "x", 0.0135, y, 0), VERRE))
    exporter(parties, "camera")
    return parties


def lidar():
    exporter([(cylindre(0.04, 0.025, "z", z=-0.0075), NOIR),
              (cylindre(0.035, 0.015, "z", z=0.0125), ANTHRACITE)], "lidar")


if __name__ == "__main__":
    for f in SORTIE.glob("collier_*.dae"):
        f.unlink()
    corps()
    segment("mat_1", S1, RAIL_X1, RAIL1)
    segment("mat_2", S2, RAIL_X2, RAIL2)
    roue()
    camera()
    lidar()
    print("maillages generes dans", SORTIE)
