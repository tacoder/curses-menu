import curses
import os
import platform


class CursesMenu():
    currently_active_menu = None

    def __init__(self, title=None, subtitle=None, items=None, exit_option=True, parent=None):
        """
        :param title: the title of the menu
        :type title: str
        :param subtitle: the subtitle of the menu
        :type subtitle: str
        :param items:
        :param exit_option:
        :param parent:
        :return:
        """
        self.screen = None
        self.highlight = None
        self.normal = None
        self._set_up_screen()
        self._set_up_colors()

        self.title = title
        self.subtitle = subtitle
        self.show_exit_option = exit_option
        if items is None:
            self.items = list()
        else:
            self.items = items
        self.parent = parent

        if parent is None:
            self.exit_item = ExitItem("Exit", self)
        else:
            self.exit_item = ExitItem("Return to %s menu" % parent.title, self)

        self.current_option = 0
        self.selected_option = -1

        self.returned_value = None

        self.should_exit = False

    @property
    def current_item(self):
        """
        :rtype: MenuItem or None
        """
        if self.items:
            return self.items[self.current_option]
        else:
            return None

    @property
    def selected_item(self):
        """
        :rtype: MenuItem or None
        """
        if self.items and self.selected_option != -1:
            return self.items[self.current_option]
        else:
            return None

    def add_item(self, item):
        self.remove_exit()
        self.items.append(item)

    def add_exit(self):
        if self.items:
            if self.items[-1] is not self.exit_item:
                self.items.append(self.exit_item)

    def remove_exit(self):
        if self.items:
            if self.items[-1] is self.exit_item:
                del self.items[-1]

    def _set_up_screen(self):
        self.screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(1)

    def _set_up_colors(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlight = curses.color_pair(1)
        self.normal = curses.A_NORMAL

    def show(self, exit_option=None):
        if exit_option is None:
            exit_option = self.show_exit_option

        if exit_option:
            self.add_exit()
        else:
            self.remove_exit()

        CursesMenu.currently_active_menu = self

        self.draw()
        while not self.should_exit:
            self.process_user_input()

        self.remove_exit()
        clean_up_screen()
        return self.returned_value

    def draw(self):
        self.screen.border(0)
        if self.title is not None:
            self.screen.addstr(2, 2, self.title, curses.A_STANDOUT)
        if self.subtitle is not None:
            self.screen.addstr(4, 2, self.subtitle, curses.A_BOLD)

        for index, item in enumerate(self.items):
            if self.current_option == index:
                text_style = self.highlight
            else:
                text_style = self.normal
            self.screen.addstr(5 + index, 4, item.show(index), text_style)
        self.screen.refresh()

    def get_input(self):
        """
        allows for changing to a different input method
        :return:
        """
        return self.screen.getch()

    def process_user_input(self):
        user_input = self.get_input()

        if ord('1') <= user_input <= ord(str(len(self.items) + 1)):
            self.go_to(user_input - ord('0') - 1)
        elif user_input == curses.KEY_DOWN:
            self.go_down()
        elif user_input == curses.KEY_UP:
            self.go_up()
        elif user_input == ord("\n"):
            self.select()

        return user_input

    def go_to(self, option):
        self.current_option = option
        self.draw()

    def go_down(self):
        if self.current_option < len(self.items) - 1:
            self.current_option += 1
        else:
            self.current_option = 0
        self.draw()

    def go_up(self):
        if self.current_option > 0:
            self.current_option += -1
        else:
            self.current_option = len(self.items) - 1
        self.draw()

    def select(self):
        self.selected_option = self.current_option
        self.returned_value = self.selected_item.action()
        self.draw()

    def exit(self):
        clear_terminal()
        self.should_exit = True

    def clear_screen(self):
        self.screen.clear()


class MenuItem:
    def __init__(self, name, menu):
        """
        :type name: str
        :type menu: curses_menu.CursesMenu
        """
        self.name = name
        self.menu = menu

    def __str__(self):
        return "%s %s" % (self.menu.title, self.name)

    def show(self, index):
        return "%d - %s" % (index + 1, self.name)

    def action(self):
        pass


class ExitItem(MenuItem):
    def action(self):
        self.menu.exit()


def clear_terminal():
    if platform.system().lower() == "windows":
        os.system('cls')
    else:
        os.system('reset')


def clean_up_screen():
    curses.endwin()
    clear_terminal()


def reset_prog_mode():
    curses.reset_prog_mode()  # reset to 'current' curses environment
    curses.curs_set(1)  # reset doesn't do this right
    curses.curs_set(0)
