import wx
from functools import partial

class GenericMenuMixin:
    # menu_items = [
    #     dict(item='menu1', handler=self.on_delete_notebook),
    #     dict(item='menu2', handler=self.on_delete_notebook),
    #     dict(item='menu3', handler=self.on_delete_notebook),
    #     dict(item='menu3', sub_items=[
    #         dict(item='sub_menu1', handler=self.on_delete_notebook, kind=wx.ITEM_CHECK),
    #         dict(item='sub_menu2', handler=self.on_delete_notebook),
    #         dict(item='sub_menu3', handler=self.on_delete_notebook),
    #         dict(item='sub_menu4', sub_items=[
    #             dict(item='sub_menu5', handler=self.on_delete_notebook, kind=wx.ITEM_CHECK),
    #             dict(item='sub_menu6', handler=self.on_delete_notebook),
    #             dict(item='sub_menu7', handler=self.on_delete_notebook)
    #         ]),
    #     ]),
    # ]
    #
    # fill the menu_params with id and kind info and bind event handler:
    #
    # menu_items = [
    #   dict(item='menu1', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #   dict(item='menu2', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #   dict(item='menu3', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #   dict(item='menu3', sub_items=[
    #       dict(item='sub_menu1', handler=self.on_delete_notebook, id=xxx, kind=wx.ITEM_CHECK),
    #       dict(item='sub_menu2', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #       dict(item='sub_menu3', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #       dict(item='sub_menu4', sub_items=[
    #           dict(item='sub_menu5', handler=self.on_delete_notebook, id=xxx, kind=wx.ITEM_CHECK),
    #           dict(item='sub_menu6', handler=self.on_delete_notebook, id=xxx, kind=xxx),
    #           dict(item='sub_menu7', handler=self.on_delete_notebook, id=xxx, kind=xxx)
    #       ]),
    #   ]),
    # ]
    #

    def setup_menu_params(self, menu_params):
        for item_dict in menu_params:
            if item_dict.get('sub_items'):
                self.setup_menu_params(item_dict.get('sub_items'))
            else:
                item_dict['item'] = item_dict.get('item','')
                item_dict['id'] = item_dict.get('id', wx.NewIdRef())
                item_dict['kind'] = item_dict.get('kind', wx.ITEM_NORMAL)
                item_dict['help'] = item_dict.get('help', '')
                if item_dict.get('handler'):
                    if item_dict.get('args'):
                        self.Bind(wx.EVT_MENU, partial(item_dict['handler'], args=item_dict['args']), id=item_dict['id'])
                    else:
                        self.Bind(wx.EVT_MENU, item_dict['handler'], id=item_dict['id'])

    def setup_menu_ui(self, menu_params, menu):
        for menu_item_param in menu_params:
            if menu_item_param.get('sub_items'):
                sub_menu = wx.Menu()
                self.setup_menu_ui(menu_item_param.get('sub_items'), sub_menu)
                if isinstance(menu, wx.Menu):
                    menu.AppendSubMenu(sub_menu, menu_item_param['item'])
                elif isinstance(menu, wx.MenuBar):
                    menu.Append(sub_menu, menu_item_param['item'])
            else:
                menu.Append(menu_item_param['id'], menu_item_param['item'], kind=menu_item_param['kind'], helpString=menu_item_param['help'])
