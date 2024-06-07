import unittest
from sh_doctest.numbered_line import NumberedLine


class TestNumberedLine(unittest.TestCase):
    def test_init(self):
        line = NumberedLine("Hello", 1)
        self.assertEqual(line.line, "Hello")
        self.assertEqual(line.lineno, 1)

    def test_repr(self):
        line = NumberedLine("Hello", 1)
        self.assertEqual(repr(line), "NumberedLine('Hello', 1)")

    def test_str(self):
        line = NumberedLine("Hello", 1)
        self.assertEqual(str(line), "Hello")

    def test_len(self):
        line = NumberedLine("Hello", 1)
        self.assertEqual(len(line), 5)

    def test_eq(self):
        line1 = NumberedLine("Hello", 1)
        line2 = NumberedLine("Hello", 2)
        line3 = NumberedLine("World", 1)
        self.assertTrue(line1 == line2)
        self.assertFalse(line1 == line3)
        self.assertTrue(line1 == "Hello")
        self.assertFalse(line1 == "World")

    def test_ne(self):
        line1 = NumberedLine("Hello", 1)
        line2 = NumberedLine("Hello", 2)
        line3 = NumberedLine("World", 1)
        self.assertFalse(line1 != line2)
        self.assertTrue(line1 != line3)
        self.assertFalse(line1 != "Hello")
        self.assertTrue(line1 != "World")

    def test_lt(self):
        line1 = NumberedLine("Hello", 1)
        line2 = NumberedLine("World", 2)
        self.assertTrue(line1 < line2)
        self.assertFalse(line2 < line1)
        self.assertTrue(line1 < "World")
        self.assertFalse(line1 < "Hello")

    def test_getitem(self):
        line = NumberedLine("Hello", 1)
        self.assertEqual(line[0], NumberedLine("H", 1))
        self.assertEqual(line[0:2], NumberedLine("He", 1))

    def test_bool(self):
        line1 = NumberedLine("Hello", 1)
        line2 = NumberedLine("", 2)
        self.assertTrue(bool(line1))
        self.assertFalse(bool(line2))

    def test_strip(self):
        line = NumberedLine("  Hello  ", 1)
        self.assertEqual(line.strip(), NumberedLine("Hello", 1))
        self.assertNotEqual(line.strip("H"), NumberedLine("ello  ", 1))

    def test_copy(self):
        line = NumberedLine("Hello", 1)
        copy = line.copy()
        self.assertEqual(copy.line, line.line)
        self.assertEqual(copy.lineno, line.lineno)
        self.assertIsNot(copy, line)

    def test_startswith(self):
        line = NumberedLine("Hello World", 1)
        self.assertTrue(line.startswith("He"))
        self.assertFalse(line.startswith("Wo"))
        self.assertTrue(line.startswith(("He", "Wo")))

    def test_endswith(self):
        line = NumberedLine("Hello World", 1)
        self.assertTrue(line.endswith("ld"))
        self.assertFalse(line.endswith("He"))
        self.assertTrue(line.endswith(("ld", "He")))


if __name__ == "__main__":
    unittest.main()
