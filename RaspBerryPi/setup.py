# -*- coding: utf-8 -*-
import threading
import time
from threading import Thread
import wx
import wx.xrc
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
import  requests
import  glob
import os

###########################################################################
## class Worker
###########################################################################

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.on = True
        self.paused = False
        self.condition = threading.Condition(threading.Lock())

    def run(self):
        n = 0
        while self.on:
            with self.condition:
                while self.paused:
                    self.pause_cond.wait()
                n += 1
                listFiles = glob.glob("*.jpg")
                listFiles.extend(glob.glob("*.jpeg"))
                listFiles.extend(glob.glob("*.png"))
                lastFile = max(listFiles, key = os.path.getctime)
                print(lastFile)

                url = 'http://tatacoaastronomia.com/obtener-imagen.php'
                files = {'file': open(lastFile, 'rb')}
                r = requests.post(url, files = files)
                wx.CallAfter(pub.sendMessage, 'actualizar', value=n)
            time.sleep(2)

    def pause(self):
        # Al pausar cambiamos la varible de control y adquirimos el candado
        if not self.paused:
            self.paused = True
            self.condition.acquire()

    def resume(self):
        # Al reanudar liberamos el candado
        if self.paused:
            self.paused = False
            self.condition.notify()
            self.condition.release()

    def stop(self):
        r = requests.post("http://tatacoaastronomia.com/detener.php", data={'estado': 'detenido'})
        self.on = False


###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.static = wx.StaticText( self, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.static.Wrap( -1 )
        self.static.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BACKGROUND ) )
        self.static.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
        bSizer1.Add( self.static, 0, wx.ALL, 5 )

        self.ini = wx.Button( self, wx.ID_ANY, u"Iniciar Transmision", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.ini, 0, wx.ALL, 5 )

        self.det = wx.Button( self, wx.ID_ANY, u"Detener Transmision", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.det, 0, wx.ALL, 5 )

        self.rea = wx.Button( self, wx.ID_ANY, u"Reaunadar Transmision", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.rea, 0, wx.ALL, 5 )

        self.pau = wx.Button( self, wx.ID_ANY, u"Pausar Transmision", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.pau, 0, wx.ALL, 5 )

        self.SetSizer(bSizer1)
        self.Layout()

        self.Centre(wx.BOTH)


        self.ini.Bind( wx.EVT_BUTTON, self._start_thread )
        self.det.Bind( wx.EVT_BUTTON, self._stop_thread )
        self.pau.Bind( wx.EVT_BUTTON, self._pause_thread )
        self.rea.Bind( wx.EVT_BUTTON, self._resume_thread )

        self.det.Disable()
        self.pau.Disable()
        self.rea.Disable()

        pub.subscribe(self._update_label, "actualizar")
        self.Bind(wx.EVT_CLOSE, self._when_closed)

        self.hilo = None


    def _update_label(self, value):
        self.static.SetLabel("Transmitiendo... {} , imagenes   ".format(value))

    def _start_thread(self, event):
        self.ini.Disable()
        self.det.Enable()
        self.pau.Enable()
        self.rea.Disable()

        self.hilo = Worker()
        self.hilo.start()

    def _stop_thread(self, event):
        if self.hilo:
            self.hilo.stop()

            self.det.Disable()
            self.pau.Disable()
            self.rea.Disable()
            self.ini.Enable()

    def _pause_thread(self, event):
        if self.hilo:
            self.hilo.pause()

            self.pau.Disable()
            self.rea.Enable()

    def _resume_thread(self, event):
        if self.hilo:
            self.hilo.resume()

            self.pau.Enable()
            self.rea.Disable()

    def _when_closed(self, event):
        self._stop_thread(event)
        event.Skip()

    def __del__(self):
        pass



app = wx.App()
fr = MyFrame1(None)
fr.Show()
app.MainLoop()