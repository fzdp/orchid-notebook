import wx
from ObjectListView import GroupListView, ColumnDefn, Filter, OLVEvent
import images
from utils import TimeUtil
from pubsub import pub


class TodoList(GroupListView):
    class StatusFilter:
        # status: "is_finished", "not_finished", "all"
        def __init__(self, status="not_finished"):
            self.status = status

        def __call__(self, model_objects):
            if self.status == "not_finished":
                return [model for model in model_objects if not model.is_finished]
            elif self.status == 'is_finished':
                return [model for model in model_objects if model.is_finished]
            else:
                return model_objects

        def set_status(self, status):
            self.status = status

    # for text search
    class TextFilter:
        def __init__(self, columns, text=None):
            self.columns = columns
            self.text = text

        def __call__(self, model_objects):
            if not self.text:
                return model_objects
            return [model for model in model_objects if self._contains_text(model)]

        def _contains_text(self, model_object):
            for col in self.columns:
                if self.text.lower() in col.GetStringValue(model_object).lower():
                    return True
            return False

        def set_text(self, text):
            self.text = text

    def __init__(self, parent):
        super().__init__(parent,useExpansionColumn=False,typingSearchesSortColumn=False,style=wx.LC_VRULES|wx.BORDER_NONE)
        self.AddNamedImages('finished', images.todo_finished.GetBitmap())
        self.AddNamedImages('not_finished', images.transparent.GetBitmap())
        group_title_format = "%(title)s (%(count)d)"

        self.SetColumns([
            ColumnDefn(title=_("todo.title"), width=200, valueGetter='title', groupKeyGetter='group',groupKeyConverter=self._display_content_group_key,groupTitleSingleItem=group_title_format,groupTitlePluralItems=group_title_format),
            ColumnDefn(title=_("todo.content"), width=200, valueGetter='content', groupKeyGetter='group',groupKeyConverter=self._display_content_group_key,groupTitleSingleItem=group_title_format,groupTitlePluralItems=group_title_format),
            ColumnDefn(title=_("todo.remark"), width=300, valueGetter='remark', groupKeyGetter=self._get_remark_group_key,isSpaceFilling=True,groupTitleSingleItem=group_title_format,groupTitlePluralItems=group_title_format),
            ColumnDefn(title=_("todo.finished_at"), valueGetter=self._get_finished_at_value, fixedWidth=150,groupKeyGetter=self._get_finished_at_group_key,groupTitleSingleItem=group_title_format,groupTitlePluralItems=group_title_format),
        ])
        self.SetEmptyListMsg(_("todo_list.no_task"))
        self.CreateCheckStateColumn()

        self.checkStateColumn.checkStateGetter = lambda model: model.is_finished

        self.evenRowsBackColor = wx.Colour(245,245,245)
        self.oddRowsBackColor = wx.Colour(255, 255, 255)

        self.text_filter = self.TextFilter(self.columns)
        self.status_filter = self.StatusFilter()
        self.filter = Filter.Chain(self.status_filter, self.text_filter)

        self.rowFormatter = self._row_formatter

        self.Bind(OLVEvent.EVT_ITEM_CHECKED, self._on_item_checked)

    def _on_item_checked(self, e):
        pub.sendMessage('on.todo.checked',model=e.rowModel,is_checked=e.checkState)

    def _row_formatter(self, item, todo):
        if todo.priority == 1:
            item.SetBackgroundColour(wx.YELLOW)
        elif todo.priority == 2:
            item.SetBackgroundColour(wx.RED)

    # override
    def _HandleLeftClickOrDoubleClick(self, e):
        e.Skip()
        if e.LeftDClick() and self.GetSelectedObject():
            pub.sendMessage('on.todo.preview', model=self.GetSelectedObject())

    # override
    def _HandleChar(self, e):
        e.Skip()
        if e.GetKeyCode() == wx.WXK_SPACE and self.GetSelectedObject():
            pub.sendMessage('on.todo.preview', model=self.GetSelectedObject())
            return

    @staticmethod
    def _get_remark_group_key(todo):
        if not todo.remark:
            return _("todo_list.no_remark")
        if len(todo.remark) <= 100:
            return _("todo_list.short_remark")
        else:
            return _("todo_list.long_remark")

    @staticmethod
    def _get_finished_at_value(todo):
        return str(todo.finished_at) if todo.finished_at else ''

    @staticmethod
    def _display_is_finished(todo):
        return ''

    @staticmethod
    def _display_is_finished_group_key(key):
        return _("todo_list.is_finished") if key else _("todo_list.not_finished")

    @staticmethod
    def _get_finished_at_group_key(todo):
        finished_at = todo.finished_at
        if not finished_at:
            return _("todo_list.not_finished")
        if TimeUtil.is_today(finished_at):
            return _("todo_list.today_finished")
        elif TimeUtil.is_yesterday(finished_at):
            return _("todo_list.yesterday_finished")
        else:
            return _("todo_list.previous_finished")

    @staticmethod
    def _display_content_group_key(key):
        return key if key else _("todo.no_group")

    @staticmethod
    def _is_finished_image_getter(todo):
        return 'finished' if todo.is_finished else 'not_finished'

    def add(self, todos):
        if not type(todos) == list:
            todos = [todos]
        self.AddObjects(todos)
        self.Layout()

    def find(self, index):
        return self.GetObjectAt(index)

    def update(self):
        self.RebuildGroups()

    def remove(self, todos):
        if not type(todos) == list:
            todos = [todos]
        self.RemoveObjects(todos)

    def set(self, todos):
        self.SetObjects(todos)
        self.RebuildGroups()

    def empty(self):
        self.text_filter.set_text('')
        self.set(list())

    def get_selected_objects(self):
        return self.GetSelectedObjects()

    def do_text_filter(self, text):
        self.text_filter.set_text(text)
        self.RebuildGroups()

    def do_status_filter(self, status):
        self.status_filter.set_status(status)
        self.RebuildGroups()

    def reset_filter(self):
        self.text_filter.set_text('')
        self.RebuildGroups()