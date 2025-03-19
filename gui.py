import tkinter as tk
import threading
import app  # Import the main application logic

class VoiceControlGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Control Assistant")
        master.geometry("400x300")
        
        # Dark mode colors
        self.bg_color = '#1E1E1E'  # Dark background
        self.text_color = '#FFFFFF'  # White text
        self.button_bg = '#2C2C2C'  # Slightly lighter dark background for buttons
        
        # Configure master window
        master.configure(bg=self.bg_color)

        # Status Label
        self.status_label = tk.Label(
            master, 
            text="Voice Control Ready", 
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.status_label.pack(pady=20)

        # Button Frame
        button_frame = tk.Frame(master, bg=self.bg_color)
        button_frame.pack(pady=10)

        # Play Button (Unicode play symbol ▶)
        self.start_button = tk.Button(
            button_frame, 
            text="▶", 
            font=("Arial", 12, "bold"),
            fg='#00FF00',  # Bright green for play
            bg=self.button_bg,
            command=self.start_voice_control,
            width=3,
            height=1,
            activebackground='#3C3C3C',
            activeforeground='#00CC00'
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop Button (Unicode stop symbol ◼)
        self.stop_button = tk.Button(
            button_frame, 
            text="◼", 
            font=("Arial", 12, "bold"),
            fg='#FF0000',  # Bright red for stop
            bg=self.button_bg,
            command=self.stop_voice_control,
            state=tk.DISABLED,
            width=3,
            height=1,
            activebackground='#3C3C3C',
            activeforeground='#CC0000'
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Text Output
        self.output_text = tk.Text(
            master, 
            height=10, 
            width=50,
            bg='#2C2C2C',  # Dark background for text area
            fg=self.text_color,  # White text
            insertbackground=self.text_color,  # Cursor color
            selectbackground='#4C4C4C',  # Selection background
            selectforeground=self.text_color
        )
        self.output_text.pack(pady=10)

        # Thread for voice control
        self.voice_thread = None
        self.is_running = False

    def start_voice_control(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="Voice Control Running...", fg='#00FF00')
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

            # Start voice control in a separate thread
            self.voice_thread = threading.Thread(
                target=self.run_voice_control, 
                daemon=True
            )
            self.voice_thread.start()

    def stop_voice_control(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="Voice Control Stopped", fg='#FF0000')
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def run_voice_control(self):
        try:
            # Modify app.main() to accept a callback for output
            app.main(output_callback=self.update_output)
        except Exception as e:
            self.update_output(f"Error: {str(e)}")

    def update_output(self, message):
        # Thread-safe method to update GUI
        self.master.after(0, self._update_output_safe, message)

    def _update_output_safe(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

def run_gui():
    root = tk.Tk()
    gui = VoiceControlGUI(root)
    
    # Position window at top-left corner
    root.geometry('400x300+0+0')
    
    # Make window always on top
    root.attributes('-topmost', True)
    
    root.mainloop()

if __name__ == "__main__":
    run_gui()
