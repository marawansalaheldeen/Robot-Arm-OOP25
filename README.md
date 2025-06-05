# Robotic Arm OOP25

A Python application simulating a 2D robotic arm with a claw, featuring interactive GUI controls, user authentication, and encrypted command execution.

## Features

- **User Authentication:** Register and log in with a username and password (passwords are hashed and salted).
- **Interactive GUI:** 
  - Move the robotic arm by mouse or by entering commands.
  - Toggle the claw (open/close) by clicking or using commands.
  - Set the number of arm segments at startup.
- **Command Encryption:** Commands (move, pickup, place) are encrypted and decrypted using symmetric encryption (`cryptography.fernet`).
- **Matplotlib Visualization:** Real-time drawing and manipulation of the robotic arm and claw.

## Requirements

- Python 3.7+
- `numpy`
- `matplotlib`
- `cryptography`

Install dependencies with:

```sh
pip install numpy matplotlib cryptography
```

## Usage

1. **Run the application:**

    ```sh
    python robotic_arm.py
    ```

2. **Login:**  
   Use the default demo user:  
   - Username: `aaa`
   - Password: `aaa`

3. **Set Segments:**  
   Enter the number of arm segments (default is 3).

4. **Control the Arm:**
   - **Mouse:** Move the mouse in the plot area to move the arm's end effector.
   - **Click:** Left-click to toggle the claw open/closed.
   - **Command Box:** Enter commands at the bottom:
     - `move X Y` — Move the arm to position (X, Y)
     - `pickup` — Close the claw
     - `place` — Open the claw

## Example Commands

- `move 100 0`
- `pickup`
- `place`

## Security Notes

- Passwords are hashed and salted, but user data is stored in-memory for demonstration.
- Command encryption uses symmetric keys generated per command instance.
- **Do not use `eval()` on untrusted data in production.**

`Created by Marwan Salah and Team-3`
