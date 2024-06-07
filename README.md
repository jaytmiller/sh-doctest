==========
sh-doctest
==========

This package was inspired by Python's doctest module and my own personal
preference for writing declarative test specifications which
express expected results in a natural way as interpreter or console
inputs and output vs. a programmatic test specification.

The goal of the package is to support test specifications which are simple to
read and write and run them in an easily repeatable way.

Like doctest, the specifications intermingle narrative text with code snippets
and expected results.  Unlike doctest, the sh_doctest specs are oriented
towards testing shell scripts or interactive shell commands.

Writing test specs
------------------

Test specifications are written in a simple language which makes it
easy to express narrative text, code snippets, and expected results.

Similarly,  under the assumption that the runner is running as a root
process,  the spec provides a mechanism for running test commands
using particular users and/or groups.

The abstract test spec syntax is roughly as follows:

```
<spec> :=  <case>+

case := <narrative_text> <bl> <name> <run_as> <command> <exit_code> <expected_stdout> <expected_stderr>

narrative_text :=  <anything-including-blank-lines-but-keyword-directives>> <bl>

name := 'name:' \s?\w+
name :=

run_as := run_as:\w+
run_as := run_as:\w+:\w+
run_as := run_as:\w+:\w+:\w+(,\w+)*
run_as :=

command := '$' <bash-commands> <eol> <command>
command := '$' <bash-commands> <eol>

exit_code :=  'exit_code:' \s? (\d+|ok|fail|ignore_stdout)
exit_code :=

expected_stdout := <anything-except-blank-line-or-!!-starting-newline>
expected_stdout :=

expected_stderr := '!!\n' <anything-except-blank-line>
expected_stderr :=
