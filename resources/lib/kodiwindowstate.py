import xbmc
import json
import os
from resources.lib.xlogger import Logger
from resources.lib.kwssettings import loadSettings


def _upgrade():
    settings = loadSettings()
    if settings['version_upgrade'] != settings['ADDONVERSION']:
        settings['ADDON'].setSetting(
            'version_upgrade', settings['ADDONVERSION'])


class kwsMonitor(xbmc.Monitor):

    def __init__(self):
        """Starts the background process to monitor window state."""
        xbmc.Monitor.__init__(self)
        _upgrade()
        self._init_vars()
        self.LW.log(['background monitor version %s started' %
                    self.SETTINGS['ADDONVERSION']], xbmc.LOGINFO)
        self.LW.log(['debug logging set to %s' %
                    self.SETTINGS['debug']], xbmc.LOGINFO)
        while not self.abortRequested():
            if self.waitForAbort(10):
                break
        self.LW.log(['background monitor version %s stopped' %
                    self.SETTINGS['ADDONVERSION']], xbmc.LOGINFO)

    def onNotification(self, sender, method, data):
        data = json.loads(data)
        if 'Player.OnPlay' in method:
            self.LW.log(['MONITOR METHOD: %s DATA: %s' %
                        (str(method), str(data))])
            self.KEEPCHECKING = True
            self._check_window_state()
        if 'Player.OnStop' in method:
            self.LW.log(['MONITOR METHOD: %s DATA: %s' %
                        (str(method), str(data))])
            self.waitForAbort(1)
            if not self.KODIPLAYER.isPlaying():
                self.KEEPCHECKING = False

    def onSettingsChanged(self):
        self._init_vars()

    def _init_vars(self):
        self.LW = Logger(
            preamble='[Kodi Window State Service]', logdebug=loadSettings()['debug'])
        self.SETTINGS = loadSettings()
        self.KODIPLAYER = xbmc.Player()
        self.KEEPCHECKING = False
        self.LW.log(['the settings are:', self.SETTINGS])
        self.LW.log(['initialized variables'])

    def _check_window_state(self):
        self.LW.log(['started checking of window ID since playback started'])
        old_window_id = self._get_window_id()
        self.LW.log(['sending window id of %s to Home Assistant' %
                    str(old_window_id)])
        while self.KEEPCHECKING and not self.abortRequested():
            current_window_id = self._get_window_id()
            if (current_window_id != old_window_id):
                old_window_id = current_window_id
                self.LW.log(['sending window id of %s to Home Assistant' %
                             str(old_window_id)])
            self.waitForAbort(1)
        self.LW.log(['ended checking of window ID since playback stopped'])

    def _get_window_id(self):
        response = xbmc.executeJSONRPC(
            '{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow"]},"id":1}')
        return json.loads(response).get('result', {}).get('currentwindow', {}).get('id', [])
