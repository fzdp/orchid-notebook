import wx
from .generic_menu_mixin import GenericMenuMixin


class PopupMenuMixin(GenericMenuMixin):
    def __display_popup_menu(self, popup_menu, event, set_position=True):
        # if set_position:
        #     pos = event.EventObject.GetPosition()
        #     self.PopupMenu(popup_menu, pos.x, pos.y + 30)
        # else:
        #     self.PopupMenu(popup_menu)
        self.PopupMenu(popup_menu)
        popup_menu.Destroy()

    # params:
    # popup_menu_owner: wx.Object
    # menu_items:
    # see GenericMenuMixin for detail
    # fill the menu_params with id and kind info, we can build popup_menus like this:
    # total_popup_menus:
    # {
    #   "popup_menu_owner_id1" : [
    #     dict(item='menu1', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #     dict(item='menu2', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #     dict(item='menu3', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #     dict(item='menu3', sub_items=[
    #         dict(item='sub_menu1', handler=self.on_delete_notebook, id=xxx, kind=wx.ITEM_CHECK),
    #         dict(item='sub_menu2', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #         dict(item='sub_menu3', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #         dict(item='sub_menu4', sub_items=[
    #             dict(item='sub_menu5', handler=self.on_delete_notebook, id=xxx, kind=wx.ITEM_CHECK),
    #             dict(item='sub_menu6', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #             dict(item='sub_menu7', handler=self.on_delete_notebook, id=xxx, kind=xxx)
    #         ]),
    #     ]),
    # ]
    #   "popup_menu_owner_id2" : {
    #           "menu_item_1_id" : {'item': 'item1', 'handler': self.on_item1},
    #           "menu_item_2_id" : {'item': 'item2', 'handler': self.on_item2}
    #            .......
    # }
    #
    def setup_popup_menu(self, menu_item_params, popup_menu_owner, popup_menu_owner_event=None, callback=None):
        popup_menu_key = self.__get_popup_menu_key(popup_menu_owner)
        # events are only bound once
        if hasattr(self, 'total_popup_menus'):
             if popup_menu_key in self.total_popup_menus:
                 return False
        else:
            self.total_popup_menus = {}
            self.total_popup_menu_callbacks = {}
        self.setup_menu_params(menu_item_params)
        self.total_popup_menus[popup_menu_key] = menu_item_params
        if popup_menu_owner_event:
            self.Bind(popup_menu_owner_event, self.show_popup_menu, popup_menu_owner)
        if callback:
            self.total_popup_menu_callbacks[popup_menu_key] = callback

    def show_popup_menu(self, event, callback=None, set_position=True):
        # so we can bind another custom handler
        event.Skip()
        popup_menu_key = self.__get_popup_menu_key(event.EventObject)
        popup_menu = wx.Menu()
        self.setup_menu_ui(self.total_popup_menus.get(popup_menu_key), popup_menu)
        found_callback = callback or self.total_popup_menu_callbacks.get(popup_menu_key)
        if found_callback:
            found_callback(popup_menu)
        self.__display_popup_menu(popup_menu, event, set_position)

    def __get_popup_menu_key(self, control):
        return "popup_menu_{}".format(control.Id)

