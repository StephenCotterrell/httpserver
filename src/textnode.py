from enum import Enum
from htmlnode import LeafNode, ParentNode
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, compare):
        if (
            self.text == compare.text
            and self.text_type == compare.text_type
            and self.url == compare.url
        ):
            return True
        else:
            return False

    def __repr__(self):
        return f'TextNode("{self.text}", {self.text_type}, "{self.url}")'


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError("Unknown Text Type")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type is not TextType.TEXT:
            new_nodes.append(old_node)
        else:
            isvalid = old_node.text.count(delimiter) % 2 == 0
            starts_with_delimiter = (
                old_node.text != "" and old_node.text[0] == delimiter
            )
            if not isvalid:
                raise Exception(
                    "There must be a matching closing delimiter for each delimiter"
                )
            new_nodes_text = old_node.text.split(delimiter)
            for index, text in enumerate(new_nodes_text):
                if not text:
                    continue  # skips empty strings
                new_node_text_type = (
                    TextType.TEXT
                    if index % 2 == 0 ^ starts_with_delimiter
                    else text_type
                )
                node = TextNode(text, new_node_text_type)
                new_nodes.append(node)
    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return matches


def extract_markdown_links(text):
    matches = re.findall(r"(?<!\!)\[(.*?)\]\((.*?)\)", text)
    return matches


def split_nodes_image(nodes):
    new_nodes = []
    for node in nodes:
        text = node.text
        original_type = node.text_type
        original_url = node.url
        sections = re.split(r"(!\[.*?\]\(.*?\))", text)
        sections = sections[:-1] if sections[-1] == "" else sections
        for section in sections:
            image_match = extract_markdown_images(section)
            if image_match:
                image_alt, image_link = image_match[0]
                new_nodes.extend([TextNode(image_alt, TextType.IMAGE, image_link)])
            else:
                new_nodes.extend([TextNode(section, original_type, original_url)])
    return new_nodes


def split_nodes_link(nodes):
    new_nodes = []
    for node in nodes:
        text = node.text
        original_type = node.text_type
        original_url = node.url
        sections = re.split(r"(?<!\!)(\[.*?\]\(.*?\))", text)
        sections = sections[:-1] if sections[-1] == "" else sections
        for section in sections:
            link_match = extract_markdown_links(section)
            if link_match:
                link, url = link_match[0]
                new_nodes.extend([TextNode(link, TextType.LINK, url)])
            else:
                new_nodes.extend([TextNode(section, original_type, original_url)])

    return new_nodes


def text_to_text_nodes(text):
    node = TextNode(text, TextType.TEXT)
    splits = [
        ("**", TextType.BOLD),
        ("_", TextType.ITALIC),
        ("`", TextType.CODE),
    ]
    nodes = [node]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    for split in splits:
        delimiter, text_type = split
        nodes = split_nodes_delimiter(nodes, delimiter, text_type)

    return nodes


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks if block != ""]
    return blocks


def block_to_block_type(block):
    lines = [line for line in block.split("\n") if line != ""]
    first = lines[0].split(" ", maxsplit=1)[0]
    last = lines[-1].split(" ", maxsplit=1)[-1]

    if all(char == "#" for char in first) and len(first) <= 6:
        return BlockType.HEADING
    elif first == "```" and last == "```":
        return BlockType.CODE
    elif all(line[0] == ">" for line in lines):
        return BlockType.QUOTE
    elif all(line[0] == "-" for line in lines):
        return BlockType.UNORDERED_LIST
    elif all(re.match(rf"^{index + 1}\.\s*", line) for index, line in enumerate(lines)):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    node_children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.PARAGRAPH:
                node_children.append(paragraph_markdown_to_html_node(block))
                continue
            case BlockType.HEADING:
                node_children.append(heading_markdown_to_html_node(block))
                continue
            case BlockType.CODE:
                node_children.append(code_markdown_to_html_node(block))
                continue
            case BlockType.QUOTE:
                node_children.append(quote_markdown_to_html_node(block))
                continue
            case BlockType.UNORDERED_LIST:
                node_children.append(unordered_list_markdown_to_html_node(block))
                continue
            case BlockType.ORDERED_LIST:
                node_children.append(ordered_list_markdown_to_html_node(block))
                continue

    return ParentNode("div", node_children)


def ordered_list_markdown_to_html_node(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        item_text = re.sub(r"^\d+\.\s*", "", line)
        children.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ol", children)


def unordered_list_markdown_to_html_node(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        item_text = re.sub(r"^-\s*", "", line)
        children.append(ParentNode("li", text_to_children(item_text)))
    return ParentNode("ul", children)


def quote_markdown_to_html_node(block):
    lines = block.split("\n")
    stripped = [re.sub(r"^>\s*", "", line) for line in lines]
    item_text = " ".join(stripped)
    return ParentNode("blockquote", text_to_children(item_text))


def code_markdown_to_html_node(block):
    text_node = TextNode(block[4:-3], TextType.CODE)
    code_node = text_node_to_html_node(text_node)
    return ParentNode("pre", [code_node])


def paragraph_markdown_to_html_node(block):
    children = text_to_children(block)
    return ParentNode("p", children)


def heading_markdown_to_html_node(block):
    first = block.split(" ", maxsplit=1)[0]
    text = block.split(" ", maxsplit=1)[1]
    tag = f"h{len(first)}"
    children = text_to_children(text)
    node = ParentNode(tag, children)
    return node


def text_to_children(text):
    text = " ".join(text.split("\n"))
    text_nodes = text_to_text_nodes(text)
    html_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
    return html_nodes
