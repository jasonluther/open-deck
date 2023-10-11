from enum import Enum, StrEnum
import math
import pickle

"""
Open Deck's firmware and design provide the capability to have 6 collections of 3 keyboard macros.
Each collection represents one app.
Each macro represents one series of keys to be typed by the virtual keyboard.
This class presents an interface to get/set configuration values.
"""


class AppOption(Enum):
    OPEN_APP_ON_MENU_CHANGE = 1  # Menu Change Opens Computer App
    OPEN_APP_ON_MACRO_USE = 2  # Macro Button Opens Computer App
    SEND_ACTIVE_APP_TO_DECK = 3  # Deck Shows Current Active App
    AUTO_DETECT_SERIAL_PORT = 4  # Auto Detect Port


class AppOptionValue(StrEnum):
    ON = "on"
    OFF = "off"


class OpenDeckConfig:
    def __init__(self, save_file=None, apps_total=6, macros_per_app=3) -> None:
        self._save_file = save_file
        self._apps_total = apps_total
        self._macros_per_app = macros_per_app
        self._app_macros = []
        self._app_options = {}
        for app_slot in range(0, self._apps_total):
            self._app_macros.append({
                "app_display_name": None,
                "app_window_search_name": None,
                "macros": []
            })
            for macro_slot in range(0, self._macros_per_app):
                self._app_macros[app_slot]["macros"].append({
                    "macro_display_name": None,
                    "macro_key_list": None,
                })
        for option in AppOption:
            self._app_options[str(option)] = None
        if self._save_file != None:
            self.persist_load()

    def fw_number_to_app_slot(self, firmware_number) -> int:
        return math.ceil(firmware_number / 3) - 1

    def fw_number_to_macro_slot(self, firmware_number) -> int:
        return (firmware_number - 1) % 3

    def fw_menu_to_app_slot(self, firmware_menu_number) -> int:
        return firmware_menu_number - 1

    def set_app(self, app_slot, app_display_name, app_window_search_name) -> None:
        self._app_macros[app_slot]["app_display_name"] = app_display_name.strip()
        self._app_macros[app_slot]["app_window_search_name"] = app_window_search_name.strip(
        )
        self.persist_save()

    def set_macro(self, app_slot, macro_slot, macro_display_name, macro_key_list) -> None:
        self._app_macros[app_slot]["macros"][macro_slot]["macro_display_name"] = macro_display_name.strip()
        self._app_macros[app_slot]["macros"][macro_slot]["macro_key_list"] = macro_key_list
        self.persist_save()

    def get_app_window_search_name(self, app_slot) -> str:
        return self._app_macros[app_slot]["app_window_search_name"] or ""

    def get_app_slot_for_window_name(self, window_name) -> int | None:
        target = window_name.strip().lower()
        for app_slot in range(0, len(self._app_macros)):
            search_name = self._app_macros[app_slot]["app_window_search_name"]
            if search_name:
                if target in search_name.lower():
                    return app_slot
        return None

    def get_macro_key_list(self, app_slot, macro_slot) -> []:
        return self._app_macros[app_slot]["macros"][macro_slot]["macro_key_list"]

    def get_macro_display_name(self, app_slot, macro_slot) -> str:
        return self._app_macros[app_slot]["macros"][macro_slot]["macro_display_name"] or ""

    def get_app_option(self, option) -> AppOptionValue | None:
        value = self._app_options[str(option)]
        if value:
            return AppOptionValue(value)
        else:
            return None

    def set_app_option(self, option, value) -> None:
        self._app_options[str(option)] = str(value)
        self.persist_save()
        pass

    def __repr__(self) -> str:
        result = "OpenDeckConfig:\n"
        result += "    Macros:\n"
        for app_slot in range(0, self._apps_total):
            menu = app_slot + 1
            result += f"        {app_slot} (menu {menu}): {self._app_macros[app_slot]['app_window_search_name']}\n"
            for macro_slot in range(0, self._macros_per_app):
                button = (app_slot) * self._macros_per_app + macro_slot + 1
                result += f"            {macro_slot} (button {button}): "
                macro = self._app_macros[app_slot]['macros'][macro_slot]
                result += f"{macro['macro_display_name']}: {macro['macro_key_list']}\n"
        result += "    Options:\n"
        for option in self._app_options:
            result += f"            {option}: {self._app_options[option]}\n"
        return result

    def persist_save(self) -> None:
        with open(self._save_file, 'wb') as file:
            pickle.dump(self, file)

    def persist_load(self) -> None:
        try:
            with open(self._save_file, 'rb') as file:
                obj = pickle.load(file)
                self.__dict__.update(obj.__dict__)
        except (FileNotFoundError, EOFError):
            pass
