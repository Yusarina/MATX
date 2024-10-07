import unittest
from src.editor import Editor

class TestEditor(unittest.TestCase):
    def setUp(self):
        self.editor = Editor()

    def test_new_file(self):
        self.editor.new_file()
        self.assertEqual(self.editor.content, "")

    # Add more tests for open_file, save_file, etc.

if __name__ == '__main__':
    unittest.main()
