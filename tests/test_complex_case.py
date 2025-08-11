import unittest
from notion_blockify.convert import Blockizer

markdown = """# Title

This is a paragraph.

- bullet 1
  - bullet 1.1
1. number 1
2. number 2

![alt](http://example.com/img.png)

> a quote

| col1 | col2 |
|------|------|
| A    | B    |

```python
print("hello")
```
[x] done
[ ] pending
---
"""


class TestComplexCase(unittest.TestCase):
    def setUp(self):
        self.notionizer = Blockizer()

    def test_complex_document_structure(self):
        blocks = self.notionizer.convert(markdown)

        # 1. order
        expected_order = [
            "heading_1",
            "paragraph",
            "bulleted_list_item",
            "numbered_list_item",
            "numbered_list_item",
            "image",
            "quote",
            "table",
            "code",
            "to_do",
            "to_do",
            "divider",
        ]

        actual_order = [b["type"] for b in blocks]
        self.assertEqual(expected_order, actual_order)

        # 2. bulleted_list
        bullet_children = blocks[2]["bulleted_list_item"]["children"]
        self.assertEqual(len(bullet_children), 1)
        self.assertEqual(bullet_children[0]["type"], "bulleted_list_item")
        self.assertIn(
            "bullet 1.1",
            bullet_children[0]["bulleted_list_item"]["rich_text"][0]["text"]["content"],
        )

        # 3. numbered_list
        self.assertEqual(blocks[3]["type"], "numbered_list_item")
        self.assertNotIn("children", blocks[3]["numbered_list_item"])

        # 4. Image
        self.assertIn("http://example.com/img.png", str(blocks[5]))

        # 5. table
        table_rows = blocks[7]["table"]["children"]
        self.assertEqual(
            table_rows[1]["table_row"]["cells"][0][0]["text"]["content"], "A"
        )

        # 6. code
        self.assertIn('print("hello")', str(blocks[8]))

        # 7. To-do
        self.assertTrue(blocks[9]["to_do"]["checked"])
        self.assertFalse(blocks[10]["to_do"]["checked"])


if __name__ == "__main__":
    unittest.main()
