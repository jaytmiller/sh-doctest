import re

from .line_block import LineBlock
from .numbered_line import NumberedLine
from .log import log

from jinja2 import Environment, BaseLoader


# log.set_level("DEBUG")

# =====================================================================================================


def transform_placeholders(input_string):
    """This function replaces placeholders/variables of the form <identifier> with Jinja2's
    somewhat more verbose {{ identifier }} syntax.  Note that the placeholder notation is only
    used in the template text itself,  not in the template's definition of its variables where
    only the identifier should be used.

    Returns:
        str: The transformed string with all placeholders replaced with Jinja2's syntax.
    """
    return re.sub(
        r"<(\w+)>", lambda match: "{{ " + match.group(1) + " }}", input_string
    )


def parse_value(keyword: str, line: NumberedLine) -> NumberedLine:
    """Parse a value from a line of text.  The value is the part of the line
    after the first colon.
    """
    try:
        log.debug(f"Parsing {keyword} from: {repr(line)}")
        index = line.line.index(":") + 1
        parts = line[:index], line[index:]
        if len(parts) != 2 or parts[0].strip() != keyword + ":":
            raise ValueError(
                f"Invalid {keyword} format: {line} partitioned to: {repr(parts)}"
            )
        value = parts[1].strip()
    except IndexError:
        # Handle IndexError
        raise ValueError("Malformed template input")
    rval = NumberedLine(value, line.lineno)
    log.debug(f"Parsed {keyword} and {repr(line)} to value: {repr(rval)}")
    return rval


class Template:
    """A template for a test specification which can be rendered to expand
    variables and produce corresponding test case instances.  It is parsed
    from a very simple form of spec like this:

    template: <template name>
    var: v1,v2,...   [optional template variable names, if any, unique, comma-separated list]
    <arbitrary text not starting with template: or var: until end_template: is seen, template name must match>
    end_template: <template name>
    """

    def __init__(
        self, name: NumberedLine, variables: list[NumberedLine], text: str = ""
    ) -> None:
        self.name = NumberedLine(name)
        self.variables = [NumberedLine(var) for var in variables]
        self.text = text

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Template):
            return NotImplemented
        return (
            self.name == other.name
            and self.variables == other.variables
            and self.text.strip() == other.text.strip()
        )

    @classmethod
    def parse(cls, lines: LineBlock) -> "Template":
        """Parse a template from a list of lines."""
        log.debug(f"Parsing template from lines: {lines[0]}")
        name = parse_value("template", lines.pop(0))
        variables = []
        while lines and lines[0].startswith("var:"):
            vars = parse_value("var", lines.pop(0)).split(",")
            variables.extend([var.strip() for var in vars])
        self = cls(name, variables)
        while lines and not lines[0].startswith("end_template:"):
            temp_line = lines.pop(0)
            log.debug(f"Adding line to template: {repr(temp_line)}")
            self.text += transform_placeholders(temp_line.line + "\n")
        if lines:
            end_template = parse_value("end_template", lines.pop(0))
            if name != end_template:
                raise ValueError(
                    f"end_template: {end_template} does not match template: {name}"
                )
        else:
            raise ValueError("Missing end_template")
        return self


class Expansion:
    """A template expansion is used to record a template name and the variables
    and values relative to which it should be expanded.  It has a simple form
    in the spec like this:

    expand: <template name>
    let: username  admin1
    let: run_as    admin1:team1:team2
    let: directory /efs/shared/team1

    The expansion ends with anything other than a line beginning with let:
    """

    def __init__(self, template_name: NumberedLine, variables: dict[str, str]) -> None:
        self.template_name = NumberedLine(template_name)
        self.variables = variables

    @classmethod
    def parse(cls, lines: LineBlock) -> "Expansion":
        """Parse a template from a list of lines."""
        log.debug(f"Parsing expansion from lines: {lines}")
        name = parse_value("expand", lines.pop(0))
        variables = {}
        while lines and lines[0].startswith("let:"):
            line = lines.pop(0)
            vars = parse_value("let", line).split()
            if len(vars) == 2:
                var, value = vars
                log.debug(f"Adding {var}={value} to expansion")
                variables[var.line] = value.line
            else:
                raise ValueError(f"let:  {repr(line)} parses to {repr(vars) }")
        variables["template"] = name.line
        return Expansion(name, variables)


class TemplatedDoc:
    """Within the bounds of template definition and expansion notations,
    a templated document describes relatively arbitrary text using with a
    simple grammar like this:

    TemplatedDoc ::= DocPart*
    DocPart ::= Text | Template | TemplateExpansion
    Text ::= .*
    """

    def __init__(
        self,
        path: str,
        lines: LineBlock = LineBlock(),
        templates: dict[str, Template] = {},
        expansions: list[Expansion] = [],
    ) -> None:
        self.path = path
        # Here we work around mutable default parameter values by replacing them with equivalent
        # dynamically allocated values.  This gets around mypy complaints about using None as a
        # default value for a mutable type in exactly the same way.  Note that forgetting to
        # replace these placeholder defaults introduces a subtle but well known bug whereby the
        # default value is a mutable singleton which can be inherited by future callers.
        self.lines = lines or LineBlock()
        self.templates = templates or {}
        self.expansions = expansions or []
        self.text = ""

    @classmethod
    def from_file(cls, path: str) -> "TemplatedDoc":
        """Create a templated document from a file."""
        lines = LineBlock.from_file(path)
        self = cls(path, lines)
        return self

    def parse(self) -> None:
        """Parse the templated document into a list of templates and template
        expansions.
        """
        last_len = len(self.lines)
        while self.lines:
            try:
                self.parse_element()
            except KeyboardInterrupt as e:
                line = self.lines[0] if self.lines else "<empty>"
                log.exception("Interrupt", self.path, "at", line, ":", repr(e))
                raise
            except Exception as e:
                line = self.lines[0] if self.lines else "<empty>"
                log.exception("Error parsing", self.path, ":", repr(e))
            last_len = self.break_on_loop(last_len)

    def break_on_loop(
        self, last_len: int
    ) -> int:  # Factored out so it can be mocked to null
        new_len = len(self.lines)
        if self.lines and new_len == last_len:
            raise RuntimeError(f"Infinite loop parsing {self.path}")
        return new_len

    def parse_element(self) -> None:
        log.debug(f"Parsing {repr(self.lines[0])}")
        line = self.lines[0]
        if line.startswith("template:"):
            template = Template.parse(self.lines)
            self.templates[template.name.line] = template
        elif line.startswith("expand:"):
            expansion = Expansion.parse(self.lines)
            template = self.templates[expansion.template_name.line]
            text = self.render(template.text, expansion.variables)
            self.text += text + "\n"
            self.expansions.append(expansion)
        else:
            log.debug(f"Skipping narrative {repr(line)}")
            text = self.lines.pop(0).line
            self.text += text + "\n"

    def render(self, template_str: str, variables: dict[str, str]) -> str:
        """Render a template pattern using the given variables."""
        environment = Environment(loader=BaseLoader())
        template = environment.from_string(template_str)
        rendered_text = template.render(variables)
        return rendered_text

    def writeto(self, path: str) -> None:
        """Save the templated document to a file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text + "\n")
