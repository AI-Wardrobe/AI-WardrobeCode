
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Item:
    type: str       # e.g., "top", "bottom"
    color: str
    image_path: str
    tags: str

def is_cool(temp_f: float) -> bool:
    return temp_f <= 60

def basic_color_ok(top_color: str, bottom_color: str) -> bool:
    # Very coarse check: avoid very similar dark combos
    def is_dark(rgb_str: str) -> bool:
        nums = [int(x) for x in rgb_str.strip("rgb()").split(",")]
        return sum(nums)/3 < 60
    return not (is_dark(top_color) and is_dark(bottom_color))

def recommend(items: List[Item], context: Dict) -> List[List[Item]]:
    # Minimal demo: choose one top + one bottom; add outerwear if cool
    tops = [i for i in items if i.type == "top"]
    bottoms = [i for i in items if i.type == "bottom"]
    outer = [i for i in items if i.type == "outerwear"]
    recs = []
    for t in tops:
        for b in bottoms:
            if not basic_color_ok(t.color, b.color): 
                continue
            outfit = [t, b]
            if is_cool(context.get("temp_f", 70)) and outer:
                outfit.append(outer[0])
            recs.append(outfit)
    return recs[:10]
