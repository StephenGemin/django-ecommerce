"""
HOW TO RUN THIS
 - python manage.py runscript add_items_to_db -v3
"""
import random
from pathlib import Path
from typing import Any

from .. import constants
from ..models import Item


def _random_choice(choices: Any):
    return random.choice(choices)


def run():
    start_item_index, end_item_index = 1, 31
    category_choices = [i[0] for i in constants.CATEGORY_CHOICES]
    label_choices = [i[0] for i in constants.LABEL_CHOICES]
    image_dir = Path(__file__).parent.parent.parent.parent.joinpath(
        "media/inventory_pics"
    )
    images = [str(i) for i in image_dir.rglob("*.jpg")]
    price_discount_indices = (3, 6, 9, 13, 26)

    for i in range(start_item_index, end_item_index):
        _dict = {
            "title": f"Dummy Item {i}",
            "description": "Te melius apeirian postulant cum, labitur admodum cu eos!",
            "slug": f"test-product-{i}",
            "image": _random_choice(list(images)),
            "category": _random_choice(category_choices),
            "label": _random_choice(label_choices),
            "price": round(random.uniform(0.1, 1000), 2),
        }
        if i in price_discount_indices:
            _dict["price_discount"] = round(0.1 * _dict["price"], 2)
        item = Item(**_dict)
        item.save()
