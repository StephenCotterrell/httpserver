from textnode import (
    TextNode,
    TextType,
    block_to_block_type,
    markdown_to_blocks,
    split_nodes_delimiter,
    extract_markdown_images,
    text_to_text_nodes,
    markdown_to_html_node,
)
from htmlnode import LeafNode, ParentNode

which_test = 2

match which_test:
    case 1:
        dummy_node = TextNode(
            "This is some anchor text", "link", "https://www.boot.dev"
        )
        print(dummy_node)

        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        print(node.to_html())

        delimiter_split_text_node = TextNode(
            "This is some _text_ which I'm attempting to split with a delimiter",
            TextType.TEXT,
        )

        print(split_nodes_delimiter([delimiter_split_text_node], "_", TextType.ITALIC))

        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        print(extract_markdown_images(text))

        # [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]

        full_test_text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_text_nodes(full_test_text)
        print(nodes)

        test = [
            TextNode("This is ", TextType.TEXT, "None"),
            TextNode("text", TextType.BOLD, "None"),
            TextNode(" with an ", TextType.TEXT, "None"),
            TextNode("italic", TextType.ITALIC, "None"),
            TextNode(" word and a ", TextType.TEXT, "None"),
            TextNode("code block", TextType.CODE, "No ne"),
            TextNode(" and an ", TextType.TEXT, "None"),
            TextNode("obi wan image", TextType.IMAGE, "None"),
            TextNode(" and a ", TextType.TEXT, "None"),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        md = """
this is **bolded** paragraph





this is another paragraph with _italic_ text and `code` here
this is the same paragraph on a new line

- this is a list
- with items
"""

        print(markdown_to_blocks(md))

        test_block = """
## This is a heading
        """

        print(block_to_block_type(test_block))

    case 2:
        md = """
# Heading 1

This is just a normal paragraph under the heading

## Heading 2

### Heading 3
"""

        node = markdown_to_html_node(md)
        print(node)
        html = node.to_html()
        print(html)
