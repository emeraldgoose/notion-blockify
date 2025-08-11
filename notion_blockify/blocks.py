import re


def text_with_style(text):
    STYLE_MAP = {
        "**": "bold",
        "__": "bold",
        "*": "italic",
        "_": "italic",
        "~~": "strikethrough",
        "`": "code",
    }

    tokens = re.split(r"(\*\*|__|\*|_|~~|`)", text)
    active_styles = set()
    spans = []

    for token in tokens:
        if not token:
            continue
        link_in_token = re.match(r"\[([\s\S]+)\]\(([\s\S]+)\)", token)
        if link_in_token:
            spans.append(
                {
                    "text": {
                        "content": link_in_token.group(1),
                        "link": {"url": link_in_token.group(2)},
                    },
                    "href": link_in_token.group(2),
                }
            )
        token = re.sub(r"\[([\s\S]+)\]\(([\s\S]+)\)", "", token)
        if token in STYLE_MAP:
            if token in active_styles:
                active_styles.remove(token)
            else:
                active_styles.add(token)
        else:
            spans.append(
                {
                    "text": {"content": token},
                    "annotations": {STYLE_MAP[style]: True for style in active_styles},
                }
            )

    return spans


def make_text_block(type, text):
    annotations = text_with_style(text)

    block = {
        "object": "block",
        "type": type,
        type: {
            "rich_text": annotations,
        },
    }
    return block


def make_image_block(url):
    block = {"object": "block", "type": "image", "image": {"external": {"url": url}}}
    return block


def make_table_row_block(row):
    block = {
        "object": "block",
        "type": "table_row",
        "table_row": {"cells": [text_with_style(data) for data in row]},
    }
    return block


def make_table_block(row):
    block = {
        "object": "block",
        "type": "table",
        "table": {
            "has_column_header": True,
            "has_row_header": False,
            "table_width": len(row),
            "children": [make_table_row_block(row)],
        },
    }
    return block


def make_code_block(language, code):
    block = {
        "object": "block",
        "type": "code",
        "code": {
            "language": language,
            "rich_text": [{"type": "text", "text": {"content": code}}],
        },
    }
    return block


def make_latex_block(latex):
    block = {"type": "equation", "equation": {"expression": latex}}
    return block


def make_embed_block(url):
    block = {"type": "embed", "embed": {"url": url}}
    return block


def make_to_do_block(row, checked):
    block = {
        "type": "to_do",
        "to_do": {"rich_text": text_with_style(row), "checked": checked},
    }
    return block
