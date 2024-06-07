from sh_doctest.line_block import LineBlock
from sh_doctest.numbered_line import NumberedLine


class TestLineBlock:
    def test_init_with_lines(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        assert block.lines == lines

    def test_init_without_lines(self):
        block = LineBlock()
        assert block.lines == []

    def test_bool_false(self):
        block = LineBlock()
        assert not block

    def test_bool_true(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        assert block

    def test_repr(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        expected = "LineBlock([NumberedLine('line1', 1), NumberedLine('line2', 2)])"
        assert repr(block) == expected

    def test_str(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        expected = "line1\nline2"
        assert str(block) == expected

    def test_eq_with_same_lines(self):
        lines1 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        lines2 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block1 = LineBlock(lines1)
        block2 = LineBlock(lines2)
        assert block1 == block2

    def test_eq_with_different_lines(self):
        lines1 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        lines2 = [NumberedLine("line3", 3), NumberedLine("line4", 4)]
        block1 = LineBlock(lines1)
        block2 = LineBlock(lines2)
        assert block1 != block2

    def test_lt_with_same_lines(self):
        lines1 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        lines2 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block1 = LineBlock(lines1)
        block2 = LineBlock(lines2)
        assert not (block1 < block2)

    def test_lt_with_different_lines(self):
        lines1 = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        lines2 = [NumberedLine("line3", 3), NumberedLine("line4", 4)]
        block1 = LineBlock(lines1)
        block2 = LineBlock(lines2)
        assert block1 < block2

    def test_to_simpl(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        expected = ["1: line1", "2: line2"]
        assert block.to_simpl() == expected

    def test_from_text(self):
        text = "line1\nline2\nline3"
        block = LineBlock.from_text(text)
        expected = [
            NumberedLine("line1", 0),
            NumberedLine("line2", 1),
            NumberedLine("line3", 2),
        ]
        assert block.lines == expected

    def test_getitem_with_int(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        assert block[0] == lines[0]
        assert block[1] == lines[1]

    def test_getitem_with_slice(self):
        lines = [
            NumberedLine("line1", 1),
            NumberedLine("line2", 2),
            NumberedLine("line3", 3),
        ]
        block = LineBlock(lines)
        expected = LineBlock([lines[1], lines[2]])
        assert block[1:] == expected

    def test_len(self):
        lines = [
            NumberedLine("line1", 1),
            NumberedLine("line2", 2),
            NumberedLine("line3", 3),
        ]
        block = LineBlock(lines)
        assert len(block) == 3

    def test_append(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        new_line = NumberedLine("line3", 3)
        block.append(new_line)
        expected = [
            NumberedLine("line1", 1),
            NumberedLine("line2", 2),
            NumberedLine("line3", 3),
        ]
        assert block.lines == expected

    def test_str_list(self):
        lines = [NumberedLine("line1", 1), NumberedLine("line2", 2)]
        block = LineBlock(lines)
        expected = ["line1", "line2"]
        assert block.str_list() == expected
