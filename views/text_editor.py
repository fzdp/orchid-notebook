import wx
import wx.html2
import os
import wx.lib.newevent
from utils import ApplicationUtil
from .browser_panel import BrowserPanel
from .popup_menu_mixin import PopupMenuMixin
from pubsub import pub
from .text_editor_toolbar import TextEditorToolbar
from urllib.parse import quote


class TextEditor(wx.Panel, PopupMenuMixin):
    EditorContentChangedEvent, EVT_EDITOR_CONTENT_CHANGED = wx.lib.newevent.NewCommandEvent()

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.BORDER_NONE)
        file_url = f"file://{os.path.join(ApplicationUtil.bundle_dir(),'assets','text_editor','index.html')}"

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.AddSpacer(20)
        self.tc_title = wx.TextCtrl(self,style=wx.BORDER_NONE)
        self.main_sizer.Add(self.tc_title, flag=wx.EXPAND|wx.LEFT|wx.RIGHT,border=15)
        self.main_sizer.AddSpacer(20)

        self.toolbar = TextEditorToolbar(self)
        self.main_sizer.Add(self.toolbar, flag=wx.EXPAND|wx.LEFT, border=15)
        line = wx.StaticLine(self, size=(-1, 1))
        line.SetBackgroundColour("#e5e5e5")
        self.main_sizer.Add(line, flag=wx.EXPAND|wx.TOP, border=25)

        self.webview = BrowserPanel(self, file_url)
        self.main_sizer.Add(self.webview, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.main_sizer)

        self.webview.set_js_bindings([('pyNotifyContentChanged', self._on_content_changed),
                                      ('pyNotifyFormatChanged', self._on_format_changed),
                                      ('pyOnLinkClicked', self.on_link_clicked)])
        self.note = None
        self.SetBackgroundColour(wx.WHITE)

        self.Bind(wx.EVT_TEXT, self._on_title_changed, self.tc_title)
        menu_params = [
            dict(item=_("note.duplicate"), handler=self._on_copying_note),
            dict(item=_("note.move"), handler=self._on_moving_note),
            dict(item=_("text_editor.open_in_browser"), handler=self._on_open_in_browser),
            dict(kind=wx.ITEM_SEPARATOR),
            dict(item=_("note.delete"), handler=self._on_deleting_note)
        ]
        self.setup_popup_menu(menu_params, self.toolbar.tool_more_action, wx.EVT_BUTTON)
        self.is_full_screen = False
        self.content_format = {
            'bold': False,
            'font': False,
            'italic': False,
            'size': False,
            'color': False,
            'underline': False,
            'strike': False,
            'background': False,
            'code-block': False,
            'blockquote': False,
            'list': False,
            'align': False
        }

    def _on_copying_note(self, e):
        pub.sendMessage('on.note.copy', note_id=self.note.id)

    def _on_moving_note(self, e):
        pub.sendMessage('on.note.move', note_id=self.note.id)

    def _on_deleting_note(self, _):
        pub.sendMessage('on.note.delete', note_id=self.note.id)

    def _on_title_changed(self, e):
        if not self.note:
            return None
        wx.CallLater(900, self._notify_title_changed)

    def _notify_title_changed(self):
        self.note.title = self.tc_title.GetValue().strip()
        self.note.save()
        self.update_timestamps()
        wx.CallAfter(pub.sendMessage, 'on.note_title.change', title=self.tc_title.GetValue().strip(), updated_at=self.note.updated_at)
        wx.CallAfter(pub.sendMessage, "note.updated.callback", note=self.note)

    def format_content(self, format_command, format_arg):
        self.webview.SetFocus()
        self.webview.run_js('quill.format', format_command, format_arg, 'user')
        self.content_format[format_command] = format_arg

    def add_note(self, note, query=None):
        self.note = note
        self.tc_title.ChangeValue(note.title)
        self.set_content(note.content)
        self.update_timestamps()
        if query:
            self.mark(query)

    def remove_note(self):
        self.tc_title.ChangeValue('')
        self.clear()
        self.note = None

    def focus_title(self):
        self.tc_title.SetFocus()

    def update_timestamps(self):
        self.toolbar.tool_info.SetToolTip(f'{_("text_editor.tooltip_created", v1=str(self.note.created_at))}\n{_("text_editor.tooltip_updated", v1=str(self.note.updated_at))}')

    def on_link_clicked(self, link):
        wx.LaunchDefaultBrowser(link)

    def _on_format_changed(self, content_format):
        changed_format = {}
        for key, val in self.content_format.items():
            format_val = content_format.pop(key, False)
            if format_val != val:
                self.content_format[key] = format_val
                changed_format[key] = format_val
        if changed_format:
            self.toolbar.display_format(changed_format)

    def _on_content_changed(self, content):
        if not self.note:
            return None
        self.note.set_content(content)
        self.update_timestamps()
        pub.sendMessage('on.note_content.change', content=content, updated_at=self.note.updated_at)

    def _on_open_in_browser(self, _):
        if self.note:
            wx.LaunchDefaultBrowser(f"file://{quote(self.note.content_file)}")

    def set_content(self, value):
        self.webview.run_js("quill.loadContent", value)

    def mark(self, keyword):
        self.webview.run_js("quill.findAll", keyword)

    def clear(self):
        self.webview.run_js("quill.loadContent", '')

