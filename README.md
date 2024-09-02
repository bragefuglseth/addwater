# Add Water
### An installer for the fantastic GNOME for Firefox theme by [Rafael Mardojai CM](https://github.com/rafaelmardojai/firefox-gnome-theme)

## PRIMARY GOALS:
* Give app functionality to run at startup, in the background, and check for + install updates automatically
    * Is the libportal manifest import okay? I copied from AdwSteamGtk 
* Add all Thunderbird and Firefox paths to Flatpak manifest
    * Does Flatpak/Flathub allow for changing file permissions after release?
* Find a good auto linter/formatter
    * Pylint
    * Black 
* Improve implementation of AppDetails and make a generic factory for this
* Properly set up Meson
    * Set up options to enable mocks and easy tests, but disable ALL of these when profile == user
    * Set up properly use my basic unit tests. Kept hitting an error


## SECONDARY GOALS:
* Find good documentation solution
    * doxygen
    * gitbook (service bleh)
    * sphinx
    * read the docs
* Change all type hints to use pathlike

## FLATHUB GOALS:
* Make sure Flatpak is configured properly
    * Ensure flatpak manifest permissions are correct
    * Allow permission to run in background to permissions
    * Is is okay to remove ipc permission? Doesn't seem necessary but idk.
    * Where does $FLATPAK_DEST go to?
* Write .desktop file
* Write appstream info
    * Finish preview images to look nicer
* Smooth out all accessibility issues


## Wrap up
* Set up project for i18n work
* Make docstrings for the classes and methods
* Write help page for user troubleshooting


### Accessibility:
[X] Large Text
[~] Screen Reader tests
    Could find everything except:
    * Can't find label for the bottom action bar
    * Some SwitchRow subtitles are not read aloud. Orca bug?
    * Toasts are not read out
[X] Full keyboard navigation
[X] Contrast
[] Touch screen support
[] Accerciser test (need to resolve imp issue; build from scratch?)


### What needs to happen for Thunderbird support:
* Be able to clone the git repo in Python and self-set rate limits to avoid clogging Github after every minor change
* Set up AddWaterPage to work with both Firefox and Thunderbird


### Other Notes:
* I will not support Experimental options. Users must enable those manually.

