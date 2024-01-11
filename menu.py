from simple_term_menu import TerminalMenu


class Menu:
    def __init__(self, title, items, exit_option=False, multi_select=False):
        self.multiSelect = multi_select
        self.back_text = 'Back'
        self.exit_text = 'Exit'

        self.title = title
        self.items = items + ([self.back_text] if not exit_option else [self.exit_text])
        self.menu = self.create_menu()

    def get_selection(self):
        selection = self.menu.show()

        # Selection is None if the user pressed Esc, in which case a return is requested
        if selection is None:
            return [self.exit_text]

        # Returns a list with all selected items if there are multiple selections
        if isinstance(selection, list):
            return [self.items[i] for i in selection]
        elif isinstance(selection, tuple):
            return list(selection)
        else:
            return [self.items[selection]]

    def create_menu(self):
        cursor = "> "
        cursor_style = ("fg_red", "bold")
        menu_style = ("bg_red", "fg_yellow")

        return TerminalMenu(
            menu_entries=self.items,
            title=self.make_title_string(self.title),
            menu_cursor=cursor,
            menu_cursor_style=cursor_style,
            menu_highlight_style=menu_style,
            cycle_cursor=True,
            clear_screen=True,
            multi_select=self.multiSelect
        )

    def make_title_string(self, title: str):
        return self.get_app_title() + f'\n{title}'

    @staticmethod
    def get_app_title():
        return "" \
               "\n.-.   .-. .----. .----..----. " \
               "\n|  `.'  |{ {__  { {__  | {}  }" \
               "\n| |\ /| |.-._} }.-._} }| .--' " \
               "\n`-' ` `-'`----' `----' `-'    " \
               "\n"

    def has_requested_return(self, selection) -> bool:
        if selection is None:
            return True
        elif isinstance(selection, list):
            return any(item in [self.back_text, self.exit_text, None] for item in selection)
        else:
            return selection in [self.back_text, self.exit_text, None]
