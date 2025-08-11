import re
from typing import List, Tuple

from notion_blockify.replace import replace_latex_and_code_block
from notion_blockify.blocks import (
    make_text_block,
    make_code_block,
    make_embed_block,
    make_image_block,
    make_latex_block,
    make_table_block,
    make_table_row_block,
    make_to_do_block,
)


class Blockizer:
    # Precompiled regex
    UNORDERED_LIST_RE = re.compile(r"^( *)(\-|\*) ")
    NUMBERED_LIST_RE = re.compile(r"^( *)(\d+)\. ")
    HEADING_RE = re.compile(r"^(#+)")
    QUOTE_RE = re.compile(r"> ([\s\S]+)")
    HR_RE = re.compile(r"^---+$")
    TABLE_RE = re.compile(r"(\|(.*)\|)")
    TABLE_SEPARATOR_RE = re.compile(r"(\|[-| ]+\|)")
    IMAGE_RE = re.compile(r"!\[(.*?)\]\((.*?)\)")
    TODO_RE = re.compile(r"^\[(x|\s|)\] ([\s\S]+)")

    # Special block identifiers
    CODE_BLOCK_PREFIX = "CODEBLOCK"
    LATEX_BLOCK_PREFIX = "LATEXBLOCK"
    IMAGEXML_BLOCK_PREFIX = "IMAGEXMLBLOCK"

    SUPPORTED_IMG_EXT = {"bmp", "gif", "heic", "jpeg", "png", "svg", "tif", "tiff"}

    def convert(self, text: str) -> List[dict]:
        """
        Convert markdown-like text into a list of Notion-style block dictionaries.
        """
        text, self.code_blocks, self.latex_blocks, self.image_xml_blocks = (
            replace_latex_and_code_block(text)
        )
        self.blocks = []
        self.list_stack: List[Tuple[dict, int]] = []

        for raw_line in text.split("\n"):
            if not raw_line.strip():
                continue
            self._process_line(raw_line)

        return self.blocks

    def _process_line(self, line: str):
        for handler in [
            self._handle_heading,
            self._handle_list,
            self._handle_image,
            self._handle_image_xml_block,
            self._handle_table,
            self._handle_quote,
            self._handle_special_blocks,
            self._handle_divider,
            self._handle_to_do,
        ]:
            if handler(line):
                return

        self._handle_paragraph(line)

    def _handle_heading(self, line: str) -> bool:
        match = self.HEADING_RE.match(line)
        if match:
            level = match.group(1).count("#")
            content = self.HEADING_RE.sub("", line).strip()
            self.blocks.append(make_text_block(f"heading_{level}", content))
            return True

        return False

    def _handle_list(self, line: str) -> bool:
        for pattern, block_type in [
            (self.UNORDERED_LIST_RE, "bulleted_list_item"),
            (self.NUMBERED_LIST_RE, "numbered_list_item"),
        ]:
            match = pattern.match(line)
            if match:
                indent = len(match.group(1))
                content = pattern.sub("", line).strip()
                if indent == 0:
                    self.list_stack = []

                block = make_text_block(block_type, text=content)

                while self.list_stack and self.list_stack[-1][1] >= indent:
                    self.list_stack.pop()

                if self.list_stack:
                    parent = self.list_stack[-1][0]
                    parent.setdefault(parent["type"], {}).setdefault(
                        "children", []
                    ).append(block)
                else:
                    self.blocks.append(block)

                self.list_stack.append((block, indent))
                return True

        return False

    def _handle_image(self, line: str) -> bool:
        match = self.IMAGE_RE.match(line)
        if match:
            _, url = match.groups()
            ext = url.split(".")[-1].lower()
            if ext in self.SUPPORTED_IMG_EXT:
                block = make_image_block(url)
            else:
                block = make_embed_block(url)
            self.blocks.append(block)
            return True

        return False

    def _handle_image_xml_block(self, line: str) -> bool:
        if line.startswith(self.IMAGEXML_BLOCK_PREFIX):
            try:
                idx = int(line.split("_")[-1])
                url, caption = self.image_xml_blocks[idx]
                ext = url.split(".")[-1].lower()
                if ext in self.SUPPORTED_IMG_EXT:
                    block = make_image_block(url)
                else:
                    block = make_embed_block(url)
                self.blocks.append(block)
                self.blocks.append(make_text_block("paragraph", text=f"_{caption}_"))
                return True
            except (IndexError, ValueError):
                return False

        return False

    def _handle_table(self, line: str) -> bool:
        if self.TABLE_SEPARATOR_RE.match(line):
            return True

        match = self.TABLE_RE.match(line)
        if match:
            columns = [cell.strip() for cell in match.group(2).split("|")]
            if self.blocks and self.blocks[-1]["type"] == "table":
                self.blocks[-1]["table"]["children"].append(
                    make_table_row_block(columns)
                )
            else:
                self.blocks.append(make_table_block(columns))
            return True

        return False

    def _handle_quote(self, line: str) -> bool:
        match = self.QUOTE_RE.match(line)
        if match:
            self.blocks.append(make_text_block("quote", text=match.group(1).strip()))
            return True

        return False

    def _handle_special_blocks(self, line: str) -> bool:
        if line.startswith(self.CODE_BLOCK_PREFIX):
            try:
                idx = int(line.split("_")[-1])
                language, code = self.code_blocks[idx]
                self.blocks.append(make_code_block(language, code))
                return True
            except (IndexError, ValueError):
                return False

        if line.startswith(self.LATEX_BLOCK_PREFIX):
            try:
                idx = int(line.split("_")[-1])
                self.blocks.append(make_latex_block(self.latex_blocks[idx]))
                return True
            except (IndexError, ValueError):
                return False

        return False

    def _handle_divider(self, line: str) -> bool:
        if self.HR_RE.match(line):
            self.blocks.append({"type": "divider", "divider": {}})
            return True

        return False

    def _handle_to_do(self, line: str) -> bool:
        match = self.TODO_RE.match(line)
        if match:
            checked, text = match.groups()
            self.blocks.append(make_to_do_block(text.strip(), checked.lower() == "x"))
            return True

        return False

    def _handle_paragraph(self, line: str):
        self.blocks.append(make_text_block("paragraph", text=line.strip()))
