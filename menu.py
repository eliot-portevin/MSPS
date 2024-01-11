from simple_term_menu import TerminalMenu
import time


class Menu:
    def __init__(self, title, items, exitOption=False):
        self.back_text = 'Back'
        self.exit_text = 'Exit'

        self.title = title
        self.items = items + ([self.back_text] if not exitOption else [self.exit_text])
        self.menu = self.create_menu()

    def get_selection(self):
        selection = self.menu.show()

        # Selection is None if user pressed Esc, in which case a return is requested
        if selection is None:
            return self.exit_text

        else:
            return self.items[selection]

    def create_menu(self):
        cursor = "> "
        cursor_style = ("fg_red", "bold")
        menu_style = ("bg_red", "fg_yellow")

        return TerminalMenu(
            menu_entries = self.items,
            title = self.make_title_string(self.title),
            menu_cursor = cursor,
            menu_cursor_style = cursor_style,
            menu_highlight_style = menu_style,
            cycle_cursor = True,
            clear_screen = True
            )

    def make_title_string(self, title: str):
        return self.get_app_title() + f'\n{title}'

    def get_app_title(self):
        return """
                .-.   .-. .----. .----..----. 
                |  `.'  |{ {__  { {__  | {}  }
                | |\ /| |.-._} }.-._} }| .--' 
                `-' ` `-'`----' `----' `-'    
                """

    def has_requested_return(self, selection) -> bool:
        return selection in [self.back_text, self.exit_text, None]