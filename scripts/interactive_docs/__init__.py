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
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/school-book.min.css">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
            </head>
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
                hljs.highlightAll();
            </script>
        </html>

    """
