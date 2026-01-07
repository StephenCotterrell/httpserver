import unittest

from textnode import (
    TextNode,
    TextType,
    BlockType,
    block_to_block_type,
    extract_markdown_links,
    extract_title,
    split_nodes_delimiter,
    text_node_to_html_node,
    extract_markdown_images,
    split_nodes_image,
    split_nodes_link,
    text_to_text_nodes,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_neq_1(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD, "http://www.boot.dev")
        self.assertNotEqual(node, node2)

    def test_neq_2(self):
        node = TextNode("This is a text node", TextType.ITALIC, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertNotEqual(node, node2)

    def test_neq_3(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.boot.dev")
        node2 = TextNode("This was a text node", TextType.BOLD, "https://www.boot.dev")
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a bold node.", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a bold node.")

    def test_italic(self):
        node = TextNode("This is an italic node.", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is an italic node.")

    def test_code(self):
        node = TextNode("This is a code node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a code node")

    def test_link(self):
        node = TextNode("This is a link node.", TextType.LINK, "https://boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a link node.")
        self.assertEqual(html_node.props, {"href": "https://boot.dev"})

    def test_image(self):
        node = TextNode("This is an image node", TextType.IMAGE, "https://boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props, {"src": "https://boot.dev", "alt": "This is an image node"}
        )

    def test_split_italics(self):
        node = TextNode("This is _text with italic_ formatting.", TextType.TEXT)
        split_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            split_nodes,
            [
                TextNode("This is ", TextType.TEXT, None),
                TextNode("text with italic", TextType.ITALIC, None),
                TextNode(" formatting.", TextType.TEXT, None),
            ],
        )

    def test_split_nodes_delimiter_skips_empty_nodes(self):
        node = TextNode("**bold**", TextType.TEXT)
        split_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            split_nodes,
            [
                TextNode("bold", TextType.BOLD, None),
            ],
        )

    def test_split_nodes_delimiter_skips_empty_middle(self):
        node = TextNode("**bold****after**", TextType.TEXT)
        split_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            split_nodes,
            [
                TextNode("bold", TextType.BOLD, None),
                TextNode("after", TextType.BOLD, None),
            ],
        )

    def test_split_nodes_delimiter_raises_on_unmatched(self):
        node = TextNode("This is **bold text", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_extract_markdown_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertEqual(
            matches,
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )

    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev) and ![to boot dev](https:www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertEqual(
            matches,
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with an [link](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_text_to_text_nodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph\n
This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line\n
- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_with_extra_newlines(self):
        md = """
This is **bolded** paragraph \n\n\n\n\n
This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_text_block_to_block_type_heading1(self):
        block = """
# heading
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.HEADING)

    def test_text_block_to_block_type_heading2(self):
        block = """
## heading
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.HEADING)

    def test_text_block_to_block_type_heading6(self):
        block = """
###### heading
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.HEADING)

    def test_text_block_to_block_type_code(self):
        block = """
```
code goes here
```
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.CODE)

    def test_text_to_block_type_quote(self):
        block = """
> This is a quote line
> This is another quote line
> This is a third quote line > > 
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.QUOTE)

    def test_text_to_block_type_unordered_list(self):
        block = """
- This is an ordered list
- this is a second line in the ordered list
- this is a third line in the ordered list
- this is a fourth line in the ordered list
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.UNORDERED_LIST)

    def test_text_to_block_type_ordered_list(self):
        block = """
1. This is the first line in an ordered list
2. This is the second line in an ordered list
3. This is the third line in an ordered list
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        block = """
This is just regular text. This is not anything really special. > This is not a quote, because it's in regular text.
"""
        blocktype = block_to_block_type(block)
        self.assertEqual(blocktype, BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_quoteblock(self):
        md = """
> test line 1
> test line 2
> test line 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote><p>test line 1</p><p>test line 2</p><p>test line 3</p></blockquote></div>",
        )

    def test_unordered_list_block(self):
        md = """
- this is an unordered list
- this is another line in the unordered list
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>this is an unordered list</li><li>this is another line in the unordered list</li></ul></div>",
        )

    def test_ordered_list_block(self):
        md = """
1. first item
2. second item
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first item</li><li>second item</li></ol></div>",
        )

    def test_ordered_list_block_with_double_digits(self):
        md = """
1. item 1
2. item 2
3. item 3
4. item 4
5. item 5
6. item 6
7. item 7
8. item 8
9. item 9
10. item 10
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>item 1</li><li>item 2</li><li>item 3</li><li>item 4</li><li>item 5</li><li>item 6</li><li>item 7</li><li>item 8</li><li>item 9</li><li>item 10</li></ol></div>",
        )

    def test_ordered_list_block_with_mixed_spacing(self):
        md = """
1.item 1
2.  item 2
3.	item 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>item 1</li><li>item 2</li><li>item 3</li></ol></div>",
        )

    def test_heading_block(self):
        md = """
# Heading 1

This is just a normal paragraph under the heading

## Heading 2

### Heading 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><p>This is just a normal paragraph under the heading</p><h2>Heading 2</h2><h3>Heading 3</h3></div>",
        )

    def test_heading_with_inline_formatting(self):
        md = """
# **Bold** Heading
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1><b>Bold</b> Heading</h1></div>")

    def test_extract_title(self):
        md = """
# Heading
"""
        heading = extract_title(md)
        self.assertEqual(heading, "Heading")

    def test_extract_title_strips_trailing_whitespace(self):
        md = """
# Heading   
"""
        heading = extract_title(md)
        self.assertEqual(heading, "Heading")


if __name__ == "__main__":
    unittest.main()
