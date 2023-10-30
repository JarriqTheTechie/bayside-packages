import asyncio
import re
import time
import traceback
from functools import partial
from pathlib import Path
from typing import Any

from flask import render_template_string
from markupsafe import Markup

from fire_starter import FireStarter
from qlog import QLog

fire_starter: FireStarter = FireStarter()
log = QLog()


def async_partial(f, *args):
    async def f2(*args2):
        result = f(*args, *args2)
        if asyncio.iscoroutinefunction(f):
            result = await result
        return result

    return f2


def micro_render(app, bang_template: Path, context=None, **kwargs: dict[Any, Any]) -> str:
    if context is None:
        context = {}
    st: float = time.time()
    fire_starter.fire("template_rendering_began", message=f"Began rendering template [{bang_template}]")
    with open(bang_template, 'r') as bang_f:
        template: str = bang_f.read()
        bang_pattern: str = r'---\n(.*?)\n---'
        bang_result: Any = re.findall(bang_pattern, template, re.DOTALL)
    bang_vals: dict[Any, Any] = {}
    for bang_script in bang_result:
        try:
            exec(bang_script.strip())
            bang_vals.update(locals())
            # remove all keys from locals that do not start with bang_
            for bang_key in list(bang_vals.keys()):
                if bang_key.startswith("bang_"):
                    del bang_vals[bang_key]

        except Exception as e:
            traceback_str = traceback.format_exc()
            print(f'ERROR: {traceback_str}')

    stripped_template = re.sub(r"^.*?(<template>.*?</template>).*?$", r"\1", template, flags=re.DOTALL)
    html_str: str = stripped_template.strip().lstrip("<template>").rstrip("</template>")
    if context:
        bang_vals.update(context)
    with app.app_context():
        app.jinja_env.enable_async = True
        app.jinja_env.globals['_render'] = partial(micro_render, app)

        if str(bang_template).startswith("components"):
            component_html = html_str
            output = Markup(render_template_string(component_html, **bang_vals))
        else:
            output: str = render_template_string("""
                {% extends 'layouts/App.html' %}
                {% block content %}
                    html_str
                {% endblock %}
            """.replace("html_str", html_str), **bang_vals)
        et: float = time.time()
        fire_starter.fire("template_rendering_ended",
                          message=f"Ended rendering [{bang_template}] template took {et - st} seconds")
        return output


@fire_starter.event("template_rendering_began")
def on_template_rendering_began(message: str) -> None:
    log.info(message)
    pass


@fire_starter.event("template_rendering_ended")
def on_template_rendering_ended(message: str) -> None:
    log.info(message)
    pass
