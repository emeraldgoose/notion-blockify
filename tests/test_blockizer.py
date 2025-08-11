import unittest
from notion_blockify.convert import Blockizer


class TestBlockizer(unittest.TestCase):
    def setUp(self):
        self.notionizer = Blockizer()

    def test_heading(self):
        md = "# Heading 1\n## Heading 2"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "heading_1")
        self.assertEqual(
            blocks[0]["heading_1"]["rich_text"][0]["text"]["content"], "Heading 1"
        )
        self.assertEqual(blocks[1]["type"], "heading_2")
        self.assertEqual(
            blocks[1]["heading_2"]["rich_text"][0]["text"]["content"], "Heading 2"
        )

    def test_paragraph(self):
        md = "This is a paragraph."
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "paragraph")
        self.assertIn(
            "This is a paragraph.",
            blocks[0]["paragraph"]["rich_text"][0]["text"]["content"],
        )

    def test_bulleted_list_depth_limit(self):
        md = "- item 1\n  - item 1.1\n    - item 1.1.1"
        blocks = self.notionizer.convert(md)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["type"], "bulleted_list_item")
        self.assertEqual(
            blocks[0]["bulleted_list_item"]["children"][0]["type"], "bulleted_list_item"
        )
        self.assertNotIn(
            "children",
            blocks[0]["bulleted_list_item"]["children"][0]["bulleted_list_item"][
                "children"
            ][0]["bulleted_list_item"],
        )

    def test_numbered_list_depth_limit(self):
        md = "1. item 1\n   1. item 1.1\n      1. item 1.1.1"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "numbered_list_item")
        self.assertEqual(
            blocks[0]["numbered_list_item"]["children"][0]["type"], "numbered_list_item"
        )
        self.assertNotIn(
            "children",
            blocks[0]["numbered_list_item"]["children"][0]["numbered_list_item"][
                "children"
            ][0]["numbered_list_item"],
        )

    def test_quote(self):
        md = "> quoted text"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "quote")
        self.assertIn(
            "quoted text", blocks[0]["quote"]["rich_text"][0]["text"]["content"]
        )

    def test_divider(self):
        md = "---"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "divider")

    def test_todo(self):
        md = "[x] done task\n[ ] pending task"
        blocks = self.notionizer.convert(md)
        self.assertTrue(blocks[0]["to_do"]["checked"])
        self.assertFalse(blocks[1]["to_do"]["checked"])

    def test_table(self):
        md = "| Col1 | Col2 |\n|------|------|\n| A    | B    |"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "table")
        self.assertEqual(len(blocks[0]["table"]["children"]), 2)  # header + 1 row

    def test_image(self):
        md = "![alt](http://example.com/image.png)"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "image")

    def test_embed(self):
        md = "![alt](http://example.com/video.mp4)"
        blocks = self.notionizer.convert(md)
        self.assertEqual(blocks[0]["type"], "embed")


if __name__ == "__main__":
    unittest.main()
