# Kotoba

XML Parser with CSS Selector

The official ocumentation is not available as this is a developmental build. If you are interested, please report an issue or ping me in the comment.

## Getting Started

```python
from kotoba import Kotoba

xml_text: str = ...

parser = Kotoba(xml_text)
```

Alternatively, you can also use this.

```python
from kotoba import load_from_file

parser = load_from_file('/path/to/file.xml')
```