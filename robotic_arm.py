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
        if not parts:
            status_box.set_val("No command entered.")
            return
        cmd = parts[0].lower()
        try:
            if cmd == "move" and len(parts) == 3:
                x, y = float(parts[1]), float(parts[2])
                move_cmd = MoveCommand(x, y)
                encrypted = move_cmd.encrypt()
                params = move_cmd.decrypt(encrypted)
                MoveCommand(params['x'], params['y']).execute(arm)
                status_box.set_val(f"Moved to ({x}, {y})")
            elif cmd == "pickup":
                pickup_cmd = PickUpCommand()
                encrypted = pickup_cmd.encrypt()
                params = pickup_cmd.decrypt(encrypted)
                PickUpCommand().execute(arm)
                status_box.set_val("Picked up (claw closed)")
            elif cmd == "place":
                place_cmd = PlaceCommand()
                encrypted = place_cmd.encrypt()
                params = place_cmd.decrypt(encrypted)
                PlaceCommand().execute(arm)
                status_box.set_val("Placed (claw opened)")
            else:
                status_box.set_val("Unknown command or wrong parameters.")
        except Exception as e:
            status_box.set_val(f"Error: {e}")
        arm.draw(ax)

    command_box.on_submit(handle_command)

    cid_move = fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
    cid_click = fig.canvas.mpl_connect('button_press_event', on_mouse_click)

    plt.show()

