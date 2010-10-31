import sys, traceback, time, os, os.path

EL = None

# Maximum file size of log file before it is thrown away
FILE_CLEAR_LIMIT = 512 * 1024


# global exception control
class StdErrReplacement:
    def write(self, data):
        global EL
#         try:
#             import ExceptionLogger as EL
#         except ImportError:
#             # This should only happen while interpreter shuts down
#             return

        try:
            f = open(os.path.join(EL._exceptionDestDir, "WikidPad_Error.log"), "a")
            try:
                if not EL._timestampPrinted:
                    # Only write for first occurrence in session
                    f.write(EL._exceptionSessionTimeStamp)
                    EL._timestampPrinted = True
                EL._previousStdOut.write(data)
                f.write(data)
            finally:
                f.close()
        except:
            pass # TODO

    def writelines(self, it):
        for l in it:
            self.write(l)
            
# 

def onException(typ, value, trace):
    global EL
    
    try:
#         import ExceptionLogger as EL
##        traceback.print_exception(typ, value, trace, file=EL._previousStdOut)
        f = open(os.path.join(EL._exceptionDestDir, "WikidPad_Error.log"), "a")
        try:
            if not EL._timestampPrinted:
                # Only write for first exception in session
                f.write(EL._exceptionSessionTimeStamp)
                EL._timestampPrinted = True
            
            EL._exceptionOccurred = True
            EL.traceback.print_exception(typ, value, trace, file=f)
            EL.traceback.print_exception(typ, value, trace, file=EL._previousStdOut)
        finally:
            f.close()
    except:
        EL._previousStdOut.write("Exception occurred during global exception handling:\n")
        EL.traceback.print_exc(file=EL._previousStdOut)
        EL._previousStdOut.write("Original exception:\n")
        EL.traceback.print_exception(typ, value, trace, file=EL._previousStdOut)
        EL._previousExcepthook(typ, value, trace)


def setLogDestDir(path):
    global EL
    
    try:
        logPath = os.path.join(path, "WikidPad_Error.log")
        if os.path.exists(logPath) and os.stat(logPath).st_size > FILE_CLEAR_LIMIT:
            bakLogPath = os.path.join(path, "WikidPad_Error_bak.log")
            try:
                os.unlink(bakLogPath)
            except:
                pass
            
            try:
                os.rename(logPath, bakLogPath) 
            except:
                pass
    except:
        pass

    EL._exceptionDestDir = path


def getLogDestDir():
    global EL
    
    return os.path.join(EL._exceptionDestDir, "WikidPad_Error.log")



def startLogger(versionstring):
    global EL
    import ExceptionLogger as EL2
    
    EL = EL2
    
    EL._exceptionDestDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    EL._exceptionSessionTimeStamp = \
            time.strftime("\n\nVersion: '" + versionstring +
                    "' Session start: %Y-%m-%d %H:%M:%S\n")
    EL._exceptionOccurred = False
    EL._timestampPrinted = False
    
    
    EL._previousStdErr = sys.stderr
    sys.stderr = StdErrReplacement()

    EL._previousStdOut = sys.stdout
    sys.stdout = StdErrReplacement()

    EL._previousExcepthook = sys.excepthook
    sys.excepthook = onException
    