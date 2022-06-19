"""
Todo Summary
"""

import glob
import json
import os
import re
from datetime import datetime
import yaml
import frontmatter
import requests
from jinja2 import Template


todo_p_list = []
todo_1_list = []
todo_2_list = []
todo_3_list = []


def todo_sender():

    """
    Send a daily list of current todo entries to Telegram
    """

    # Configuration file:
    with open("config.yml", "r", encoding="utf-8") as config:

        # Load config file:
        config_file = yaml.safe_load(config)

    # Grab todo entries:
    log_path = config_file["log_path"]

    for path in sorted(glob.glob(os.path.join(log_path, "*.md"))):
        with open(path, "r", encoding="utf-8") as entry_content:

            metadata, content = frontmatter.parse(entry_content.read())

            entry_title = metadata["title"]
            entry_id = metadata["id"]
            entry_types = metadata["types"]

            todo_p = re.search(r"todo-p", entry_types)
            todo_1 = re.search(r"todo-1", entry_types)
            todo_2 = re.search(r"todo-2", entry_types)
            todo_3 = re.search(r"todo-3", entry_types)

            if todo_p:
                todo_p_entries = entry_id, entry_title
                todo_p_list.append(todo_p_entries)
            if todo_1:
                todo_1_entries = entry_id, entry_title
                todo_1_list.append(todo_1_entries)
            if todo_2:
                todo_2_entries = entry_id, entry_title
                todo_2_list.append(todo_2_entries)
            if todo_3:
                todo_3_entries = entry_id, entry_title
                todo_3_list.append(todo_3_entries)

    date = datetime.now().strftime("%A %e %B %Y")
    log_url = config_file["log_url"]

    html = Template(
        """
<b>Todo Summary</b>
<i>{{date}}</i>

<b>Priority Todos</b>
{%- for todo in todo_p %}
- <a href="{{ log_url }}/{{ todo[0] }}">{{ todo[1] }}</a>
{%- endfor %}

<b>Priority 1 Todos</b>
{%- for todo in todo_1 %}
- <a href="{{ log_url }}/{{ todo[0] }}">{{ todo[1] }}</a>
{%- endfor %}

<b>Priority 2 Todos</b>
{%- for todo in todo_2 %}
- <a href="{{ log_url }}/{{ todo[0] }}">{{ todo[1] }}</a>
{%- endfor %}

<b>Priority 3 Todos</b>
{%- for todo in todo_3 %}
- <a href="{{ log_url }}/{{ todo[0] }}">{{ todo[1] }}</a>
{%- endfor %}
"""
    )
    print(html.render(date=date, log_url=log_url, todo_p=todo_p_list, todo_1=todo_1_list, todo_2=todo_2_list, todo_3=todo_3_list))

    # Telegram API Configuration:
    bot_token = config_file["telegram_bot_token"]
    base_url = config_file["telegram_base_url"]
    chat_id = str(config_file["telegram_bot_chat_id"])
    api_url = f"/bot{bot_token}/sendMessage"
    api_payload = {
        "chat_id": chat_id,
        "parse_mode": "HTML",
        "text": f"{html.render(date=date, log_url=log_url, todo_p=todo_p_list, todo_1=todo_1_list, todo_2=todo_2_list, todo_3=todo_3_list)}",
    }
    api_endpoint = base_url + api_url

    # Telegram API call:
    response = requests.post(
        api_endpoint,
        headers={"Content-Type": "application/json"},
        data=json.dumps(api_payload),
    )


todo_sender()
