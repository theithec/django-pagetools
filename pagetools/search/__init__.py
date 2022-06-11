from typing import List


search_mods: List = [
    # ( app.models.Model1,   ('title', 'content') ),
    # ( app.models.Model2, ('title', 'content','footer') ),
]


def extra_filter(queryset):
    return queryset
