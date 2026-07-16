import math

MELEE_R = 5.0
RANGED_R = 30.0
MOVE_SPEED = 5.0
CONE = 0.9239       # cos(22.5 deg)
ARENA_MIN = 0.0
ARENA_MAX = 100.0
MARGIN = 10.0


def _unit(dx, dy):
    d = math.hypot(dx, dy)
    return (dx / d, dy / d) if d > 1e-9 else (1.0, 0.0)


def decide(state, memory):
    # Read state
    ox, oy = state["own_position"]["x"], state["own_position"]["y"]
    rx, ry = state["opponent_position"]["x"], state["opponent_position"]["y"]
    dx, dy = rx - ox, ry - oy
    dist = math.hypot(dx, dy)

    hp = state["own_hp"]
    opp_hp = state["opponent_hp"]
    cd = state["ranged_cooldown_remaining"]
    uses = state["ranged_uses_remaining"]

    # Aim check
    fx, fy = state["own_facing"]["dx"], state["own_facing"]["dy"]
    fl = math.hypot(fx, fy)
    aim = (fx * dx + fy * dy) / (fl * dist) if dist > 0.1 else 1.0
    aimed = aim >= CONE

    # Opponent facing — info advantage
    ofx, ofy = state["opponent_facing"]["dx"], state["opponent_facing"]["dy"]
    to_me = math.hypot(ox - rx, oy - ry)
    if to_me > 0.1:
        opp_aim = (ofx * (ox - rx) + ofy * (oy - ry)) / (math.hypot(ofx, ofy) * to_me)
    else:
        opp_aim = 1.0
    opp_faces_away = opp_aim <= -CONE  # back is to us

    # 1. RANGED — best damage (15), fire when ready and aimed
    if uses > 0 and cd == 0 and dist <= RANGED_R:
        if aimed:
            return {"type": "attack_ranged"}, {"hp": hp, "opp_hp": opp_hp}
        return {"type": "rotate", "dx": dx, "dy": dy}, {"hp": hp, "opp_hp": opp_hp}

    # 2. MELEE — aim first, then strike
    if dist <= MELEE_R:
        if aimed:
            return {"type": "attack_melee"}, {"hp": hp, "opp_hp": opp_hp}
        return {"type": "rotate", "dx": dx, "dy": dy}, {"hp": hp, "opp_hp": opp_hp}

    # 3. Rotate to face opponent if needed before moving
    if not aimed:
        return {"type": "rotate", "dx": dx, "dy": dy}, {"hp": hp, "opp_hp": opp_hp}

    # 4. MOVE toward opponent with wall avoidance
    ux, uy = _unit(dx, dy)

    # Avoid walls
    steer_x, steer_y = 0.0, 0.0
    if ox < MARGIN:
        steer_x += 1.0
    if ox > ARENA_MAX - MARGIN:
        steer_x -= 1.0
    if oy < MARGIN:
        steer_y += 1.0
    if oy > ARENA_MAX - MARGIN:
        steer_y -= 1.0
    if steer_x != 0.0 or steer_y != 0.0:
        steer_x, steer_y = _unit(steer_x, steer_y)
        ux = ux * 0.7 + steer_x * 0.3
        uy = uy * 0.7 + steer_y * 0.3
        ux, uy = _unit(ux, uy)

    return {"type": "move", "dx": ux * MOVE_SPEED, "dy": uy * MOVE_SPEED}, {"hp": hp, "opp_hp": opp_hp}
