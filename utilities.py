import sys
import ctypes
from winreg import *
from subprocess import *

class utility:
    def __init__(self):
        pass
    
    def block_input(self, should_block):
        """Stop the mouse and keyboard"""
        
        try:
            #Requires administrator privileges
            ctypes.windll.user32.BlockInput(should_block)
        except Exception as e:
            print(e)
    
    def run_cmd_command(self, command):
        """Run a CMD command"""
        
        try:
            result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
            return result.stdout
        except Exception as e:
            print(e)
    
    def run_powershell_command(self, command):
        """Run a powershell command"""
        
        try:
            result = run(["powershell", "-Command", command], capture_output=True)
            return (result.stdout.decode(), result.returncode)      #Return the output, and the returncode (0, 1...)
        except Exception as e:
            print(e)
    
    def is_running_as_exe(self):
        """Are we running as .exe""" 
        return getattr(sys, "frozen", False)
    
    def create_reg_key(self, as_who, reg_path, reg_name, reg_value):
        """Create a register"""
        
        #as_who means CURRENT_USER, LOCAL_MACHINE... (Registry settings)
        try:        
            CreateKey(as_who, reg_path)
            registry_key = OpenKey(as_who, reg_path, 0, KEY_WRITE)                
            
            SetValueEx(registry_key, reg_name, 0, REG_SZ, reg_value)        
            CloseKey(registry_key)
        except Exception as e:
            print(e)
    
    def modify_register(self, as_who, reg_path, reg_name, reg_values):
        """Modify a register"""
        
        try:
            reg_key = OpenKey(as_who, reg_path, 0, KEY_ALL_ACCESS)
            if len(reg_values) == 1:
                SetValueEx(reg_key, reg_name, 0, REG_SZ, reg_values[0])
            else:
                SetValueEx(reg_key, reg_name, 0, REG_MULTI_SZ, reg_values)
            
            CloseKey(reg_key)
        except Exception as e:
            print(e)
    
    def delete_register(self, as_who, reg_path, reg_name):
        """Delete a register"""
        
        try:
            reg_key = OpenKey(as_who, reg_path, 0, KEY_ALL_ACCESS)
            
            DeleteValue(reg_key, reg_name)
            CloseKey(reg_key)
        except Exception as e:
            print(e)