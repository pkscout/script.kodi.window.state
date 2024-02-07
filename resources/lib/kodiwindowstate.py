import xbmc
import xbmcgui
import json
import os
import re
from resources.lib import url
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
        self.FULLSCREENSTATE = 'off'
        self.OLDFULLSCREENSTATE = 'off'
        sensor_id = re.sub('[^0-9a-zA-Z]+', '_', os.uname()[1]).lower()
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        headers['Authorization'] = 'Bearer %s' % self.SETTINGS['ha_token']
        self.JSONURL = url.URL('json', headers=headers)
        self.RESTURL = 'http://%s:%s/api/states/binary_sensor.%s_fullscreen_front' % (
            self.SETTINGS['ha_ip'], self.SETTINGS['ha_port'], sensor_id)
        self.LW.log(['the settings are:', self.SETTINGS])
        self.LW.log(['initialized variables'])

    def _check_window_state(self):
        self.LW.log(['started checking of window ID since playback started'])
        old_window_id = self._get_window_id()
        self._set_fullscreen_state(old_window_id)
        while self.KEEPCHECKING and not self.abortRequested():
            current_window_id = self._get_window_id()
            if current_window_id != old_window_id:
                self._set_fullscreen_state(current_window_id)
                old_window_id = current_window_id
            self.waitForAbort(1)
        self._set_fullscreen_state(0)
        self.LW.log(['ended checking of window ID since playback stopped'])

    def _get_window_id(self):
        id = xbmcgui.getCurrentWindowDialogId()
        if id == 9999:
            id = xbmcgui.getCurrentWindowId()
        return id

    def _set_fullscreen_state(self, window_id):
        self.LW.log(['got window id of %s' % str(window_id)])
        if window_id == 12005 or window_id == 12006:
            self.FULLSCREENSTATE = 'on'
        else:
            self.FULLSCREENSTATE = 'off'
        if self.OLDFULLSCREENSTATE != self.FULLSCREENSTATE:
            payload = {'state': self.FULLSCREENSTATE}
            status, loglines, results = self.JSONURL.Post(
                self.RESTURL, data=json.dumps(payload))
            self.LW.log(loglines)
            self.OLDFULLSCREENSTATE = self.FULLSCREENSTATE
