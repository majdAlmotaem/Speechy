import tkinter as tk
import threading
from modules.live_transcriber import LiveTranscriber
from modules.command_executor import execute_command

class VoiceControlGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Control Assistant")
        master.geometry("400x300")
        self.transcriber = None
        
        # Dark mode colors
        self.bg_color = '#1E1E1E'  # Dark background
        self.text_color = '#FFFFFF'  # White text
        self.button_bg = '#2C2C2C'  # Slightly lighter dark background for buttons
        
        # Configure master window
        master.configure(bg=self.bg_color)
        
        # Konfigurieren Sie das Hauptfenster für Größenänderungen
        master.rowconfigure(0, weight=0)  # Status-Label-Zeile
        master.rowconfigure(1, weight=0)  # Button-Frame-Zeile
        master.rowconfigure(2, weight=1)  # Text-Output-Zeile
        master.columnconfigure(0, weight=1)

        # Status Label
        self.status_label = tk.Label(
            master, 
            text="Voice Control Ready", 
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.status_label.grid(row=0, column=0, pady=20)

        # Button Frame
        button_frame = tk.Frame(master, bg=self.bg_color)
        button_frame.grid(row=1, column=0, pady=10)

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

        # Text Output - Jetzt mit Grid und Skalierungsoptionen
        self.output_text = tk.Text(
            master, 
            bg='#2C2C2C',  # Dark background for text area
            fg=self.text_color,  # White text
            insertbackground=self.text_color,  # Cursor color
            selectbackground='#4C4C4C',  # Selection background
            selectforeground=self.text_color
        )
        self.output_text.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Thread for voice control
        self.voice_thread = None
        self.is_running = False

    def start_voice_control(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="Voice Control Running...", fg='#00FF00')
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.voice_thread = threading.Thread(target=self.run_voice_control, daemon=True)
            self.voice_thread.start()

    def stop_voice_control(self):
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="Voice Control Stopped", fg='#FF0000')
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.transcriber:
                self.transcriber.stop()
                self.transcriber = None  # Reset after stopping

    def run_voice_control(self):
        try:
            self.transcriber = LiveTranscriber()  # Create instance here
            def process_command(text):
                self.update_output(f"You said: {text}")
                execute_command(text)
            self.transcriber.live_transcribe(callback=process_command)
        except Exception as e:
            self.update_output(f"Error: {str(e)}")
        finally:
            self.stop_voice_control()

    def update_output(self, message):
        # Thread-safe method to update GUI
        self.master.after(0, self._update_output_safe, message)

    def _update_output_safe(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

def run_gui():
    root = tk.Tk()
    gui = VoiceControlGUI(root)
    root.geometry('320x600+0+0')
    logo_img = tk.PhotoImage(file='logo.png')
    root.iconphoto(True, logo_img)
    root.minsize(300, 200)  
    root.attributes('-topmost', True)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
