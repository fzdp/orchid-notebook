import wx
import wx.lib.agw.customtreectrl as customtreectrl
from models import Notebook


class NotebookChoiceDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent,title=_("notebook_choice_dialog.title"))
        self.tree_ctrl = customtreectrl.CustomTreeCtrl(self, style=wx.TR_FULL_ROW_HIGHLIGHT,size=(400,200))

        panel_font = self.GetFont()
        panel_font.SetPointSize(panel_font.GetPointSize() + 1)
        self.tree_ctrl.SetFont(panel_font)

        self.tree_ctrl.root = self.tree_ctrl.AddRoot(_("notebook_choice_dialog.root_node"))
        self.tree_ctrl.SetItemData(self.tree_ctrl.root, None)

        total_note_books = Notebook.all()
        root_note_books = list(filter(lambda n: n.parent_id == None, total_note_books))
        child_note_books = list(filter(lambda n: n.parent_id != None, total_note_books))

        for note_book in root_note_books:
            item = self.tree_ctrl.AppendItem(self.tree_ctrl.root, note_book.name, data=note_book.id)
            self._build_note_tree(note_book.id, item, child_note_books)
        self.tree_ctrl.ExpandAll()
        self.tree_ctrl.SetSpacing(20)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.tree_ctrl, flag=wx.EXPAND|wx.TOP,border=20)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL, _("dialog_cancel")))
        btn_ok = wx.Button(self, wx.ID_OK, _("dialog_ok"))
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.Realize()

        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)
        main_sizer.Fit(self)
        self.SetSizer(main_sizer)

        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_OK)

    def _build_note_tree(self, parent_id, parent_item, child_note_books):
        children = list(filter(lambda n: n.parent_id == parent_id, child_note_books))
        for note_book in children:
            item = self.tree_ctrl.AppendItem(parent_item, note_book.name, data=note_book.id)
            self._build_note_tree(note_book.id, item, child_note_books)

    def get_selected_notebook_id(self):
        return self.tree_ctrl.GetSelection().GetData()

    def on_save(self, _):
        self.EndModal(wx.ID_OK)
