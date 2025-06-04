# Move_Arm_Receiver.py
from security import SecurityManager
from tkinter import messagebox, Tk
from receiver_gui import RoboticArmIK  # Make sure receiver_gui.py is in the same directory
from LoginInformation import LoginInformation

def main():
    sm = SecurityManager()

    # Read encrypted data and signature
    try:
        with open("encrypted_command.bin", "rb") as f:
            encrypted = f.read()
        with open("signature.bin", "rb") as f:
            signature = f.read()
    except FileNotFoundError:
        print("Missing encrypted_command.bin or signature.bin. Run sender.py first.")
        return

    # Decrypt and verify
    decrypted = sm.decrypt(encrypted)
    if sm.verify(decrypted, signature):
        print("Signature is valid. Data is authentic.")
        print("Decrypted data:", decrypted)

        # Extract info from decrypted string
        lines = decrypted.split("\n")
        username = lines[0].split(":")[1].strip()
        segment_count = lines[1].split(":")[1].strip()
        arm_length = lines[2].split(":")[1].strip()
        command = lines[3].split(":")[1].strip()

        # Launch GUI
        root = Tk()
        app = RoboticArmIK(root, segment_count, arm_length, command, username)
        root.mainloop()

    else:
        print("Signature is invalid! Data may have been tampered with.")

if __name__ == "__main__":
    main()
