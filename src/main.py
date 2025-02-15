# main.py
#
# Copyright 2024 Qwery
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import shutil
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from addwater.apps.firefox.firefox_details import (
    FatalAppDetailsError,
    FirefoxAppDetails,
)
from addwater.backend import BackendFactory
from gi.repository import Adw, Gio, GLib, Gtk

from addwater import info

from .preferences import AddWaterPreferences
from .utils import paths
from .utils.background import BackgroundUpdater
from .utils.logs import init_logs
from .window import AddWaterWindow

log = logging.getLogger(__name__)


class AddWaterApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id=info.APP_ID, flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )
        self.create_action("quit", lambda *_: self.quit(), ["<primary>q", "<primary>w"])
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action, ["<Ctrl>comma"])
        self.create_action("open-help-page", self.on_help_action)
        self.create_action("reset-app", self.on_reset_app_action)

        paths.init_paths()
        init_logs()

        self.backends = self.construct_backends()

        self.add_main_option(
            "quick-update",
            ord("q"),
            GLib.OptionFlags.IN_MAIN,
            GLib.OptionArg.NONE,
            "Quickly update and install theme with the last-used settings",
            None,
        )

    def do_command_line(self, command_line):
        """Handles command line args and options if given, or starts the GUI
        window if none are provided.
        """
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if options or info.FORCE_BG == "True":
            try:
                self.handle_background_update(options)
                return 0
            except CommandMisuseException as err:
                log.error(f"Use --help for proper usage notes: {err}")
                return 1

        self.activate()
        return 0

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """

        # Create window with the logic it needs
        win = self.props.active_window
        if not win:
            win = AddWaterWindow(application=self, backends=self.backends)

        # TODO make this error handling better and more explicit
        if not self.backends:
            win.error_page()
        win.present()

    def handle_background_update(self, options):
        if info.FORCE_BG == "True":
            options = {"quick-update": True}

        # TODO handle the option better and handle the error better
        if "quick-update" in options and options["quick-update"]:
            if not self.backends:
                log.error("Cannot find Firefox Profile Data")
                log.info(
                    "Please ensure Firefox is installed and Add Water has permission to access your profiles."
                )
                return

            background_updater = BackgroundUpdater(self.backends[0])
            background_updater.quick_update()

            notif = background_updater.get_status_notification()
            if notif:
                self.send_notification("addwater-bg-update-status", notif)
            return

        raise CommandMisuseException(f"Unknown options: {options}")

    def construct_backends(self):
        # TODO make this dynamic to find all available app details
        backends = []
        try:
            app_detail = FirefoxAppDetails()
        except FatalAppDetailsError:
            return None

        backends.append(BackendFactory.new_from_appdetails(app_detail))

        return backends

    def on_reset_app_action(self, *_):
        log.warning("resetting the entire app...")

        settings = Gio.Settings(info.APP_ID)
        settings.reset("background-update")

        for each in self.backends:
            each.reset_app()

        try:
            shutil.rmtree(paths.DOWNLOAD_DIR)
        except FileNotFoundError:
            pass
        log.info("deleted download folder")

        log.info("app has been reset and will now exit")
        self.quit()

    # TODO make a custom issue page that bundles log files, the help page link,
    # and the issue link in a single navpage.
    # The debugging page doesn't work for me because the logs are already a file.
    def on_about_action(self, *_):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(
            application_name="Add Water",
            application_icon=info.APP_ID,
            issue_url=info.ISSUE_TRACKER,
            website=info.WEBSITE,
            developer_name="qwery",
            version=info.VERSION,
            developers=["Qwery"],
            copyright="© 2024 Qwery",
            license_type=Gtk.License.GPL_3_0,
        )
        about.add_credit_section(
            name="Theme Created and Maintained by",
            people=["Rafael Mardojai CM https://www.mardojai.com/"],
        )
        about.add_legal_section(
            "Other Wordmarks",
            "Firefox and Thunderbird are trademarks of the Mozilla Foundation in the U.S. and other countries.",
            Gtk.License.UNKNOWN,
            None,
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, *_):
        """Callback for the app.preferences action."""
        pref = AddWaterPreferences(self.backends[0])
        pref.present(self.props.active_window)

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
                name: the name of the action
                callback: the function to be called when the action is
                  activated
                shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_help_action(self, *_):
        log.info("help page action activated")
        weblaunch = Gtk.UriLauncher.new(
            "https://github.com/largestgithubuseronearth/addwater/blob/main/docs/troubleshooting.md"
        )
        weblaunch.launch(None, None, None, None)


def main(version):
    """The application's entry point."""
    app = AddWaterApplication()
    return app.run(sys.argv)


class CommandMisuseException(Exception):
    pass
