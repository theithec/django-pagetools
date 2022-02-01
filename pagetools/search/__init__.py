from typing import List

from django.db import models


search_mods: List = [
    # ( app.models.Model1,   ('title', 'content') ),
    # ( app.models.Model2, ('title', 'content','footer') ),
]


def extra_filter(x):
    return x
