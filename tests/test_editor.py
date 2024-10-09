import unittest
import wx
from src.editor import Editor
from src.utils.file_operations import read_file, write_file
import os
import tempfile

class TestEditor(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.editor = Editor()

    def tearDown(self):
        self.editor.ui.Destroy()
        self.app.Destroy()

    def test_new_file(self):
        self.editor.new_file()
        current_content = self.editor.ui.get_current_content()
        self.assertEqual(current_content, "")

    def test_open_and_save_file(self):
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write("Test content")
            temp_file_path = temp_file.name

        self.editor.ui.add_tab(temp_file_path, "Test content")
        current_content = self.editor.ui.get_current_content()
        self.assertEqual(current_content, "Test content")

        new_content = "Updated test content"
        self.editor.ui.notebook.GetCurrentPage().SetText(new_content)
        self.editor.save_file()

        saved_content = read_file(temp_file_path)
        self.assertEqual(saved_content, new_content)

        os.unlink(temp_file_path)

    def test_undo_redo(self):
        self.editor.new_file()
        text_ctrl = self.editor.ui.notebook.GetCurrentPage()
        text_ctrl.SetText("Initial")
        text_ctrl.AppendText(" text")
        
        self.editor.undo()
        self.assertEqual(text_ctrl.GetText(), "Initial")
        
        self.editor.redo()
        self.assertEqual(text_ctrl.GetText(), "Initial text")

    def test_find_replace(self):
        self.editor.new_file()
        text_ctrl = self.editor.ui.notebook.GetCurrentPage()
        text_ctrl.SetText("Find and replace this text")
        
        # Simulate find operation
        find_data = wx.FindReplaceData()
        find_data.SetFindString("this")
        event = wx.FindDialogEvent(wx.wxEVT_COMMAND_FIND)
        event.SetEventObject(self.editor.ui)
        event.SetFindString("this")
        self.editor.ui.do_find(event, text_ctrl)
        
        self.assertEqual(text_ctrl.GetSelectedText(), "this")

        # Simulate replace operation
        find_data.SetReplaceString("that")
        event = wx.FindDialogEvent(wx.wxEVT_COMMAND_FIND_REPLACE)
        event.SetEventObject(self.editor.ui)
        event.SetFindString("this")
        event.SetReplaceString("that")
        self.editor.ui.do_replace(event, text_ctrl)
        
        self.assertEqual(text_ctrl.GetText(), "Find and replace that text")

if __name__ == '__main__':
    unittest.main()
