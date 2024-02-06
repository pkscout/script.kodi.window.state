
from resources.lib.kodisettings import *

SETTINGSLIST = [{'name': 'version_upgrade', 'default': ''},
                {'name': 'ha_ip', 'default': '127.0.0.1'},
                {'name': 'ha_port', 'default': '8123'},
                {'name': 'ha_secure', 'default': False},
                {'name': 'ha_token', 'default': ''},
                {'name': 'debug', 'default': False}
                ]


def loadSettings():
    settings = {}
    settings['ADDON'] = ADDON
    settings['ADDONNAME'] = ADDONNAME
    settings['ADDONLONGNAME'] = ADDONLONGNAME
    settings['ADDONVERSION'] = ADDONVERSION
    settings['ADDONPATH'] = ADDONPATH
    settings['ADDONDATAPATH'] = ADDONDATAPATH
    settings['ADDONICON'] = ADDONICON
    settings['ADDONLANGUAGE'] = ADDONLANGUAGE
    for item in SETTINGSLIST:
        if isinstance(item['default'], bool):
            getset = getSettingBool
        elif isinstance(item['default'], int):
            getset = getSettingInt
        elif isinstance(item['default'], float):
            getset = getSettingNumber
        else:
            getset = getSettingString
        settings[item['name']] = getset(item['name'], item['default'])
    return settings
