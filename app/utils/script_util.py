from pathlib import Path
import os
from app.model.container import Container
from app.model.medium import PlatformList

current_file_path = Path(__file__).resolve()
js_files_dir_path = current_file_path.parents[2] / 'js_files'

def make_file(container: Container):
    mediums_js_code = ''
    mediums = {PlatformList.get_name(medium.platform_id): [medium.base_code, medium.tracking_list] for medium in container.mediums}
    for k, v in mediums.items():
        mediums_js_code += f"{k}: {str(v)}, "
    mediums_js_code = f'let mediums = {{{mediums_js_code}}}; export {{mediums}};'
    with open(js_files_dir_path / 'mediums.js' ,"w") as file:
        file.write(mediums_js_code)

    events_js_code = ''
    events = {event.name: [event.func_code, event.url_reg] for event in container.events}
    for k, v in events.items():
        events_js_code += f"{k}: {str(v)}, "
    events_js_code = f'let events = {{{events_js_code}}}; export {{events}};'
    with open(js_files_dir_path / 'events.js' ,"w") as file:
        file.write(events_js_code)

    tags_js_code = ''
    tags = {tag.name: tag.script for tag in container.tags}
    for k, v in tags.items():
        tags_js_code += f"{k}: {v}, "
    tags_js_code = f'let tags = {{{tags_js_code}}}; export {{tags}};'

    with open(js_files_dir_path / 'tags.js' ,"w") as file:
        file.write(tags_js_code)

    os.system("npx webpack --entry ./js_files/index.js --output-path ./js_files --output-filename script.js")
