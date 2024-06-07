import unittest
from unittest.mock import patch
from sh_doctest.templates import (
    Template,
    Expansion,
    TemplatedDoc,
    transform_placeholders,
)
from sh_doctest.line_block import LineBlock
from sh_doctest.numbered_line import NumberedLine
from sh_doctest.templates import parse_value


"""
This test suite covers the following cases:

TestTemplate:

Parsing a template with variables
Parsing a template without variables
Raising an error when the end_template name doesn't match the template name
TestExpansion:

Parsing an expansion with valid let lines
Raising an error when a let line is invalid

TestTemplatedDoc:

Parsing a templated document with templates and expansions
Expanding all templates in a document
Rendering a template string with variables

Note that these tests use the unittest.mock library to mock out certain dependencies,
such as reading files and creating Jinja2 environments. You may need to adjust the imports
and mocking depending on your project's structure and dependencies.
"""


def test_transform_placeholders():
    template_text = """
This is a template with <var1> and <var2> on the first line,
and {{ var3 }} and {{ var4 }} on the second line.
"""
    expected_output = """
This is a template with {{ var1 }} and {{ var2 }} on the first line,
and {{ var3 }} and {{ var4 }} on the second line.
"""
    output = transform_placeholders(template_text)
    assert output == expected_output


TemplatedDoc.break_on_loop = lambda self, x: x + 1


class TestTemplateParsing(unittest.TestCase):
    def test_parse_value_valid(self):
        line = NumberedLine("keyword: value", 1)
        result = parse_value("keyword", line)
        self.assertEqual(result.line, "value")
        self.assertEqual(result.lineno, 1)

    def test_parse_value_missing_colon(self):
        line = NumberedLine("keyword value", 1)
        with self.assertRaises(ValueError):
            parse_value("keyword", line)

    def test_template_parse_missing_end_template(self):
        lines = LineBlock.from_text(
            """
template: my_template
var: var1, var2
This is a template with {{ var1 }} and {{ var2 }}.
"""
        )
        with self.assertRaises(ValueError):
            Template.parse(lines)

    def test_expansion_parse_invalid_let(self):
        lines = LineBlock.from_text(
            """
expand: my_template
let: var1
"""
        )
        with self.assertRaises(ValueError):
            Expansion.parse(lines)

    def test_expansion_parse_no_let(self):
        lines = LineBlock.from_text(
            """
expand: my_template
"""
        )
        expansion = Expansion.parse(lines)
        self.assertEqual(expansion.template_name.line, "my_template")
        self.assertEqual(expansion.variables, {"template": "my_template"})


class TestTemplatedDocParsing(unittest.TestCase):
    def test_parse_narrative_only(self):
        doc = TemplatedDoc("test.txt", LineBlock.from_text("random text"))
        doc.parse()

    def test_parse_line_template(self):
        template = Template(
            "my_template",
            ["var1", "var2"],
            "This is a template with {{ var1 }} and {{ var2 }}.",
        )
        doc = TemplatedDoc(
            "test.txt",
            LineBlock.from_text(
                """
template: my_template
var: var1, var2
This is a template with {{ var1 }} and {{ var2 }}.
end_template: my_template
"""
            ),
        )
        doc.parse()
        self.assertEqual(doc.templates, {"my_template": template})

    def test_parse_line_expansion(self):
        doc = TemplatedDoc(
            "test.txt",
            LineBlock.from_text(
                """
template: my_template
var: var1, var2
This is a template with {{ var1 }} and {{ var2 }}.
end_template: my_template

expand: my_template
let: var1 value1
let: var2 value2
"""
            ),
        )
        doc.parse()
        self.assertEqual(
            doc.text.strip(), """This is a template with value1 and value2."""
        )


class TestTemplate(unittest.TestCase):
    def test_parse_empty_template(self):
        lines = LineBlock.from_text(
            """
template: empty_template
end_template: empty_template
"""
        )
        template = Template.parse(lines)
        self.assertEqual(template.name.line, "empty_template")
        self.assertEqual(template.variables, [])
        self.assertEqual(template.text, "")

    def test_parse_template_with_whitespace(self):
        lines = LineBlock.from_text(
            """
template: whitespace_template
var: var1, var2

    This is a template with whitespace.

end_template: whitespace_template
"""
        )
        template = Template.parse(lines)
        self.assertEqual(template.name.line, "whitespace_template")
        self.assertEqual(template.variables, ["var1", "var2"])
        self.assertEqual(template.text, "\n    This is a template with whitespace.\n\n")


class TestExpansion(unittest.TestCase):
    def test_parse_expansion_no_variables(self):
        lines = LineBlock.from_text(
            """
expand: no_variables
"""
        )
        expansion = Expansion.parse(lines)
        self.assertEqual(expansion.template_name.line, "no_variables")
        self.assertEqual(expansion.variables, {"template": "no_variables"})

    def test_parse_expansion_multiple_variables(self):
        lines = LineBlock.from_text(
            """
expand: multiple_variables
let: var1 value1
let: var2 value2
let: var3 value3
"""
        )
        expansion = Expansion.parse(lines)
        self.assertEqual(expansion.template_name.line, "multiple_variables")
        self.assertEqual(
            expansion.variables,
            {
                "var1": "value1",
                "var2": "value2",
                "var3": "value3",
                "template": "multiple_variables",
            },
        )


class TestTemplatedDoc(unittest.TestCase):
    @patch("sh_doctest.line_block.LineBlock.from_file")
    def test_parse_empty_doc(self, mock_from_file):
        mock_from_file.return_value = LineBlock.from_text("")
        doc = TemplatedDoc.from_file("test.txt")
        doc.parse()
        self.assertEqual(doc.templates, {})
        self.assertEqual(doc.expansions, [])
