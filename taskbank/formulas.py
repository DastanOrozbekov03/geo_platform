FORMULAS = {
    "triangle_area": lambda p: p["a"] * p["h"] / 2,
    "square_area": lambda p: p["a"] ** 2,
    "rectangle_area": lambda p: p["a"] * p["b"],
    "triangle_perimeter": lambda p: p["a"] + p["b"] + p["c"],
    "segment_sum": lambda p: p["x"] + p["y"],
    "segment_difference": lambda p: p["x"] - p["y"],
    "adjacent_angle": lambda p: 180 - p["a"],
    "vertical_angle": lambda p: p["a"],
    "triangle_angle_sum": lambda p: 180 - p["a"] - p["b"],
}