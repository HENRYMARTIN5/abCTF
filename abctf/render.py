from typing import Any, Dict
from flask import render_template as _render_template
from jinja2 import Template
from datetime import datetime
import subprocess

def get_current_commit_hash() -> str:
    """Gets the current git commit hash."""
    try:
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return commit_hash
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "N/A"

global_context: Dict[str, Any] = {
    "year": datetime.now().year,
    "commit": get_current_commit_hash()
}

def render_template(
    template_name_or_list: str | Template | list[str | Template],
    **context: Any):
    """
    Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """
    
    merged_context = {**global_context, **context}
    return _render_template(template_name_or_list, **merged_context)