import math

ARENA_MIN = 0.0
ARENA_MAX = 100.0
MOVE_SPEED = 5.0
MELEE_RANGE = 5.0
RANGED_RANGE = 30.0
CLOSE_RANGE = 25.0
AIM_THRESHOLD = 0.95


def decide(state, memory):
    own_x = state["own_position"]["x"]
    own_y = state["own_position"]["y"]
    opp_x = state["opponent_position"]["x"]
    opp_y = state["opponent_position"]["y"]

    dx = opp_x - own_x
    dy = opp_y - own_y
    gap = math.hypot(dx, dy)

    cooldown = state["ranged_cooldown_remaining"]
    uses_left = state["ranged_uses_remaining"]

    facing_dx = state["own_facing"]["dx"]
    facing_dy = state["own_facing"]["dy"]

    facing_length = math.hypot(facing_dx, facing_dy)
    aim_dot = (facing_dx * dx + facing_dy * dy) / (facing_length * gap) if gap > 0 else 1.0

    if aim_dot < AIM_THRESHOLD:
        return {"type": "rotate", "dx": dx, "dy": dy}, memory

    if uses_left > 0 and cooldown == 0 and gap <= RANGED_RANGE:
        return {"type": "attack_ranged"}, memory

    if gap <= MELEE_RANGE:
        return {"type": "attack_melee"}, memory

    if gap < CLOSE_RANGE:
        return _move_toward(dx, dy), memory

    return _move_toward(dx, dy), memory


def _normalize(dx, dy):
    mag = math.hypot(dx, dy)
    if mag == 0:
        return 0.0, 0.0
    return dx / mag, dy / mag


def _clamp(value):
    return min(max(value, ARENA_MIN), ARENA_MAX)


def _move_toward(dx, dy):
    ux, uy = _normalize(dx, dy)
    return {
        "type": "move",
        "dx": ux * MOVE_SPEED,
        "dy": uy * MOVE_SPEED,
    }


def _move_away(own_x, own_y, opp_x, opp_y, dx, dy):
    ax, ay = _normalize(-dx, -dy)
    predicted_x = _clamp(own_x + ax * MOVE_SPEED)
    predicted_y = _clamp(own_y + ay * MOVE_SPEED)
    current_gap = math.hypot(opp_x - own_x, opp_y - own_y)
    predicted_gap = math.hypot(opp_x - predicted_x, opp_y - predicted_y)

    if predicted_gap - current_gap >= MOVE_SPEED * 0.5:
        return {
            "type": "move",
            "dx": predicted_x - own_x,
            "dy": predicted_y - own_y,
        }

    if ax == 0.0 and ay == 0.0:
        ax, ay = 1.0, 0.0
    perp_options = ((-ay, ax), (ay, -ax))
    best = max(
        perp_options,
        key=lambda p: _distance_to_nearest_wall(
            _clamp(own_x + p[0] * MOVE_SPEED),
            _clamp(own_y + p[1] * MOVE_SPEED),
        ),
    )
    px, py = best
    return {
        "type": "move",
        "dx": px * MOVE_SPEED,
        "dy": py * MOVE_SPEED,
    }


def _distance_to_nearest_wall(x, y):
    return min(x - ARENA_MIN, ARENA_MAX - x, y - ARENA_MIN, ARENA_MAX - y)
