import re

CODE_BLOCK_PATTERN = re.compile(r"```(\w+)?\n([\s\S]*?)\n```", re.DOTALL)
LATEX_BLOCK_PATTERN = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
IMAGE_XML_BLOCK_PATTERN = image_xml_pattern = re.compile(
    r"<figure>\n([\s\S]*?)\n</figure>", re.DOTALL
)


def replace_code_blocks(match):
    index = len(code_blocks)
    language, content = match.group(1), match.group(2)
    if language == "cpp":
        language = "c++"
    code_blocks[index] = ((language or "plain text").strip(), content.strip())
    return f"CODEBLOCK_{index}"


def replace_latex_blocks(match):
    index = len(latex_blocks)
    content = match.group(1)
    latex_blocks[index] = content.strip()
    return f"LATEXBLOCK_{index}"


def replace_image_xml_blocks(match):
    index = len(image_xml_blocks)
    content = match.group(1)
    src = re.findall(r'<img src="([\s\S]*?)">', content)
    figcaption = re.findall(r"<figcaption>([\s\S]*?)</figcaption>", content)
    src = "" if src is None else src[0]
    figcaption = "" if figcaption is None else figcaption[0]
    image_xml_blocks[index] = (src, figcaption)
    return f"IMAGEXMLBLOCK_{index}"


def replace_latex_and_code_block(text):
    global code_blocks, latex_blocks, image_xml_blocks

    code_blocks = {}
    latex_blocks = {}
    image_xml_blocks = {}

    text = CODE_BLOCK_PATTERN.sub(replace_code_blocks, text)
    text = LATEX_BLOCK_PATTERN.sub(replace_latex_blocks, text)
    text = IMAGE_XML_BLOCK_PATTERN.sub(replace_image_xml_blocks, text)
    return text, code_blocks, latex_blocks, image_xml_blocks
