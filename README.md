# notion-blockify
`notion-blockify` is a Python library that converts Markdown into Notion API–compatible block structures.

## Installation
```
pip install notion-blockify
```

## Usage
```
from notion_blockify import Blockizer

markdown = """
# Heading 1
This is paragraph.
"""

blocks = Blockizer().convert(markdown)
```

## Supported Blocks
### Headings
```
# Heading 1
## Heading 2
### Heading 3
```
### Lists

> Note: The block that allows children is limited to a maximum of two levels of nesting by the Notion API.

**bulleted list**
```
- bulleted list 1
  - bulleted list 2
    - bulleted list 3
```

**numbered list**
```
1. numbered list 1
    1. numbered list 2
        1. numbered list 3
```

### Table
```
| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |
```

### Quote
```
> Quote
```

### Code
    ```cpp
    #include <iostream>
    using namespace std;
    int main() {
        cout<<"hello world"<<endl;
        return 0;
    }
    ```

    ```python
    print('hello')
    ```

    ```
    plain text
    ```

### Horizontal Line
```
---
```

### Image
```
![Alt](Image url)
```

Only `<figure>` tags containing both an `<img>` and a `<figcaption>` are supported. The caption will be added below the image in italic text.
```
<figure>
    <img src="image url">
    <figcaption>caption text</figcaption>
</figure>
```

### Latex
```
$$ E = mc^2 $$
```

### TODO
```
[x] checked
[] not checked
[ ] not checked
```

### Text Style
**bold**
```
**bold**
__bold__
```
**italic**
```
*italic*
_italic_
```
~~strikethrough~~
```
~~strikethrough~~
```
`code`
```
`code`
```


## Examples
If you are using the [notion-client](https://github.com/ramnes/notion-sdk-py) library, you can create a page.

> Note: The Notion API does not allow more than 100 blocks in a single request. Exceeding this limit will result in an error.   
> If you need to add more than 100 blocks, split them into multiple requests and append them sequentially to the same parent block or page.

### Create a page in a Notion page
```python
import os
from notion_blockify import Blockizer
from notion_client import Client

with open('example.md', 'r') as f:
    text = f.read()

blocks = Blockizer().convert(text)

notion = Client(auth=os.environ["NOTION_API_KEY"])
my_page = notion.pages.create(
    **{
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties: {"title": [{"text": {"content": PAGE_TITLE}}]},
        "children": blocks
    }
)
```

### Create a page in a Notion database
```python
import os
from notion_blockify import Blockizer
from notion_client import Client

with open('example.md', 'r') as f:
    text = f.read()

blocks = Blockizer().convert(text)

notion = Client(auth=os.environ["NOTION_API_KEY"])
my_page = notion.pages.create(
    **{
        "parent": {"page_id": NOTION_DATABASE_ID},
        "properties: {
            "Name": {
                "title": [
                    {"text": {"content": PAGE_TITLE}}
                ]
            },
            "Food group": {"select": {"name": "Vegetable"}},
            "Price": {"number": 2.5},
        },
        "children": blocks
    }
)
```
