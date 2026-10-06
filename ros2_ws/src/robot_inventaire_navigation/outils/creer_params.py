"""cree config/nav2_params.yaml a partir des parametres officiels de nav2 humble,
en ne modifiant que ce qui concerne notre robot"""
from pathlib import Path

import yaml

SOURCE = "/opt/ros/humble/share/nav2_bringup/params/nav2_params.yaml"
SORTIE = Path(__file__).resolve().parent.parent / "config" / "nav2_params.yaml"

# gabarit au sol, pare-chocs compris (0,85 x 0,65 m)
EMPRISE = "[[0.43, 0.33], [0.43, -0.33], [-0.43, -0.33], [-0.43, 0.33]]"
BASE = "base_footprint"

p = yaml.safe_load(open(SOURCE))


def tous_les_parametres(noeud):
    """les blocs ros__parameters d'un noeud, y compris les costmaps imbriquees"""
    if "ros__parameters" in noeud:
        yield noeud["ros__parameters"]
    for v in noeud.values():
        if isinstance(v, dict) and "ros__parameters" in v:
            yield v["ros__parameters"]


# temps simule et repere du robot partout
for noeud in p.values():
    for prm in tous_les_parametres(noeud):
        prm["use_sim_time"] = True
        if "robot_base_frame" in prm:
            prm["robot_base_frame"] = BASE
p["amcl"]["ros__parameters"]["base_frame_id"] = BASE

# cartes de cout : notre gabarit, allees de 1,47 m (41 cm libres de chaque cote)
for cm in ("local_costmap", "global_costmap"):
    c = p[cm][cm]["ros__parameters"]
    c.pop("robot_radius", None)
    c["footprint"] = EMPRISE
    c["inflation_layer"]["inflation_radius"] = 0.35
    # cout qui chute vite : le robot peut passer, en restant au milieu
    c["inflation_layer"]["cost_scaling_factor"] = 6.0
p["local_costmap"]["local_costmap"]["ros__parameters"]["width"] = 5
p["local_costmap"]["local_costmap"]["ros__parameters"]["height"] = 5

# suivi de chemin : pure pursuit regule, adapte a un differentiel en allees etroites
p["controller_server"]["ros__parameters"]["FollowPath"] = {
    "plugin": "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController",
    "desired_linear_vel": 0.4,
    "lookahead_dist": 0.6,
    "min_lookahead_dist": 0.3,
    "max_lookahead_dist": 0.9,
    "lookahead_time": 1.5,
    "rotate_to_heading_angular_vel": 0.6,
    "transform_tolerance": 0.2,
    "use_velocity_scaled_lookahead_dist": False,
    "min_approach_linear_velocity": 0.05,
    "approach_velocity_scaling_dist": 0.6,
    "use_collision_detection": True,
    "max_allowed_time_to_collision_up_to_carrot": 1.0,
    "use_regulated_linear_velocity_scaling": True,
    "use_cost_regulated_linear_velocity_scaling": False,
    "regulated_linear_scaling_min_radius": 0.9,
    "regulated_linear_scaling_min_speed": 0.15,
    "use_rotate_to_heading": True,
    "rotate_to_heading_min_angle": 0.785,
    "allow_reversing": False,
    "max_angular_accel": 1.5,
    "max_robot_pose_search_dist": 10.0,
}

# limites du robot : 0,4 m/s en deplacement, demarrages doux (mat lourd)
vs = p["velocity_smoother"]["ros__parameters"]
vs["max_velocity"] = [0.4, 0.0, 0.8]
vs["min_velocity"] = [-0.2, 0.0, -0.8]
vs["max_accel"] = [0.3, 0.0, 1.0]
vs["max_decel"] = [-0.5, 0.0, -1.5]

SORTIE.parent.mkdir(exist_ok=True)
yaml.safe_dump(p, open(SORTIE, "w"), sort_keys=False)
print("parametres ecrits dans", SORTIE)
