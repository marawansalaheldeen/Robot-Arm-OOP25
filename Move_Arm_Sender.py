

# Move_Arm_Sender.py
from security import SecurityManager
from LoginInformation import LoginInformation
import tkinter as tk

def main():
    # Initialize security manager
    """SecurityManager handles encryption, decryption, and signing of data."""
    sm = SecurityManager()

    # Collect login info
    login_info = LoginInformation()

    # GUI for segment, arm length, and command
    root = tk.Tk()
    root.title("Arm Command Input")

    tk.Label(root, text="Enter the Number of segments:").pack()
    segment_entry = tk.Entry(root)
    segment_entry.pack()

    tk.Label(root, text="Enter Arm Length:").pack()
    arm_length_entry = tk.Entry(root)
    arm_length_entry.pack()

    tk.Label(root, text="Enter Command (Pick up, Drop off, Move):").pack()
    command_entry = tk.Entry(root)
    command_entry.pack()
# Collect user inputs in a empty dictionary 
    user_inputs = {}

    def submit():
        user_inputs['Arm_Seg'] = segment_entry.get()
        user_inputs['Arm_l'] = arm_length_entry.get()
        user_inputs['Command'] = command_entry.get().strip()
        root.destroy()

    tk.Button(root, text="Submit", command=submit).pack()
    root.mainloop()

    Arm_Seg = user_inputs.get('Arm_Seg', '')
    Arm_l = user_inputs.get('Arm_l', '')
    Command = user_inputs.get('Command', '')

    out_put_data = (
        f"User: {login_info}\n"
        f"Segment Number: {Arm_Seg}\n"
        f"Arm Length: {Arm_l}\n"
        f"You chose to: {Command}"
    )

    # Encrypt and sign
    """Encrypts the command data and signs it for authenticity."""
    encrypted = sm.encrypt(out_put_data) # all processing is done in security.py
    # Sign the encrypted data so not tampered with
    """Generates a digital signature for the encrypted data to ensure integrity."""
    signature = sm.sign(out_put_data)

    # Save to files
    """Saves the encrypted data and signature to files for secure transmission."""
    with open("encrypted_command.bin", "wb") as f:
        f.write(encrypted)
    with open("signature.bin", "wb") as f:
        f.write(signature)

    # Log the activity
    login_info.log_login(out_put_data)

    print("Data encrypted and signed. Files ready for secure transmission.")

if __name__ == "__main__":
    main()
