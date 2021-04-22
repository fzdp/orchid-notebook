import wx
import images
from .generic_bitmap_button import GenericBitmapButton
from pubsub import pub
from datetime import datetime


class _ToolColor(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._init_ui()
        self.display_color('#000000')

    def _init_ui(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(GenericBitmapButton(self, 'tool_color'))
        self.color_indicator = wx.StaticLine(self, size=(-1, 2))
        self.main_sizer.Add(self.color_indicator, flag=wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def display_color(self, color):
        self.color_indicator.SetBackgroundColour(color)


class TextEditorToolbar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.editor = parent
        self._init_ui()
        self._init_event()

    def _init_ui(self):
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.tool_font_name = wx.Choice(self, choices=['Helvetica', 'Arial', 'sans-serif'], size=(100, -1))
        self.tool_font_size = wx.Choice(self, choices=['12','13','14','16','18','24','36','48','72'], style=wx.CB_SORT, size=(50, -1))
        self.tool_bold = GenericBitmapButton(self, 'tool_bold')
        self.tool_italic = GenericBitmapButton(self, 'tool_italic')
        self.tool_underline = GenericBitmapButton(self, 'tool_underline')
        self.tool_color = _ToolColor(self)
        self.tool_background = GenericBitmapButton(self, 'tool_background')
        self.tool_quote = GenericBitmapButton(self, 'tool_quote')
        self.tool_code_block = GenericBitmapButton(self, 'tool_code_block')
        self.tool_bullet_list = GenericBitmapButton(self, 'tool_bullet_list')
        self.tool_ordered_list = GenericBitmapButton(self, 'tool_ordered_list')
        self.tool_align = wx.Choice(self, choices=[
            _("text_editor_toolbar.align_left"), _("text_editor_toolbar.align_center"),
            _("text_editor_toolbar.align_right"), _("text_editor_toolbar.justify_align")
        ], size=(100, -1))

        self.tool_time = GenericBitmapButton(self, 'tool_time')
        self.tool_info = GenericBitmapButton(self, 'tool_info')
        self.tool_full_screen = GenericBitmapButton(self, 'tool_full_screen')
        self.tool_more_action = GenericBitmapButton(self, 'tool_more_action')

        self.main_sizer.AddSpacer(2)
        self.main_sizer.Add(self.tool_font_name, flag=wx.RIGHT, border=5)
        self.main_sizer.Add(self.tool_font_size, flag=wx.RIGHT, border=5)
        self.main_sizer.Add(self.tool_align, flag=wx.RIGHT, border=5)
        self.main_sizer.Add(self.tool_bold, flag=wx.RIGHT, border=3)
        self.main_sizer.Add(self.tool_italic, flag=wx.RIGHT, border=4)
        self.main_sizer.Add(self.tool_underline, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_color, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_background, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_quote, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_code_block, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_bullet_list, flag=wx.RIGHT, border=8)
        self.main_sizer.Add(self.tool_ordered_list, flag=wx.RIGHT, border=20)
        self.main_sizer.Add(self.tool_time, flag=wx.RIGHT, border=9)
        self.main_sizer.Add(self.tool_info, flag=wx.RIGHT, border=9)
        self.main_sizer.Add(self.tool_full_screen, flag=wx.RIGHT, border=9)
        self.main_sizer.Add(self.tool_more_action)

        self.SetSizer(self.main_sizer)

    def _init_event(self):
        self.tool_font_name.Bind(wx.EVT_CHOICE, self._on_font_name_selected)
        self.tool_font_size.Bind(wx.EVT_CHOICE, self._on_font_size_selected)
        self.tool_bold.Bind(wx.EVT_BUTTON, self._on_bold_clicked)
        self.tool_italic.Bind(wx.EVT_BUTTON, self._on_italic_clicked)
        self.tool_underline.Bind(wx.EVT_BUTTON, self._on_underline_clicked)
        self.tool_color.Bind(wx.EVT_BUTTON, self._on_fg_color_clicked)
        self.tool_background.Bind(wx.EVT_BUTTON, self._on_bg_color_clicked)
        self.tool_quote.Bind(wx.EVT_BUTTON, self._on_quote_clicked)
        self.tool_code_block.Bind(wx.EVT_BUTTON, self._on_code_block_clicked)
        self.tool_bullet_list.Bind(wx.EVT_BUTTON, self._on_bullet_list_clicked)
        self.tool_ordered_list.Bind(wx.EVT_BUTTON, self._on_ordered_list_clicked)
        self.tool_align.Bind(wx.EVT_CHOICE, self._on_align_selected)
        self.tool_info.Bind(wx.EVT_BUTTON, self._on_info_clicked)
        self.tool_time.Bind(wx.EVT_BUTTON, self._on_time_clicked)
        self.tool_full_screen.Bind(wx.EVT_BUTTON, self._on_full_screen_clicked)

    def _on_time_clicked(self, e):
        current_time = datetime.now()
        weekdays = [_("day1"), _("day2"), _("day3"), _("day4"), _("day5"), _("day6"), _("day7")]
        ymd = current_time.strftime('%Y-%m-%d')
        hms = current_time.strftime('%H:%M:%S')
        weekday = weekdays[current_time.weekday()]
        self.editor.webview.run_js('quill.insertTime', f"{ymd} {weekday} {hms}")

    def _on_italic_clicked(self, e):
        format_val = not self.editor.content_format['italic']
        self.editor.format_content('italic', format_val)
        self._display_italic_format()

    def _display_italic_format(self):
        bitmap = images.tool_italic_active.Bitmap if self.editor.content_format['italic'] else images.tool_italic.Bitmap
        self.tool_italic.SetBitmap(bitmap)

    def _on_underline_clicked(self, e):
        format_val = not self.editor.content_format['underline']
        self.editor.format_content('underline', format_val)
        self._display_underline_format()

    def _display_underline_format(self):
        bitmap = images.tool_underline_active.Bitmap if self.editor.content_format['underline'] else images.tool_underline.Bitmap
        self.tool_underline.SetBitmap(bitmap)

    def _on_quote_clicked(self, e):
        format_val = not self.editor.content_format['blockquote']
        self.editor.format_content('blockquote', format_val)
        self._display_quote_format()

    def _display_quote_format(self):
        bitmap = images.tool_quote_active.Bitmap if self.editor.content_format['blockquote'] else images.tool_quote.Bitmap
        self.tool_quote.SetBitmap(bitmap)

    def _on_bullet_list_clicked(self, e):
        format_val = False if self.editor.content_format['list'] == 'bullet' else 'bullet'
        self.editor.format_content('list', format_val)
        self._display_list_format()

    def _display_list_format(self):
        format_val = self.editor.content_format['list']
        if format_val is False:
            self.tool_ordered_list.SetBitmap(images.tool_ordered_list.Bitmap)
            self.tool_bullet_list.SetBitmap(images.tool_bullet_list.Bitmap)
        elif format_val == 'bullet':
            self.tool_ordered_list.SetBitmap(images.tool_ordered_list.Bitmap)
            self.tool_bullet_list.SetBitmap(images.tool_bullet_list_active.Bitmap)
        elif format_val == 'ordered':
            self.tool_ordered_list.SetBitmap(images.tool_ordered_list_active.Bitmap)
            self.tool_bullet_list.SetBitmap(images.tool_bullet_list.Bitmap)

    def _on_ordered_list_clicked(self, e):
        format_val = False if self.editor.content_format['list'] == 'ordered' else 'ordered'
        self.editor.format_content('list', format_val)
        self._display_list_format()

    def _on_align_selected(self, e):
        format_val = {
            _("text_editor_toolbar.align_left"): False, _("text_editor_toolbar.align_center"): 'center',
            _("text_editor_toolbar.align_right"): 'right', _("text_editor_toolbar.justify_align"): 'justify'
        }.get(e.String, False)
        self.editor.format_content('align', format_val)

    def _display_align_format(self):
        align_val = self.editor.content_format['align']
        if isinstance(align_val, list):
            align_val = align_val[0]
        format_val = {
            False: _("text_editor_toolbar.align_left"), 'center': _("text_editor_toolbar.align_center"),
            'right': _("text_editor_toolbar.align_right"), 'justify': _("text_editor_toolbar.justify_align")
        }.get(align_val, '左对齐')
        self.tool_align.SetSelection(self.tool_align.GetItems().index(format_val))

    def _on_info_clicked(self, e):
        pass

    def _on_full_screen_clicked(self, e):
        if self.editor.is_full_screen:
            self.editor.is_full_screen = False
            self.tool_full_screen.SetBitmap(images.tool_full_screen.Bitmap)
        else:
            self.editor.is_full_screen = True
            self.tool_full_screen.SetBitmap(images.tool_full_screen_active.Bitmap)
        pub.sendMessage('note.full_screen',enable=self.editor.is_full_screen)

    def _on_font_name_selected(self, e):
        self.editor.format_content('font', e.String)

    def _on_font_size_selected(self, e):
        self.editor.format_content('size', f'{e.String}px')

    def _on_bold_clicked(self, e):
        format_val = not self.editor.content_format['bold']
        self.editor.format_content('bold', format_val)
        self._display_bold_format()

    def _on_fg_color_clicked(self, e):
        color = wx.GetColourFromUser(self, self.editor.content_format['color'] or '#000000').GetAsString(wx.C2S_HTML_SYNTAX)
        self.editor.format_content('color', color)
        self._display_color_format()

    def _on_bg_color_clicked(self, e):
        color = wx.GetColourFromUser(self, self.editor.content_format['background'] or '#ffffff').GetAsString(wx.C2S_HTML_SYNTAX)
        self.editor.format_content('background', color)
        self._display_background_format()

    def _on_code_block_clicked(self, e):
        format_val = not self.editor.content_format['code-block']
        self.editor.format_content('code-block',format_val)
        self._display_code_block_format()

    def _display_bold_format(self):
        bitmap = images.tool_bold_active.Bitmap if self.editor.content_format['bold'] else images.tool_bold.Bitmap
        self.tool_bold.SetBitmap(bitmap)

    def _display_code_block_format(self):
        bitmap = images.tool_code_block_active.Bitmap if self.editor.content_format['code-block'] else images.tool_code_block.Bitmap
        self.tool_code_block.SetBitmap(bitmap)

    def _display_font_format(self):
        format_val = self.editor.content_format['font']
        if format_val is False:
            index = 0
        elif format_val in self.tool_font_name.GetItems():
            index = self.tool_font_name.GetItems().index(self.editor.content_format['font'])
        else:
            index = self.tool_font_name.Append(format_val)
        self.tool_font_name.SetSelection(index)

    def _display_size_format(self):
        format_val = self.editor.content_format['size']
        if format_val is False:
            index = 0
        # todo handle em rem
        elif format_val[:-2] in self.tool_font_size.GetItems():
            index = self.tool_font_size.GetItems().index(format_val[:-2])
        else:
            index = self.tool_font_size.Append(format_val[:-2])
        self.tool_font_size.SetSelection(index)

    def _display_color_format(self):
        self.tool_color.display_color(self.editor.content_format['color'] or '#000000')

    def _display_background_format(self):
        self.tool_background.SetBackgroundColour(self.editor.content_format['background'] or '#ffffff')
        self.tool_background.Refresh()

    def display_format(self, changed_format):
        if 'bold' in changed_format:
            self._display_bold_format()
        if 'font' in changed_format:
            self._display_font_format()
        if 'italic' in changed_format:
            self._display_italic_format()
        if 'underline' in changed_format:
            self._display_underline_format()
        if 'blockquote' in changed_format:
            self._display_quote_format()
        if 'list' in changed_format:
            self._display_list_format()
        if 'size' in changed_format:
            self._display_size_format()
        if 'color' in changed_format:
            self._display_color_format()
        if 'background' in changed_format:
            self._display_background_format()
        if 'code-block' in changed_format:
            self._display_code_block_format()
        if 'align' in changed_format:
            self._display_align_format()
