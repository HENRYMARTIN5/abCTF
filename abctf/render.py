from typing import Any, Dict
from flask import (
    render_template as _render_template,
    render_template_string as _render_template_string,
)
from jinja2 import Template
from datetime import datetime
import subprocess
from flask_login import current_user


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
    "commit": get_current_commit_hash(),
}
"""
Global constants passed to all templates.
"""


def make_context(context: Dict[str, Any]):
    user_context = {
        "is_authed": current_user.is_authenticated,
        "is_on_team": current_user.is_authenticated
        and current_user.team_id is not None,
        "is_admin": current_user.is_authenticated and current_user.is_admin,
        "username": current_user.username if current_user.is_authenticated else "",
        "current_user": current_user,
    }
    """
    Information about the currently logged in user passed to all templates.
    """

    return {**global_context, **user_context, **context}


def render_template(
    template_name_or_list: str | Template | list[str | Template], **context: Any
):
    """
    Render a template by name with the given context.

    :param template_name_or_list: The name of the template to render. If
        a list is given, the first name to exist will be rendered.
    :param context: The variables to make available in the template.
    """

    return _render_template(template_name_or_list, **make_context(context))


def render_template_string(source: str, **context: Any):
    """
    Render a template by name with the given context.
    """

    return _render_template_string(source, **make_context(context))
