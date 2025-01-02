# ui_module.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yaml
import os

class ConfigUI(tk.Tk):
    """
    A graphical user interface for configuring the book generation script.
    Allows users to modify parameters in the config.yaml file and edit prompt templates.
    """
    def __init__(self):
        super().__init__()
        self.title("Book Generator Configuration")
        self.geometry("800x600")

        # Intenta establecer un tema diferente
        try:
            self.tk.call("::ttk::style", "theme", "use", "clam") # Prueba con "clam"
        except tk.TclError:
            pass # Si "clam" no está disponible, continúa

        self.config_path = 'config.yaml'
        self.prompts_dir = '.'  # Assuming prompts are in the same directory, can be made configurable
        self.config_data = self._load_config()
        self.prompt_files = self._get_prompt_files()
        
        #Store the prompts
        self.prompt_contents = {}
        for file in self.prompt_files:
            self.prompt_contents[file] = self._load_prompt(os.path.join(self.prompts_dir, file))
        
        # --- Buttons at the bottom ---
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=10, padx=10, fill='x')

        ttk.Button(buttons_frame, text="Save Configuration", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Generate Book", command=self._run_script).pack(side=tk.RIGHT, padx=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        # --- Configuration Tab ---
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text='Configuration')
        self._create_config_widgets(self.config_tab)

        # --- Prompts Tab ---
        self.prompts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.prompts_tab, text='Prompts')
        self._create_prompts_widgets(self.prompts_tab)

        self._populate_from_config()

    def _load_config(self):
        """Loads configuration from config.yaml."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Configuration file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            messagebox.showerror("Error", f"Error parsing configuration file: {e}")
            return {}

    def _save_config(self):
        """Saves the current configuration to config.yaml."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving configuration: {e}")

    def _get_prompt_files(self):
        """Lists all .txt files in the prompts directory."""
        return [f for f in os.listdir(self.prompts_dir) if f.endswith('.txt')]

    def _load_prompt(self, filepath):
        """Loads the content of a prompt file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading prompt file: {e}")
            return ""

    def _save_prompt(self, filepath, content):
        """Saves the content to a prompt file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Prompt saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving prompt file: {e}")

    def _create_widgets(self):
        """Creates and arranges the UI elements."""
        
        # Notebook for tabs
        

        
    
    def _create_config_widgets(self, parent_frame):
        """Creates widgets for the Configuration tab."""
        # --- General Settings ---
        settings_frame = ttk.LabelFrame(parent_frame, text="General Settings")
        settings_frame.pack(pady=10, padx=10, fill='x')

        ttk.Label(settings_frame, text="Book Title:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.book_title_entry = ttk.Entry(settings_frame, width=40)
        self.book_title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(settings_frame, text="Number of Chapters:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.num_chapters_spin = tk.Spinbox(settings_frame, from_=1, to=50)
        self.num_chapters_spin.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(settings_frame, text="Number of Subchapters:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.num_subchapters_spin = tk.Spinbox(settings_frame, from_=1, to=20)
        self.num_subchapters_spin.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # --- Model Settings ---
        model_frame = ttk.LabelFrame(parent_frame, text="Model Settings")
        model_frame.pack(pady=10, padx=10, fill='x')

        # Helper function to create model sub-widgets
        def create_model_section(parent, label_text, temp_var, top_p_var, tokens_var):
            sub_frame = ttk.LabelFrame(parent, text=label_text)
            sub_frame.pack(pady=5, padx=5, fill='x')
            ttk.Label(sub_frame, text="Temperature:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            ttk.Scale(sub_frame, from_=0.1, to=2.0, variable=temp_var, orient=tk.HORIZONTAL).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            ttk.Label(sub_frame, text="Top P:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            ttk.Scale(sub_frame, from_=0.05, to=1.0, variable=top_p_var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
            ttk.Label(sub_frame, text="Max Output Tokens:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            ttk.Spinbox(sub_frame, from_=500, to=8192, increment=100, textvariable=tokens_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
            return sub_frame

        # Model parameters variables
        self.model_temp = tk.DoubleVar()
        self.model_top_p = tk.DoubleVar()
        self.model_tokens = tk.IntVar()
        create_model_section(model_frame, "Main Model", self.model_temp, self.model_top_p, self.model_tokens)

        self.review_model_temp = tk.DoubleVar()
        self.review_model_top_p = tk.DoubleVar()
        self.review_model_tokens = tk.IntVar()
        create_model_section(model_frame, "Review Model", self.review_model_temp, self.review_model_top_p, self.review_model_tokens)

        # --- Character Names ---
        char_frame = ttk.LabelFrame(parent_frame, text="Character Names")
        char_frame.pack(pady=10, padx=10, fill='both', expand=True)
        self.char_list = tk.Listbox(char_frame, height=8) # Reduced height
        self.char_list.pack(pady=5, padx=5, fill='both', expand=True)

        # --- World Elements ---
        world_frame = ttk.LabelFrame(parent_frame, text="World Elements")
        world_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        world_scroll = ttk.Frame(world_frame)
        world_scroll.pack(fill='both', expand=True)
        
        world_scrollbar = ttk.Scrollbar(world_scroll)
        world_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.world_text = tk.Text(world_scroll, height=10, wrap='word', yscrollcommand=world_scrollbar.set)
        self.world_text.pack(pady=5, padx=5, fill='both', expand=True)
        
        world_scrollbar.config(command=self.world_text.yview)

    def _create_prompts_widgets(self, parent_frame):
        """Creates widgets for the Prompts tab."""
        # --- Prompt Files List ---
        prompts_list_frame = ttk.Frame(parent_frame)
        prompts_list_frame.pack(side=tk.LEFT, padx=10, pady=10, fill='y')
        ttk.Label(prompts_list_frame, text="Prompt Files:").pack(anchor='w')
        self.prompts_listbox = tk.Listbox(prompts_list_frame, width=40, height=20)
        self.prompts_listbox.pack(fill='y', expand=True)
        for file in self.prompt_files:
            self.prompts_listbox.insert(tk.END, file)
        self.prompts_listbox.bind('<<ListboxSelect>>', self._load_selected_prompt)

        # --- Prompt Editor ---
        prompts_editor_frame = ttk.Frame(parent_frame)
        prompts_editor_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill='both', expand=True)

        
        prompt_scroll = ttk.Frame(prompts_editor_frame)
        prompt_scroll.pack(fill='both', expand=True)
        
        prompt_scrollbar = ttk.Scrollbar(prompt_scroll)
        prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Label(prompt_scroll, text="Prompt Editor:").pack(anchor='w')
        self.prompt_editor = tk.Text(prompt_scroll, wrap='word', yscrollcommand=prompt_scrollbar.set)
        self.prompt_editor.pack(fill='both', expand=True)
        
        prompt_scrollbar.config(command=self.prompt_editor.yview)

        # --- Save Prompt Button ---
        save_prompt_button = ttk.Button(prompts_editor_frame, text="Save Prompt", command=self._save_current_prompt)
        save_prompt_button.pack(pady=5, anchor='w')

    def _populate_from_config(self):
        """Populates the UI widgets with values from the configuration."""
        self.book_title_entry.insert(0, self.config_data.get('book_title', ''))
        self.num_chapters_spin.delete(0, tk.END)
        self.num_chapters_spin.insert(0, self.config_data.get('num_chapters', 2))
        self.num_subchapters_spin.delete(0, tk.END)
        self.num_subchapters_spin.insert(0, self.config_data.get('num_subchapters', 4))

        # Model settings
        self.model_temp.set(self.config_data.get('model_temperature', 1.0))
        self.model_top_p.set(self.config_data.get('model_top_p', 0.85))
        self.model_tokens.set(self.config_data.get('model_max_output_tokens', 8192))

        # Review model settings
        review_config = self.config_data.get('review_model_parameters', {})  # Assuming 'review_model_parameters' exists
        self.review_model_temp.set(review_config.get('temperature', 0.7))
        self.review_model_top_p.set(review_config.get('top_p', 0.8))
        self.review_model_tokens.set(review_config.get('max_output_tokens', 2048))

        # Character names
        self.char_list.delete(0, tk.END)
        for name in self.config_data.get('character_names', []):
            self.char_list.insert(tk.END, name)

        # World elements
        self.world_text.delete(1.0, tk.END)
        self.world_text.insert(tk.END, self.config_data.get('world_elements', ''))

    def _collect_config_from_ui(self):
        """Collects the current values from the UI widgets and updates the config data, without modifying prompts."""
        self.config_data['book_title'] = self.book_title_entry.get()
        self.config_data['num_chapters'] = int(self.num_chapters_spin.get())
        self.config_data['num_subchapters'] = int(self.num_subchapters_spin.get())
        self.config_data['model_temperature'] = self.model_temp.get()
        self.config_data['model_top_p'] = self.model_top_p.get()
        self.config_data['model_max_output_tokens'] = self.model_tokens.get()

        # Update review model parameters
        self.config_data.setdefault('model_parameters', {})['review'] = {
            'temperature': self.review_model_temp.get(),
            'top_p': self.review_model_top_p.get(),
            'max_output_tokens': self.review_model_tokens.get()
        }

        self.config_data['character_names'] = list(self.char_list.get(0, tk.END))
        self.config_data['world_elements'] = self.world_text.get(1.0, tk.END).strip()

    def _load_selected_prompt(self, event):
        """Loads the selected prompt file into the editor, using the stored content."""
        selected_indices = self.prompts_listbox.curselection()
        if selected_indices:
            filename = self.prompts_listbox.get(selected_indices[0])
            self.prompt_editor.delete(1.0, tk.END)
            self.prompt_editor.insert(tk.END, self.prompt_contents[filename])

    def _save_current_prompt(self):
        """Saves the content of the prompt editor to the currently selected file."""
        selected_indices = self.prompts_listbox.curselection()
        if selected_indices:
            filename = self.prompts_listbox.get(selected_indices[0])
            filepath = os.path.join(self.prompts_dir, filename)
            content = self.prompt_editor.get(1.0, tk.END)
            self.prompt_contents[filename] = content  # update the stored content
            self._save_prompt(filepath, content) # save to file only here.
        else:
            messagebox.showwarning("Warning", "No prompt file selected.")

    def _run_script(self):
        """Saves the configuration (but not prompts) and runs the main script."""
        self._collect_config_from_ui()
        self._save_config()
        # Construct the command to run the main script
        script_name = "book_generatorv3.py"  # Replace with your main script's name
        command = f"python {script_name}"
        
        try:
            os.system(command)
            messagebox.showinfo("Info", f"Running script: {script_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Error running script: {e}")

if __name__ == "__main__":
    app = ConfigUI()
    app.mainloop()