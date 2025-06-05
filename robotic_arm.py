import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import hashlib
import secrets
from cryptography.fernet import Fernet
import logging
from datetime import datetime


# Configure the logger to output messages to a log file with timestamp, level, and message.
logging.basicConfig(
    filename='robotic_arm_app.log',
    level=logging.INFO,  ## Log all INFO level and above messages
    format='%(asctime)s - %(levelname)s - %(message)s '
)

logger = logging.getLogger(__name__)  # # Create a logger instance for this module


class User:
    def __init__(self, username, password, public_key=None, private_key=None):
        self._username = username
        self._password_hash = self._hash_password(password)
        self._public_key = public_key
        self._private_key = private_key

    @property
    def username(self):
        return self._username

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def _hash_password(self, password):
        salt = secrets.token_hex(16)
        hash_ = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}${hash_}"

    def verify_password(self, password):
        salt, hash_ = self._password_hash.split('$')
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_
    

    @classmethod
    def register(cls, username, password):
        # In a real app, generate/store public/private keys here
        return cls(username, password, public_key="public_key_stub", private_key="private_key_stub")

    @staticmethod
    def login(user, password):
        return user.verify_password(password)

# Example user storage (in-memory for demo)
user_db = {}

def register_user(username, password):
    if username in user_db:
        # Log warning if registration fails due to existing username
        logger.warning(f"Registration failed: username '{username}' already exists.")
        print("Username already exists.")
        return None
    user = User.register(username, password)
    user_db[username] = user
    # Log success message when a new user is registered
    logger.info(f"User '{username}' registered successfully.")
    print("Registration successful.")
    return user

def login_gui():
    """GUI-based login function to authenticate the user with password masked as '*'."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis('off')
    plt.subplots_adjust(left=0.7, right=0.8, top=0.8, bottom=0.2)

    username_box = TextBox(plt.axes([0.3, 0.6, 0.4, 0.1]), 'Username:')
    password_box = TextBox(plt.axes([0.3, 0.4, 0.4, 0.1]), 'Password:')

    # Store the real password separately
    real_password = {'value': ''}

    # Overwrite the password box on every keystroke to show '*' only
    def on_password_submit(text):
        # This function is called when the user presses Enter in the password box
        pass  # Do nothing here

    def on_password_change(text):
        # Only update the real password if the change is a single character addition or deletion
        prev = real_password['value']
        if len(text) < len(prev):
            # Deletion
            real_password['value'] = prev[:len(text)]
        elif len(text) > len(prev):
            # Addition
            addition = text.replace('*', '')
            if addition:
                real_password['value'] += addition[-1]
        # Always mask the box
        password_box.set_val('*' * len(real_password['value']))

    password_box.on_submit(on_password_submit)
    password_box.on_text_change(on_password_change)

    login_status = {'authenticated': False}

    def submit(event):
        username = username_box.text
        password = real_password['value']
        user = user_db.get(username)
        if user and User.login(user, password):
            # Log successful login with username and timestamp
            logger.info(f"SUCCESS: User '{username}' logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Login successful!")
            login_status['authenticated'] = True
            plt.close(fig)
        else:
            # Log failed login attempt with attempted username and timestamp
            logger.warning(f"FAILED login attempt for username '{username}' at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("Invalid credentials. Try again.")
            username_box.set_val("")
            real_password['value'] = ""
            password_box.set_val("")

    submit_button = plt.axes([0.4, 0.2, 0.2, 0.1])
    button = plt.Button(submit_button, 'Login')
    button.on_clicked(submit)

    plt.show()
    return login_status['authenticated']

# Register a default user for demonstration
register_user("aaa", "aaa")

class RoboticArm:
    def __init__(self, num_segments=3, segment_length=50):
        self.num_segments = num_segments
        self.segment_length = segment_length
        self.tolerance = 1e-2
        self.joints = [np.array([i * segment_length, 0.0]) for i in range(num_segments + 1)]
        self.clamped = False  # Track claw state: False = open, True = clamped

    def solve_ik(self, target):
        joints = self.joints.copy()
        dist = np.linalg.norm(joints[0] - target)
        total_length = self.segment_length * self.num_segments

        if dist > total_length:
            for i in range(1, len(joints)):
                r = np.linalg.norm(target - joints[i - 1])
                lambda_ = self.segment_length / r
                joints[i] = (1 - lambda_) * joints[i - 1] + lambda_ * target
        else:
            base = joints[0]
            diff = np.linalg.norm(joints[-1] - target)
            while diff > self.tolerance:
                joints[-1] = target
                for i in reversed(range(self.num_segments)):
                    r = np.linalg.norm(joints[i + 1] - joints[i])
                    lambda_ = self.segment_length / r
                    joints[i] = (1 - lambda_) * joints[i + 1] + lambda_ * joints[i]
                joints[0] = base
                for i in range(self.num_segments):
                    r = np.linalg.norm(joints[i + 1] - joints[i])
                    lambda_ = self.segment_length / r
                    joints[i + 1] = (1 - lambda_) * joints[i] + lambda_ * joints[i + 1]
                diff = np.linalg.norm(joints[-1] - target)

        self.joints = joints

    def toggle_claw(self):
        self.clamped = not self.clamped

    def draw(self, ax):
        ax.clear()
        ax.set_xlim(-300, 300)
        ax.set_ylim(-300, 300)
        ax.set_aspect('equal')

        # Draw the arm
        xs = [joint[0] for joint in self.joints]
        ys = [joint[1] for joint in self.joints]
        ax.plot(xs, ys, 'o-', linewidth=4, markersize=8, color='blue')

        # Draw the claw at the end effector
        self.draw_claw(ax)

        ax.set_title("2D Robotic Arm with Claw")
        plt.draw()

    def draw_claw(self, ax):
        end = self.joints[-1]
        prev = self.joints[-2]
        direction = end - prev
        length = np.linalg.norm(direction)
        if length == 0:
            return
        unit_dir = direction / length

        # Claw angles: narrower when clamped, wider when open
        if self.clamped:
            angle = np.deg2rad(10)  # Clamped claw angle
            claw_len = 30           # Shorter claw length when clamped
            second_segment_len = 15 # Short second segment
        else:
            angle = np.deg2rad(30)  # Open claw angle
            claw_len = 45           # Longer claw length when open
            second_segment_len = 30 # Longer second segment to form half rectangle

        # Rotation matrices for left and right claw arms
        rot_left = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle),  np.cos(angle)]
        ])
        rot_right = np.array([
            [np.cos(-angle), -np.sin(-angle)],
            [np.sin(-angle),  np.cos(-angle)]
        ])

        # First segment of claw arms
        claw_left_start = end
        claw_left_end = end + rot_left @ unit_dir * claw_len

        claw_right_start = end
        claw_right_end = end + rot_right @ unit_dir * claw_len

        # Calculate perpendicular direction for second segment (to form "L" shape)
        # Perpendicular vector to the claw arm segment (rotate by 90 degrees)
        def perp(v):
            return np.array([-v[1], v[0]])

        left_perp_dir = perp(claw_left_end - claw_left_start)
        left_perp_dir /= np.linalg.norm(left_perp_dir)
        right_perp_dir = perp(claw_right_end - claw_right_start)
        right_perp_dir /= np.linalg.norm(right_perp_dir)
        # Second segment ends
        claw_left_second_end = claw_left_end + left_perp_dir * second_segment_len
        claw_right_second_end = claw_right_end + right_perp_dir * second_segment_len

        # Draw first segment of claws
        ax.plot([claw_left_start[0], claw_left_end[0]], [claw_left_start[1], claw_left_end[1]], color='red', linewidth=3)
        ax.plot([claw_right_start[0], claw_right_end[0]], [claw_right_start[1], claw_right_end[1]], color='red', linewidth=3)

        # Draw second segment of claws (forming half rectangle)
        ax.plot([claw_left_end[0], claw_left_second_end[0]], [claw_left_end[1], claw_left_second_end[1]], color='red', linewidth=3)
        ax.plot([claw_right_end[0], claw_right_second_end[0]], [claw_right_end[1], claw_right_second_end[1]], color='red', linewidth=3)


def on_mouse_move(event):
    if event.xdata is not None and event.ydata is not None:
        target = np.array([event.xdata, event.ydata])
        arm.solve_ik(target)
        arm.draw(ax)

def on_mouse_click(event):
    if event.button == 1:  # Left mouse button
        arm.toggle_claw()
        arm.draw(ax)


def segment_input_gui():
    """GUI to input the number of arm segments."""
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.axis('off')
    plt.subplots_adjust(left=0.3, right=0.7, top=0.8, bottom=0.2)

    segment_box = TextBox(plt.axes([0.3, 0.5, 0.4, 0.2]), 'Segments:', initial="3")
    input_status = {'value': None}

    def submit(text):
        try:
            val = int(segment_box.text)
            if val < 1:
                raise ValueError
            input_status['value'] = val
            plt.close(fig)
        except ValueError:
            segment_box.set_val("3")

    segment_box.on_submit(submit)

    plt.show()
    return input_status['value'] if input_status['value'] is not None else 3

class Command:
    def __init__(self, params, key=None):
        self.params = params
        self._key = key or Fernet.generate_key()
        self._fernet = Fernet(self._key)

    def encrypt(self):
        """Encrypt the command parameters."""
        data = str(self.params).encode()
        return self._fernet.encrypt(data)

    def decrypt(self, token):
        """Decrypt the command parameters."""
        decrypted = self._fernet.decrypt(token)
        return eval(decrypted.decode())  # Only safe if you trust the source

    @property
    def key(self):
        return self._key

class MoveCommand(Command):
    def __init__(self, x, y, key=None):
        params = {'action': 'move', 'x': x, 'y': y}
        super().__init__(params, key)

    def execute(self, robotic_arm):
        robotic_arm.solve_ik(np.array([self.params['x'], self.params['y']]))

class PickUpCommand(Command):
    def __init__(self, key=None):
        params = {'action': 'pickup'}
        super().__init__(params, key)

    def execute(self, robotic_arm):
        if not robotic_arm.clamped:
            robotic_arm.toggle_claw()

class PlaceCommand(Command):
    def __init__(self, key=None):
        params = {'action': 'place'}
        super().__init__(params, key)

    def execute(self, robotic_arm):
        if robotic_arm.clamped:
            robotic_arm.toggle_claw()

if __name__ == "__main__":
    if not login_gui():
        exit()

    num = segment_input_gui()

    arm = RoboticArm(num_segments=num, segment_length=50)

    fig, ax = plt.subplots()
    arm.draw(ax)

    # Add command entry TextBox to the main GUI
    command_box = TextBox(plt.axes([0.15, 0.01, 0.5, 0.05]), 'Command:', initial="move 100 0")
    status_box = TextBox(plt.axes([0.68, 0.01, 0.3, 0.05]), 'Status:', initial="", color='.95')
    status_box.set_active(False)

    def handle_command(text):
        parts = command_box.text.strip().split()
        # DEBUG log to track raw user command input before parsing
        logger.debug(f"Raw command input: '{text}' parsed into parts: {parts}")
        if not parts:
            # WARNING log if the user submits an empty command
            logger.warning("Empty command submitted.")
            status_box.set_val("No command entered.")
            return
        cmd = parts[0].lower()
        try:
            if cmd == "move" and len(parts) == 3:
                x, y = float(parts[1]), float(parts[2])
                # DEBUG log to trace MoveCommand creation with coordinates
                logger.debug(f"Creating MoveCommand with x={x}, y={y}")
                move_cmd = MoveCommand(x, y)
                encrypted = move_cmd.encrypt()
                params = move_cmd.decrypt(encrypted)
                MoveCommand(params['x'], params['y']).execute(arm)
                status_box.set_val(f"Moved to ({x}, {y})")
                logger.info(f"Executed MoveCommand to ({x}, {y})")
            elif cmd == "pickup":
                logger.debug("Creating PickUpCommand")
                pickup_cmd = PickUpCommand()
                encrypted = pickup_cmd.encrypt()
                params = pickup_cmd.decrypt(encrypted)
                PickUpCommand().execute(arm)
                status_box.set_val("Picked up (claw closed)")
                logger.info("Executed PickUpCommand (claw closed)")
            elif cmd == "place":
                logger.debug("Creating PlaceCommand")
                place_cmd = PlaceCommand()
                encrypted = place_cmd.encrypt()
                params = place_cmd.decrypt(encrypted)
                PlaceCommand().execute(arm)
                status_box.set_val("Placed (claw opened)")
                logger.info("Executed PlaceCommand (claw opened)")
            else:
                # WARNING log if user enters an unrecognized or malformed command
                logger.warning(f"Invalid command: {text}")
                status_box.set_val("Unknown command or wrong parameters.")
        except Exception as e:
            # ERROR log for any unexpected exception that occurs during command handling
            logger.error(f"Error handling command '{text}': {e}")
            status_box.set_val(f"Error: {e}")
        arm.draw(ax)

    command_box.on_submit(handle_command)

    cid_move = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
    cid_click = fig.canvas.mpl_connect('button_press_event', on_mouse_click)

    plt.show()

