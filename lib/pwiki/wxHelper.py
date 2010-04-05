import os, os.path, traceback, sys, re

from wx.xrc import XRCCTRL, XRCID, XmlResource
import wx

from MiscEvent import KeyFunctionSink
import Configuration


def _unescapeWithRe(text):
    """
    Unescape things like \n or \f. Throws exception if unescaping fails
    """
    return re.sub(u"", text, u"", 1)


class wxIdPool:
    def __init__(self):
        self.poolmap={}

    def __getattr__(self, name):
        """Returns a new wx-Id for each new string <name>.
 
        If the same name is given twice, the same id is returned.
        
        If the name is in the XRC id-table its value there will be returned
        """
        try:
            return XRCID(name)
        except:
            try:
                return self.poolmap[name]
            except KeyError:
                id = wx.NewId()
                self.poolmap[name] = id
                return id


GUI_ID = wxIdPool()
GUI_ID.__doc__="All purpose standard Gui-Id-Pool"

 
class XrcControls:
    """
    Convenience wrapper for XRCCTRL
    """
    def __init__(self, basepanel):
        self.__basepanel = basepanel

    def __getattr__(self, name):
        return XRCCTRL(self.__basepanel, name)
        
    def __getitem__(self, name):
        return XRCCTRL(self.__basepanel, name)

    def _byId(self, wid):
        return self.__basepanel.FindWindowById(wid)



class WindowUpdateLocker(object):
    """
    Python translation of wxWindowUpdateLocker.
    Usage:
    with WindowUpdateLocker(window):
        do this, do that...
    thawn again
    """
    def __init__(self, window):
        self.window = window
    
    def __enter__(self):
        if self.window is not None:
            self.window.Freeze()
        
        return self.window
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.window is not None:
            self.window.Thaw()



class _TopLevelLockerClass(object):
    """
    Provides context in which all top level windows are locked
    Usage:
    with TopLevelLocker:
        do this, do that...
    
    """
    def __enter__(self):
        wx.EnableTopLevelWindows(False)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        wx.EnableTopLevelWindows(True)

# The one and only instance
TopLevelLocker = _TopLevelLockerClass()


class IdRecycler:
    """
    You can get ids from it, associate them with a value, later clear the
    associations and reuse ids
    """
    def __init__(self):
        self.unusedSet = set()
        self.assoc = {}
    
    def assocGetId(self, value):
        """
        Get a new or unused id and associate it with value. Returns the id.
        """
        if len(self.unusedSet) == 0:
            id = wx.NewId()
        else:
            id = self.unusedSet.pop()
        
        self.assoc[id] = value
        return id
    
    def assocGetIdAndReused(self, value):
        """
        Get a new or unused id and associate it with value.
        Returns tuple (id, reused) where reused is True iff id is not new.
        """
        if len(self.unusedSet) == 0:
            id = wx.NewId()
            reused = False
        else:
            id = self.unusedSet.pop()
            reused = True

        self.assoc[id] = value
        return (id, reused)


    def get(self, id, default=None):
        """
        Get value for an id as for a dict object.
        """
        return self.assoc.get(id, default)
        
    def __getitem__(self, id):
        """
        Get value for an id as for a dict object.
        """
        return self.assoc[id]

    def iteritems(self):
        return self.assoc.iteritems()

    def clearAssoc(self):
        """
        Clear the associations, but store all ids for later reuse.
        """
        self.unusedSet.update(self.assoc.iterkeys())
        self.assoc.clear()



def getTextFromClipboard():
    """
    Retrieve text or unicode text from clipboard
    """
    from StringOps import lineendToInternal, mbcsDec

    cb = wx.TheClipboard
    cb.Open()
    try:
        dataob = textToDataObject()
        if cb.GetData(dataob):
            if dataob.GetTextLength() > 0:
                return lineendToInternal(dataob.GetText())
            else:
                return u""
        return None

# DO NOT DELETE! Useful later for retrieving HTML URL source
#         dataob = wx.CustomDataObject(wx.CustomDataFormat("HTML Format"))
# 
#         print "--getTextFromClipboard5"
#         if cb.GetData(dataob):
#             print "--getTextFromClipboard6"
#             if dataob.GetSize() > 0:
#                 print "--getTextFromClipboard7", repr(dataob.GetData()[:800])
#                 return lineendToInternal(dataob.GetData())
#             else:
#                 return u""
#         return None
    finally:
        cb.Close()


def textToDataObject(text=None):
    """
    Create data object for an unicode string
    """
    from StringOps import lineendToOs, mbcsEnc, utf8Enc
    
    if text is None:
        text = u""
    
    text = lineendToOs(text)

    return wx.TextDataObject(text)


def getBitmapFromClipboard():
    """
    Retrieve bitmap from clipboard if available
    """
    cb = wx.TheClipboard
    cb.Open()
    try:
        dataob = wx.BitmapDataObject()

        if cb.GetData(dataob):
            result = dataob.GetBitmap()
            if result is not wx.NullBitmap:
                return result
            else:
                return None
        return None
    finally:
        cb.Close()


if Configuration.isWindows():
#     def getMetafileFromClipboard():
#         """
#         Retrieve metafile from clipboard if available
#         """
#         cb = wx.TheClipboard
#         cb.Open()
#         try:
#             dataob = wx.CustomDataObject(wx.DataFormat(wx.DF_METAFILE))
#             dataob.SetData("")
#     
#             if cb.GetData(dataob):
#                 result = dataob.GetData()
# #                 if result is not wx.NullBitmap:
#                 return result
# #                 else:
# #                     return None
#             return None
#         finally:
#             cb.Close()


    def getMetafileFromClipboard():
        """
        Retrieve metafile from clipboard if available
        """
        cb = wx.TheClipboard
        cb.Open()
        try:
            dataob = wx.MetafileDataObject()
    
            if cb.GetData(dataob):
                result = dataob.GetMetafile()
#                 if result is not wx.NullBitmap:
                return result
#                 else:
#                     return None
            return None
        finally:
            cb.Close()
else:
    def getMetafileFromClipboard():
        return None



# if Configuration.isLinux():   # TODO Mac?
#     
#     def copyTextToClipboard(text): 
#         dataob = textToDataObject(text)
#     
#         cb = wx.TheClipboard
#         
#         cb.Open()
#         try:
#             cb.SetData(dataob)
#         finally:
#             cb.Close()
#     
#         dataob = textToDataObject(text)
#         cb.UsePrimarySelection(True)
#         cb.Open()
#         try:
#             cb.SetData(dataob)
#         finally:
#             cb.Close()
#             cb.UsePrimarySelection(False)
# 
# else:


def copyTextToClipboard(text): 
    dataob = textToDataObject(text)

    cb = wx.TheClipboard
    
    cb.Open()
    try:
        cb.SetData(dataob)
    finally:
        cb.Close()




def getAccelPairFromKeyDown(evt):
    """
    evt -- wx KeyEvent received from a key down event
    return: tuple (modifier, keycode) suitable e.g. as AcceleratorEntry
            (without event handling function)
    """
    keyCode = evt.GetKeyCode()
    
    modif = wx.ACCEL_NORMAL

    if evt.ShiftDown():
        modif |= wx.ACCEL_SHIFT
    if evt.ControlDown():
        modif |= wx.ACCEL_CTRL
    if evt.AltDown():
        modif |= wx.ACCEL_ALT
    
    return (modif, keyCode)


def getAccelPairFromString(s):
    ae = wx.GetAccelFromString(s)
    if ae is None:
        return (None, None)

    return ae.GetFlags(), ae.GetKeyCode()


def setHotKeyByString(win, hotKeyId, keyString):
    # Search for Windows key
    winMatch = re.search(u"(?<![^\+\-])win[\+\-]", keyString, re.IGNORECASE)
    winKey = False
    if winMatch:
        winKey = True
        keyString = keyString[:winMatch.start(0)] + \
                keyString[winMatch.end(0):]

    accFlags, vkCode = getAccelPairFromString("\t" + keyString)

#     win.RegisterHotKey(hotKeyId, 0, 0)
    win.UnregisterHotKey(hotKeyId)
    if accFlags is not None:
        modFlags = 0
        if accFlags & wx.ACCEL_SHIFT:
            modFlags |= wx.MOD_SHIFT
        if accFlags & wx.ACCEL_CTRL:
            modFlags |= wx.MOD_CONTROL
        if accFlags & wx.ACCEL_ALT:
            modFlags |= wx.MOD_ALT
        if winKey:
            modFlags |= wx.MOD_WIN
            
#         print "setHotKeyByString7", hotKeyId
        return win.RegisterHotKey(hotKeyId, modFlags, vkCode)

    return False


def cloneFont(font):
    return wx.Font(font.GetPointSize(), font.GetFamily(), font.GetStyle(),
                font.GetWeight(), font.GetUnderlined(), font.GetFaceName(),
                font.GetDefaultEncoding())


def drawTextRight(dc, text, startX, startY, width):
    """
    Draw text on a device context right aligned.
    startX, startY -- Upper left corner of box in which to align
    width -- Width of the box in which text should be aligned
    """
    # Calc offset to right align text
    offsetX = width - dc.GetTextExtent(text)[0]
    if offsetX < 0:
        offsetX = 0
    
    dc.DrawText(text, startX + offsetX, startY)


def drawTextCenter(dc, text, startX, startY, width):
    """
    Draw text on a device context center aligned.
    startX, startY -- Upper left corner of box in which to align
    width -- Width of the box in which text should be aligned
    """
    # Calc offset to center align text
    offsetX = (width - dc.GetTextExtent(text)[0]) // 2
    if offsetX < 0:
        offsetX = 0
    
    dc.DrawText(text, startX + offsetX, startY)


def clearMenu(menu):
    """
    Remove all items from a menu.
    """
    for item in menu.GetMenuItems():
        menu.DestroyItem(item)


def appendToMenuByMenuDesc(menu, desc, keyBindings=None):
    """
    Appends the menu items described in unistring desc to
    menu.
    keyBindings -- a KeyBindingsCache object or None
     
    menu -- already created wx-menu where items should be appended
    desc consists of lines, each line represents an item. A line only
    containing '-' is a separator. Other lines consist of multiple
    parts separated by ';'. The first part is the display name of the
    item, it may be preceded by '*' for a radio item or '+' for a checkbox
    item.
    
    The second part is the command id as it can be retrieved by GUI_ID,
    third part (optional) is the long help text for status line.
    
    Fourth part (optional) is the shortcut, either written as e.g.
    "Ctrl-A" or preceded with '*' and followed by a key to lookup
    in the KeyBindings, e.g. "*ShowFolding". If keyBindings
    parameter is None, all shortcuts are ignored.
    """
    for line in desc.split(u"\n"):
        if line.strip() == u"":
            continue

        parts = [p.strip() for p in line.split(u";")]
        if len(parts) < 4:
            parts += [u""] * (4 - len(parts))

        if parts[0] == u"-":
            ic = menu.GetMenuItemCount()
            if ic > 0 and not menu.FindItemByPosition(ic - 1).IsSeparator():
                # Separator
                menu.AppendSeparator()
        else:
            # First check for radio or checkbox items
            kind = wx.ITEM_NORMAL
            title = _unescapeWithRe(parts[0])
            if title[0] == u"*":
                # Radio item
                title = title[1:]
                kind = wx.ITEM_RADIO
            elif title[0] == u"+":
                # Checkbox item
                title = title[1:]
                kind = wx.ITEM_CHECK

            # Check for shortcut
            if parts[3] != u"" and keyBindings is not None:
                if parts[3][0] == u"*":
                    parts[3] = getattr(keyBindings, parts[3][1:], u"")
                
                if parts[3] != u"":
                    title += u"\t" + parts[3]
                
            menuID = getattr(GUI_ID, parts[1], -1)
            if menuID == -1:
                continue
            parts[2] = _unescapeWithRe(parts[2])
            menu.Append(menuID, _(title), _(parts[2]), kind)




def runDialogModalFactory(clazz):
    def runModal(*args, **kwargs):
        dlg = clazz(*args, **kwargs)
        try:
            dlg.CenterOnParent(wx.BOTH)
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetValue()
            else:
                return None
    
        finally:
            dlg.Destroy()
    
    return runModal



def getWindowParentsUpTo(childWindow, stopWindow):
    result = [childWindow]
    currentWindow = childWindow

    while True:
        currentWindow = currentWindow.GetParent()
        if currentWindow is None:
            return None   # Error
        result.append(currentWindow)
        if currentWindow is stopWindow:
            return result


def getAllChildWindows(win):
    winSet = set()
    winSet.add(win)
    _getAllChildWindowsRecurs(win, winSet)
    
    return winSet


def _getAllChildWindowsRecurs(win, winSet):
    for c in win.GetChildren():
        winSet.add(c)
        _getAllChildWindowsRecurs(c, winSet)




class wxKeyFunctionSink(wx.EvtHandler, KeyFunctionSink):
    """
    A MiscEvent sink which dispatches events further to other functions.
    If the wxWindow ifdestroyed receives a destroy message, the sink
    automatically disconnects from evtSource.
    """
    __slots__ = ("eventSource", "ifdestroyed", "disabledSource")


    def __init__(self, activationTable, eventSource=None, ifdestroyed=None):
        wx.EvtHandler.__init__(self)
        KeyFunctionSink.__init__(self, activationTable)

        self.eventSource = eventSource
        self.ifdestroyed = ifdestroyed
        self.disabledSource = None
        
        if self.eventSource is not None:
            self.eventSource.addListener(self, self.ifdestroyed is None)

        if self.ifdestroyed is not None:
            wx.EVT_WINDOW_DESTROY(self.ifdestroyed, self.OnDestroy)


    def OnDestroy(self, evt):
        # Event may be sent for child windows. Ignore them
        if not self.ifdestroyed is evt.GetEventObject():
            evt.Skip()
            return

        self.disconnect()
        evt.Skip()


    def enable(self, val=True):
        if val:
            if self.eventSource is not None or self.disabledSource is None:
                return

            self.eventSource = self.disabledSource
            self.disabledSource = None
            self.eventSource.addListener(self)
        else:
            if self.eventSource is None or self.disabledSource is not None:
                return
            
            self.disabledSource = self.eventSource
            self.eventSource.removeListener(self)
            self.eventSource = None

    def disable(self):
        return self.enable(False)


    def setEventSource(self, eventSource):
        if self.eventSource is eventSource:
            return

        self.disconnect()
        self.eventSource = eventSource
        self.disabledSource = None
        if self.eventSource is not None:
            self.eventSource.addListener(self)

    def disconnect(self):
        """
        Disconnect from eventSource.
        """
        self.disabledSource = None
        if self.eventSource is None:
            return
        self.eventSource.removeListener(self)
        self.eventSource = None

    def __repr__(self):
        return "<wxHelper.wxKeyFunctionSink " + hex(id(self)) + " ifdstr: " + \
                repr(self.ifdestroyed) + ">"



class IconCache:
    def __init__(self, iconDir):
        self.iconDir = iconDir
#         self.lowResources = lowResources
        
        # default icon is page.gif
        icons = ['page.gif']
        # add the rest of the icons
        icons.extend([fn for fn in os.listdir(self.iconDir)
                if fn.endswith('.gif') and fn != 'page.gif'])

        self.iconFileList = icons
        self.fillIconCache()


    def fillIconCache(self):
        """
        Fills or refills the self.iconLookupCache (if createIconImageList is
        false, self.iconImageList must exist already)
        If createIconImageList is true, self.iconImageList is also
        built
        """

        # create the image icon list
        self.iconImageList = wx.ImageList(16, 16)
        self.iconLookupCache = {}

        for icon in self.iconFileList:
#             iconFile = os.path.join(self.wikiAppDir, "icons", icon)
            iconFile = os.path.join(self.iconDir, icon)
            bitmap = wx.Bitmap(iconFile, wx.BITMAP_TYPE_GIF)
            try:
                id = self.iconImageList.Add(bitmap, wx.NullBitmap)

#                 if self.lowResources:   # and not icon.startswith("tb_"):
#                     bitmap = None

                iconname = icon.replace('.gif', '')
                if id == -1:
                    id = self.iconLookupCache[iconname][0]

                self.iconLookupCache[iconname] = (id, iconFile, bitmap)
            except Exception, e:
                traceback.print_exc()
                sys.stderr.write("couldn't load icon %s\n" % iconFile)


#     # TODO !  Do not remove bitmaps which are in use
#     def clearIconBitmaps(self):
#         """
#         Remove all bitmaps stored in the cache, needed by
#         PersonalWiki.resourceSleep.
#         """
#         for k in self.iconLookupCache.keys():
#             self.iconLookupCache[k] = self.iconLookupCache[k][0:2] + (None,)


    def lookupIcon(self, iconname):
        """
        Returns the bitmap object for the given iconname.
        If the bitmap wasn't cached already, it is loaded and created.
        If icon is unknown, None is returned.
        """
        try:
            bitmap = self.iconLookupCache[iconname][2]
            if bitmap is not None:
                return bitmap
                
            # Bitmap not yet available -> create it and store in the cache
            iconFile = os.path.join(self.iconDir, iconname+".gif")
            bitmap = wx.Bitmap(iconFile, wx.BITMAP_TYPE_GIF)
            
            self.iconLookupCache[iconname] = self.iconLookupCache[k][0:2] + \
                    (bitmap,)

            return bitmap

        except KeyError:
            return None


    def lookupIconIndex(self, iconname):
        """
        Returns the id number into self.iconImageList of the requested icon.
        If icon is unknown, -1 is returned.
        """
        try:
            return self.iconLookupCache[iconname][0]
        except KeyError:
            return -1


    def lookupIconPath(self, iconname):
        """
        Returns the path to icon file of the requested icon.
        If icon is unknown, -1 is returned.
        """
        try:
            return self.iconLookupCache[iconname][1]
        except KeyError:
            return None

    def resolveIconDescriptor(self, desc, default=None):
        """
        Used for plugins of type "MenuFunctions" or "ToolbarFunctions".
        Tries to find and return an appropriate wxBitmap object.
        
        An icon descriptor can be one of the following:
            - None
            - a wxBitmap object
            - the filename of a bitmap
            - a tuple of filenames, first existing file is used
        
        If no bitmap can be found, default is returned instead.
        """
        if desc is None:
            return default            
        elif isinstance(desc, wx.Bitmap):
            return desc
        elif isinstance(desc, basestring):
            result = self.lookupIcon(desc)
            if result is not None:
                return result
            
            return default
        else:    # A sequence of possible names
            for n in desc:
                result = self.lookupIcon(n)
                if result is not None:
                    return result

            return default
            
            
#     def getNewImageList(self):
#         """
#         Return a new (cloned) image list
#         """
#         return cloneImageList(self.iconImageList)
        
        
    def getImageList(self):
        """
        Return the internal image list. The returned object should be given
        wx components only with SetImageList, not AssignImageList
        """
        return self.iconImageList




class LayerSizer(wx.PySizer):
    def __init__(self):
        wx.PySizer.__init__(self)
        self.addedItemIds = set()

    def CalcMin(self):
        minw = 0
        minh = 0
        for item in self.GetChildren():
            mins = item.GetMinSize()
            minw = max(minw, mins.width)
            minh = max(minh, mins.height)

        return wx.Size(minw, minh)
        
    
    def Add(self, item):
        pId = id(item)
        if pId not in self.addedItemIds:
             self.addedItemIds.add(pId)
             wx.PySizer.Add(self, item)


    def RecalcSizes(self):
        pos = self.GetPosition()
        size = self.GetSize()
        size = wx.Size(size.GetWidth(), size.GetHeight())
        for item in self.GetChildren():
            win = item.GetWindow()
            if win is None:
                item.SetDimension(pos, size)
            else:
                # Bad hack
                # Needed because some ctrls like e.g. ListCtrl do not support
                # to overwrite virtual methods like DoSetSize
                win.SetDimensions(pos.x, pos.y, size.GetWidth(), size.GetHeight())



class DummyWindow(wx.Window):
    """
    Used to catch hotkeys because there seems to be a bug which prevents
    deleting them so instead the whole window is deleted and recreated.
    """
    def __init__(self, parent, id=-1):
        wx.Window.__init__(self, parent, id, size=(0,0))


# class ProxyPanel(wx.Panel):
class ProxyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        self.subWindow = None
        
        wx.EVT_SIZE(self, self.OnSize)

    def __repr__(self):
        return "<ProxyPanel " + str(id(self)) + " for " + repr(self.subWindow) + ">"


    def setSubWindow(self, subWindow):
        self.subWindow = subWindow

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(subWindow, 1, wx.EXPAND, 0)

        self.SetSizer(sizer)


    def getSubWindow(self):
        return self.subWindow


    def close(self):
        if self.subWindow is not None:
            self.subWindow.close()


    def OnSize(self, evt):
        evt.Skip()
        size = evt.GetSize()


class ProgressHandler(object):
    """
    Implementation of a GuiProgressListener to
    show a progress dialog
    """
    def __init__(self, title, msg, addsteps, parent, flags=wx.PD_APP_MODAL,
            yieldsteps=5):
        self.title = title
        self.msg = msg
        self.addsteps = addsteps
        self.parent = parent
        self.flags = flags
        self.progDlg = None
        self.yieldsteps = yieldsteps
        self.currYieldStep = 1

    def open(self, sum):
        """
        Start progress handler, set the number of steps, the operation will
        take in sum. Will be called once before update()
        is called several times
        """
        if self.progDlg is None:
            res = XmlResource.Get()
            self.progDlg = res.LoadDialog(self.parent, "ProgressDialog")
            self.progDlg.ctrls = XrcControls(self.progDlg)
            self.progDlg.SetTitle(self.title)

        self.currYieldStep = 1

        self.progDlg.ctrls.text.SetLabel(self.msg)
        self.progDlg.ctrls.gauge.SetRange(sum + self.addsteps)
        self.progDlg.ctrls.gauge.SetValue(0)
        self.progDlg.Show()

    def update(self, step, msg):
        """
        Called after a step is finished to trigger update
        of GUI.
        step -- Number of done steps
        msg -- Human readable description what is currently done
        returns: True to continue, False to stop operation
        """
        self.msg = msg

        self.progDlg.ctrls.text.SetLabel(msg)
        self.progDlg.ctrls.gauge.SetValue(step)
        
        self.currYieldStep -= 1
        if self.currYieldStep <= 0:
            self.currYieldStep = self.yieldsteps
            wx.SafeYield(onlyIfNeeded = True)

        return True

    def close(self):
        """
        Called after finishing operation or after abort to 
        do clean-up if necessary
        """
        self.progDlg.Destroy()
        self.progDlg = None



class EnhancedListControl(wx.ListCtrl):
    def __init__(*args, **kwargs):
        wx.ListCtrl.__init__(*args, **kwargs)

    def GetAllSelected(self):
        result = []
        sel = -1
        while True:
            sel = self.GetNextItem(sel, state=wx.LIST_STATE_SELECTED)
            if sel == -1:
                break
            result.append(sel)

        return result

    def GetFirstSelected(self):
        return self.GetNextItem(-1, state=wx.LIST_STATE_SELECTED)

    def GetIsSelected(self, idx):
        if idx < 0 or idx >= self.GetItemCount():
            return False

        return bool(self.GetItemState(idx, wx.LIST_STATE_SELECTED))


    if Configuration.isWindows():
        _SETSSI_ITEMMASK = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
    else:
        # TODO Check for MacOS
        _SETSSI_ITEMMASK = wx.LIST_STATE_SELECTED


    def SelectSingle(self, idx, scrollVisible=False):
        # Unselect all selected
        for prev in self.GetAllSelected():
            self.SetItemState(prev, 0, self._SETSSI_ITEMMASK)

        if idx > -1:
            self.SetItemState(idx, self._SETSSI_ITEMMASK, self._SETSSI_ITEMMASK)
            if scrollVisible:
                self.EnsureVisible(idx)

# class ColoredStatusBar(wx.StatusBar):
#     def __init__(self, *args, **kwargs):
#         wx.StatusBar.__init__(self, *args, **kwargs)
#         self.bgColors = [None]
#         self.Bind(wx.EVT_PAINT, self.OnPaint)
# 
#     def SetFieldsCount(self, number=1):
#         wx.StatusBar.SetFieldsCount(self, number)
#         self.bgColors = [None] * number
#         
#     def SetFieldBgColor(self, idx, color):
#         self.bgColors[idx] = color
#         
#     def OnPaint(self, evt):
# #         wx.StatusBar.Update(self)
#         dc = wx.WindowDC(self)
# 
#         for i, color in enumerate(self.bgColors):
#             if color is None:
#                 continue
# 
#             rect = self.GetFieldRect(i)
#             
#             
#             dc.SetBrush(wx.RED_BRUSH)
#             dc.SetPen(wx.RED_PEN)
#             dc.DrawRectangle(rect.x + 1, rect.y + 1, rect.width - 2,
#                     rect.height - 2)
#             dc.SetPen(wx.BLACK_PEN)
#             dc.SetFont(self.GetFont())
#             dc.SetClippingRect(rect)
#             dc.DrawText(self.GetStatusText(i), rect.x + 2, rect.y + 2)
#             dc.SetFont(wx.NullFont)
#             dc.SetBrush(wx.NullBrush)
#             dc.SetPen(wx.NullPen)
# 
#         evt.Skip()
        

