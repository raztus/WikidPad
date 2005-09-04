#!/bin/python

import sys, os, traceback, os.path

os.stat_float_times(True)

import pwiki.urllib_red as urllib

from wxPython.wx import *
import wxPython.xrc as xrc

from pwiki.PersonalWikiFrame import PersonalWikiFrame


openThisWiki = None
openThisWikiWord = None
if len(sys.argv) > 1:
   openThisWiki = sys.argv[1]
   if openThisWiki.startswith("wiki:"):
      openThisWiki = urllib.url2pathname(openThisWiki)
      openThisWiki = openThisWiki.replace("wiki:", "")

   if len(sys.argv) > 2:
      openThisWikiWord = sys.argv[2]

class App(wxApp):   
    def OnInit(self):
        appdir = os.path.dirname(os.path.abspath(sys.argv[0]))
        rf = open(os.path.join(appdir, "WikidPad.xrc"), "r")
        rd = rf.read()
        rf.close()
        
        res = xrc.wxXmlResource.Get()
        res.SetFlags(0)
        res.LoadFromString(rd)

        self.wikiFrame = PersonalWikiFrame(None, -1, "WikidPad", openThisWiki, openThisWikiWord)
        self.SetTopWindow(self.wikiFrame)

        # set the icon of the app
        try:
            self.wikiFrame.SetIcon(wxIcon(os.path.join('icons', 'pwiki.ico'), wxBITMAP_TYPE_ICO))
        except:
            pass

        return True

class ErrorFrame(wxFrame):
   def __init__(self, parent, id, title):
      wxFrame.__init__(self, parent, -1, title, size = (300, 200),
                       style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
      dlg_m = wxMessageDialog(self, "%s. %s." % ("Error starting wikidPad", e), 'Error!', wxOK)
      dlg_m.ShowModal()
      dlg_m.Destroy()
      self.Close()

class Error(wxApp):   
   def OnInit(self):
      errorFrame = ErrorFrame(None, -1, "Error")
      self.SetTopWindow(errorFrame)
      return False

app = None
exception = None

try:
   app = App(0)
   app.MainLoop()
except Exception, e:
   traceback.print_exc()
   exception = e
   error = Error(0)
   error.MainLoop()
   
sys.exit()