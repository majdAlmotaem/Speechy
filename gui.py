import tkinter as tk
from tkinter import ttk
import threading
from modules.live_transcriber import LiveTranscriber
from modules.command_executor import execute_command
from config import MODEL_OPTIONS, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, WHISPER_MODEL

class VoiceControlGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Control Assistant")
        self.transcriber = None
        self.selected_language = tk.StringVar(value=DEFAULT_LANGUAGE)
        
        # Dark mode colors
        self.bg_color = '#1E1E1E'
        self.text_color = '#FFFFFF'
        self.button_bg = '#2C2C2C'
        
        master.configure(bg=self.bg_color)
        master.rowconfigure(0, weight=0)  # Status label
        master.rowconfigure(1, weight=0)  # Button frame
        master.rowconfigure(2, weight=0)  # Settings frame
        master.rowconfigure(3, weight=1)  # Output text
        master.columnconfigure(0, weight=1)

        # Status label
        self.status_label = tk.Label(
            master, 
            text="Voice Control Ready", 
            font=("Arial", 12, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.status_label.grid(row=0, column=0, pady=10)

        # Control buttons
        button_frame = tk.Frame(master, bg=self.bg_color)
        button_frame.grid(row=1, column=0, pady=5)

        self.start_button = tk.Button(
            button_frame, 
            text="▶", 
            font=("Arial", 12, "bold"),
            fg='#00FF00',
            bg=self.button_bg,
            command=self.start_voice_control,
            width=3,
            height=1,
            activebackground='#3C3C3C',
            activeforeground='#00CC00'
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(
            button_frame, 
            text="◼", 
            font=("Arial", 12, "bold"),
            fg='#FF0000',
            bg=self.button_bg,
            command=self.stop_voice_control,
            state=tk.DISABLED,
            width=3,
            height=1,
            activebackground='#3C3C3C',
            activeforeground='#CC0000'
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Settings frame (language and model selection)
        settings_frame = tk.Frame(master, bg=self.bg_color)
        settings_frame.grid(row=2, column=0, pady=5, padx=10, sticky="ew")
        
        # Configure style for dropdowns
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox', 
                        fieldbackground=self.button_bg,
                        background=self.button_bg,
                        foreground='black',
                        arrowcolor=self.text_color)
        style.map('TCombobox', 
                selectbackground=[('readonly', self.button_bg)],
                selectforeground=[('readonly', 'black')])
        
        # Language selection
        lang_label = tk.Label(
            settings_frame,
            text="Language:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        lang_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.lang_dropdown = ttk.Combobox(
            settings_frame,
            values=list(SUPPORTED_LANGUAGES.values()),
            textvariable=self.selected_language,
            state="readonly",
            width=10,
            style='TCombobox'
        )
        self.lang_dropdown.set(SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
        self.lang_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.lang_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        # Model selection
        model_label = tk.Label(
            settings_frame,
            text="Model:",
            font=("Arial", 10),
            fg=self.text_color,
            bg=self.bg_color
        )
        model_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.model_names = [info.get("name", key) for key, info in MODEL_OPTIONS.items()]
        self.selected_model = tk.StringVar(value=MODEL_OPTIONS[WHISPER_MODEL].get("name", WHISPER_MODEL))

        self.model_dropdown = ttk.Combobox(
            settings_frame,
            values=self.model_names,
            textvariable=self.selected_model,
            state="readonly",
            width=10,
            style='TCombobox'
        )
        self.model_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Output text area
        self.output_text = tk.Text(
            master, 
            bg='#2C2C2C',
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground='#4C4C4C',
            selectforeground=self.text_color
        )
        self.output_text.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")


        self.voice_thread = None
        self.is_running = False

    def on_language_change(self, event):
        selected_name = self.lang_dropdown.get()
        # Get language code from name
        lang_code = next((code for code, name in SUPPORTED_LANGUAGES.items() 
                         if name == selected_name), DEFAULT_LANGUAGE)
        
        self.update_output(f"Language changed to {selected_name} ({lang_code})")
        
        # Update transcriber language if it's running
        if self.transcriber and hasattr(self.transcriber, 'set_language'):
            self.transcriber.set_language(lang_code)

    def start_voice_control(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="Listening…", fg='#00FF00')
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
            if self.transcriber and hasattr(self.transcriber, 'stop'):
                self.transcriber.stop()
            self.transcriber = None

    def run_voice_control(self):
        try:
            # Get the language code from the selected language name
            selected_lang_name = self.lang_dropdown.get()
            lang_code = next((code for code, name in SUPPORTED_LANGUAGES.items() 
                             if name == selected_lang_name), DEFAULT_LANGUAGE)
            
            # Get the model name from the selected model
            selected_model_name = self.model_dropdown.get()
            model_code = next((key for key, info in MODEL_OPTIONS.items() 
                              if info.get("name", key) == selected_model_name), WHISPER_MODEL)
            
            self.update_output(f"Starting with model: {selected_model_name}, language: {selected_lang_name}")
            
            self.transcriber = LiveTranscriber(model_size=model_code, language=lang_code)
            
            def process_command(text):
                self.status_label.config(text="Processing…", fg='#FFFF00')
                self.update_output(f"{text}")
                success = execute_command(text)
                self.status_label.config(
                    text="Command Executed" if success else "Listening…",
                    fg='#00FF00'
                )
                if not success:
                    self.stop_voice_control()
                    
            self.transcriber.live_transcribe(callback=process_command)
        except Exception as e:
            self.update_output(f"Error: {str(e)}")
            self.status_label.config(text="Error Occurred", fg='#FF0000')
        finally:
            if self.is_running:
                self.stop_voice_control()

    def update_output(self, message):
        self.master.after(0, self._update_output_safe, message)

    def _update_output_safe(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

def run_gui():
    root = tk.Tk()
    gui = VoiceControlGUI(root)
    root.geometry('320x600+0+0')
    
    try:
        logo_img = tk.PhotoImage(file='logo.png')
        root.iconphoto(True, logo_img)
    except Exception:
        pass  # Ignore if logo file is missing
    
    root.minsize(300, 200)
    root.attributes('-topmost', True)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
