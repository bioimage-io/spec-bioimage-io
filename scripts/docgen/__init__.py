from typing import Any, List
from .hint import Hint, Unrecognized, Widget

def generate_docs(*, raw_type: Any, root_path: List[str]) -> "str | Exception":
    hint = Hint.parse(raw_hint=raw_type, parent_raw_hints=[])
    if isinstance(hint, (Exception, Unrecognized)):
        return Exception(f"Could not process {raw_type}: {hint}")

    root_hint_widget = hint.to_type_widget(root_path)
    assert isinstance(root_hint_widget, Widget), root_hint_widget

    return f"""
        <!doctype html>
        <html>
            <script>
                document.addEventListener("DOMContentLoaded", () => {{
                    if(location.hash){{
                        console.log("Expanding details and jumping to hash");
                        const target = document.getElementById(location.hash.slice(1));
                        if(!target){{
                            return
                        }}
                        let parent = target.parentElement;
                        while(parent){{
                            if(parent.tagName == "DETAILS"){{
                                parent.open = true;
                            }}
                            parent = parent.parentElement;
                        }}
                        target.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start',
                        }});
                    }}
                }})
            </script>
            <style>
                {Widget.get_css()}
            </style>
            <body>
                {root_hint_widget.to_html()}
            </body>
            <script>
                const p = document.createElement('p')
                document.body.prepend(document.createElement('p'))
            </script>
        </html>

    """