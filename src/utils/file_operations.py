import wx

def get_file_path(action, initial_dir=None):
    style = wx.FD_OPEN if action == 'open' else wx.FD_SAVE
    dialog = wx.FileDialog(None, "Open File" if action == 'open' else "Save File",
                           defaultDir=initial_dir or wx.GetHomeDir(),
                           style=style)
    
    if dialog.ShowModal() == wx.ID_OK:
        file_path = dialog.GetPath()
        dialog.Destroy()
        return file_path
    dialog.Destroy()
    return None

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)
