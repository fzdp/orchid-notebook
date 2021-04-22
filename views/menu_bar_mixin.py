import wx
from .generic_menu_mixin import GenericMenuMixin


class MenuBarMixin(GenericMenuMixin):
    def setup_menu_bar(self, menu_params):
        menu_bar = wx.MenuBar()
        self.setup_menu_params(menu_params)
        self.setup_menu_ui(menu_params, menu_bar)
        self.SetMenuBar(menu_bar)
