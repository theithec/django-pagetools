from typing import Dict

from django.apps import AppConfig


class SectionsConfig(AppConfig):
    name: str = "pagetools.sections"
    render_node_extradata: Dict[str, str] = {}
