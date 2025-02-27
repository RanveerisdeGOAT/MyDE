
__doc__ = '''
MYDE 2025
Author: @RanveeristheGOAT
Version: 1.0.0
Co-Authors: ChatGPT, Gemini, DeepSeek ;)
Free to use, modify, distribute and improve.
GitHub: https://github.com/RanveerisdeGOAT

This is a simple Python IDE (Integrated Development Environment)
with basic features like syntax highlighting, auto-completion, code folding.

'''


import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import os
import subprocess
import re
import threading
import builtins
import keyword
import ast
import importlib
import datetime
import webbrowser


__author__ = "@RanveeristheGOAT"
__version__ = "1.0.0"


class MyDE:
    def __init__(self, root: tk.Tk):
        """Initialize MyDE"""

        self.root = root
        self.root.title("MyDE")

        # Variables
        self.current_tab = None
        self.current_file_path = None
        self.searching = False
        self.last_key_pressed = None
        self.last_saved_content = None
        self.current_process = None

        # Directory Panel (Left Side)
        self.dir_frame = tk.Frame(root, width=200, bg="#e0e0e0")
        self.dir_frame.pack(side="left", fill="y")

        self.dir_label = tk.Label(self.dir_frame, text="Directory", bg="#e0e0e0", font=("Arial", 10, "bold"))
        self.dir_label.pack(pady=10)

        self.dir_listbox = tk.Listbox(self.dir_frame, bg="white", selectmode=tk.SINGLE)
        self.dir_listbox.pack(fill="both", expand=True)
        self.dir_listbox.bind("<Double-1>", self.open_file_from_dir)

        self.back_button = tk.Button(self.dir_frame, text="Back", command=self.go_back_directory)
        self.back_button.pack(pady=5)

        # Text Editor
        self.editor_frame = tk.Frame(root, width=200, bg="#e0e0e0")
        self.editor_frame.pack(side="top", fill="both", expand=True)

        self.file_editor_frame = tk.Frame(self.editor_frame, width=200, bg="#e0e0e0")
        self.file_editor_frame.pack(padx=0, pady=0)

        self.file_label = tk.Label(self.file_editor_frame, text="", font=("Arial", 10, "bold"), width=20)
        self.file_label.grid(row=0, column=0)

        self.text_editor = scrolledtext.ScrolledText(self.editor_frame, wrap='none', font=("Courier New", 12), undo=True, bg="white")

        self.status_label = tk.Label(self.editor_frame, text="", font=("Arial", 10, "bold"))
        self.status_label.pack()

        # Buttons Frame
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(side='left', fill="x", pady=5)

        self.run_button = tk.Button(self.button_frame, text="Run Code", command=self.run_code)
        self.run_button.pack(pady=5)

        self.kill_button = tk.Button(self.button_frame, text="Kill Process", command=self.kill_process)
        self.kill_button.pack(pady=5)

        self.search_button = tk.Button(self.button_frame, text="Search", command=self.search_in_editor)
        self.search_button.pack(pady=5)

        # Console Output
        self.console_output_frame = tk.Frame(root)
        self.console_output = tk.Text(self.console_output_frame, height=10, wrap="word", font=("Courier New", 10), bg="#f0f0f0")
        self.console_output.pack(fill="both", expand=True, padx=5, pady=5)
        self.console_output_frame.pack(side="top", fill="both", expand=True)

        # Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New File", command=self.create_new_file)
        file_menu.add_command(label="Open File", command=self.load_code)
        file_menu.add_command(label="Save File", command=self.save_code)
        file_menu.add_command(label="Delete File", command=self.delete_file, foreground='red')
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.text_editor.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_editor.edit_redo)
        edit_menu.add_command(label="Clear Console", command=self.clear_console)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # New Tab Menu
        new_menu = tk.Menu(self.menu_bar, tearoff=0)
        new_menu.add_command(label="New Window", command=self.open_new_window)
        new_menu.add_command(label="New Project", command=self.create_new_project)
        new_menu.add_command(label="New File", command=self.create_new_file)
        self.menu_bar.add_cascade(label="New", menu=new_menu)

        # Set up initial directory
        self.current_dir = os.path.abspath(".")
        self.update_directory_panel(self.current_dir)

        # Syntax highlighting tags
        self.setup_syntax_highlighting()

        # Suggestions Listbox
        self.suggestion_box = tk.Listbox(root, font=("Courier New", 10))
        self.suggestions = []  # List to hold suggestions
        self.suggestion_index = -1  # Track the index of the currently selected suggestion
        self.suggestion_box = tk.Listbox(self.root, width=30)

        # Highlight syntax variables
        self.variables = set()
        self.keywords = set(keyword.kwlist)
        self.builtins = set(dir(builtins))
        self.functions = set()
        self.classes = set()
        self.imports = set()
        self.class_methods = set()
        self.module_members = set()
        self.function_params = set()

        # Bind keyboard shortcuts
        self.text_editor.bind("<KeyRelease>", self.on_key_release)
        self.text_editor.bind("<Key>", self.on_key_press)  # Track key presses
        self.suggestion_box.bind("<Double-1>", self.insert_suggestion)
        self.suggestion_box.bind("<Return>", self.insert_suggestion)
        self.suggestion_box.bind("<Up>", self.navigate_suggestion(-1))
        self.suggestion_box.bind("<Down>", self.navigate_suggestion(1))
        self.suggestion_box.bind("<Double-1>", self.insert_suggestion)
        self.suggestion_box.bind("<FocusOut>", self.unfocus_suggestion)
        self.text_editor.bind("<Configure>", lambda event: self.highlight_syntax())
        self.text_editor.config(tabs=('1c',))

        self.text_editor.bind("<Control-f>", lambda event: self.search_in_editor())
        self.text_editor.bind("<Control-s>", lambda event: self.save_code())
        self.text_editor.bind("<Control-n>", lambda event: self.create_new_file())
        self.text_editor.bind("<Control-Alt-F1>", lambda event: self.delete_file())
        self.text_editor.bind("<Control-F6>", lambda event: self.run_code())
        self.console_output.bind("Control-C", lambda event: self.kill_process())

        # Line numbers
        self.line_numbers_text = LineNumbers(self.editor_frame, self.text_editor, bg="#e0e0e0")
        self.line_numbers_text.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers_text.config(yscrollcommand=self.text_editor.yview())


    def highlight_syntax_errors_python(self, event=None):
        """Highlight lines with syntax errors."""

        # Remove previous syntax error highlights
        self.text_editor.tag_remove("error", "1.0", tk.END)

        # Get the code from the text editor
        code = self.text_editor.get("1.0", tk.END)

        try:
            # Try parsing the code
            ast.parse(code)
        except SyntaxError as e:
            # Except syntax error
            line_num = e.lineno
            if e.args[1][2] != e.args[1][5]:
                start_index = f"{line_num}.{e.args[1][2]-1}"
                end_index = f"{line_num}.{e.args[1][5]}"
            else:
                start_index = f"{line_num}.0"
                end_index = f"{line_num}.end"
            self.text_editor.tag_add("error", start_index, end_index)
            self.status_label.config(text=e.args[0], fg='red')
        else:
            self.status_label.config(fg='black')

    def focus_suggestion(self, event):
        """focus the suggestion listbox."""

        if self.suggestion_box.winfo_ismapped():
            self.suggestion_box.focus_set()
            return 'break'

    def unfocus_suggestion(self, event):
        """unfocus the suggestion listbox."""

        self.suggestion_box.place_forget()
        return 'break'

    def on_key_release(self, event):
        """Handle key release events."""

        self.autosave_code(event)
        self.show_suggestions(event)
        self.auto_bracket(event)
        self.auto_tab(event)
        self.line_numbers_text.redraw()

    def on_key_press(self, event):
        """Track the last key pressed."""

        self.last_key_pressed = event.keysym  # Store the last key pressed

    def auto_bracket(self, event):
        """Automatically add closing bracket or quote."""
        # Check if the last key pressed was backspace
        if self.last_key_pressed == "BackSpace":
            return

        char = event.char
        if char in ['(', '{', '[', '"', "'"]:
            closing_bracket = {
                '(': ')',
                '{': '}',
                '[': ']',
                '"': '"',
                "'": "'"
            }[char]
            self.text_editor.insert("insert", closing_bracket)
            self.text_editor.mark_set("insert", "insert-1c")  # Move cursor back

        return "break"  # Prevent default behavior

    def show_suggestions(self, event=None):
        """Show suggestions, including parameters and module members."""
        try:
            # Parse code
            text_content = self.text_editor.get("1.0", tk.END)
            tree = ast.parse(text_content)

            self.variables = set()
            self.functions = set()
            self.classes = set()
            self.imports = set()
            self.class_methods = {}
            self.module_members = {}
            self.function_params = {}

            for node in ast.walk(tree):
                # Add each node's id to the respective set
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    self.variables.add(node.id)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef): # Handle both function types
                    self.functions.add(node.name)
                    params = [arg.arg for arg in node.args.args]
                    self.function_params[node.name] = set(params)
                elif isinstance(node, ast.ClassDef):
                    self.classes.add(node.name)
                    for method_node in ast.walk(node):
                        if isinstance(method_node, ast.FunctionDef):
                            if node.name not in self.class_methods:
                                self.class_methods[node.name] = set()
                            self.class_methods[node.name].add(method_node.name)
                            params = [arg.arg for arg in method_node.args.args]
                            self.function_params[f"{node.name}.{method_node.name}"] = set(params)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.add(alias.name)
                        try:
                            module = importlib.import_module(alias.name)
                            self.module_members[alias.name] = set(dir(module))
                        except ModuleNotFoundError:
                            pass
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    for alias in node.names:
                        self.imports.add(alias.name)
                        try:
                            module = importlib.import_module(module_name)
                            self.module_members[module_name] = set(dir(module))
                        except ModuleNotFoundError:
                            pass

        except SyntaxError:
            pass

        # Match the typed word with suggestions
        cursor_pos = self.text_editor.index("insert")
        line_start = self.text_editor.index(f"{cursor_pos} linestart")
        current_line = self.text_editor.get(line_start, cursor_pos)

        match = re.search(r'\b(\w+)$', current_line)
        if match:
            typed_word = match.group(1)

            all_suggestions = (
                list(self.variables)
                + list(self.functions)
                + list(self.classes)
                + list(self.imports)
                + list(keyword.kwlist)
                + list(dir(builtins))
            )

            if "." in current_line:
                class_name_match = re.search(r'(\w+)\.$', current_line)
                if class_name_match:
                    class_name = class_name_match.group(1)
                    if class_name in self.class_methods:
                        all_suggestions.extend(
                            [f"{class_name}.{method}" for method in self.class_methods[class_name]]
                        )
                    elif class_name in self.module_members:
                        all_suggestions.extend(
                            [f"{class_name}.{member}" for member in self.module_members[class_name]]
                        )

            if "(" in current_line:
                func_name_match = re.search(r'(\w+)\($', current_line)
                if func_name_match:
                    func_name = func_name_match.group(1)
                    if func_name in self.function_params:
                        all_suggestions.extend(list(self.function_params[func_name]))

            suggestions = sorted(list(set(sug for sug in all_suggestions if sug.startswith(typed_word)))) # Remove duplicates, sort alphabetically

            if suggestions:
                self.show_suggestion_box(suggestions, event)
            else:
                self.suggestion_box.place_forget()
        else:
            self.suggestion_box.place_forget()



    def show_suggestion_box(self, suggestions, event):
        """Display suggestions in the suggestion box."""
        self.suggestion_box.delete(0, tk.END)
        for suggestion in suggestions:
            self.suggestion_box.insert(tk.END, suggestion)

        # Position the suggestion box
        cursor_pos = self.text_editor.index("insert")
        x, y, _, _ = self.text_editor.bbox(cursor_pos)
        self.suggestion_box.place(x=x+182, y=y+82)

    def insert_suggestion(self, event):
        """Insert the selected suggestion into the text editor."""
        if self.suggestion_box.curselection():
            selected_suggestion = self.suggestion_box.get(self.suggestion_box.curselection())
            cursor_pos = self.text_editor.index("insert")
            line_start = self.text_editor.index(f"{cursor_pos} linestart")
            current_line = self.text_editor.get(line_start, cursor_pos)

            # Find the beginning of the current word
            match = re.search(r'\b(\w+)$', current_line)
            if match:
                start_index = f"{line_start} + {match.start()}c"
                end_index = cursor_pos
                self.text_editor.delete(start_index, end_index)

            # Insert the selected suggestion
            self.text_editor.insert(f'{line_start} + {match.start()}c', selected_suggestion)
            self.suggestion_box.place_forget()
            self.text_editor.focus_set()

    def navigate_suggestion(self, direction):
        """Navigate through the suggestion list."""

        def navigate(event):
            if self.suggestion_box.size() > 0:
                # Navigates through the suggestion list
                current_selection = self.suggestion_box.curselection()
                if direction == -1:  # Up
                    new_index = (current_selection[0] - 1) % self.suggestion_box.size() if current_selection else 0
                else:  # Down
                    new_index = (current_selection[0] + 1) % self.suggestion_box.size() if current_selection else 0

                self.suggestion_box.selection_clear(0, tk.END)
                self.suggestion_box.selection_set(new_index)
                self.suggestion_box.activate(new_index)
                self.suggestion_box.see(new_index)

        return navigate

    def delete_file(self):
        """Delete the current file."""
        if tk.messagebox.askyesno(f"Delete File", f"Are you sure you want to delete {self.current_file_path}?"):
            os.remove(self.current_file_path)
            self.update_directory_panel(os.path.dirname(self.current_file_path))
            self.current_file_path = None
            self.change_file()

    def change_file(self):
        """Change the current file."""
        if self.current_file_path is not None:
            self.file_label.config(text=os.path.basename(self.current_file_path))
            self.text_editor.pack(fill="both", expand=True, padx=0, pady=0, side='top')
            if self.current_file_path.endswith(".py"):
                self.run_button.config(state="normal")
            elif self.current_file_path.endswith(".html"):
                self.run_button.config(state="normal")
            else:
                self.run_button.config(state="disabled")
            self.dir_listbox.update()
        else:
            self.file_label.config(text='')
            self.text_editor.pack_forget()

    def autosave_code(self, e=None):
        """Automatically saves the file if there are unsaved changes."""
        # Check if there's an open file path to save to
        if hasattr(self, 'current_file_path') and self.current_file_path:
            current_content = self.text_editor.get("1.0", tk.END)

            # Check if content has changed since last save
            if not hasattr(self, 'last_saved_content') or self.last_saved_content != current_content:
                with open(self.current_file_path, "w") as f:
                    f.write(current_content)
                self.last_saved_content = current_content  # Update last saved content
            self.highlight_syntax()
            self.status_label.config(text=f"Last saved: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def setup_syntax_highlighting(self):
        """Setup syntax highlighting for different file types."""
        # Create tags for syntax highlighting
        self.text_editor.tag_configure("comment", foreground="#a0a0a0")
        self.text_editor.tag_configure("integer", foreground="blue")
        self.text_editor.tag_configure("builtin", foreground="purple")
        self.text_editor.tag_configure("keyword", foreground="orange")
        self.text_editor.tag_configure("string", foreground="green")
        self.text_editor.tag_configure('error', underline=True, foreground='red')
        self.text_editor.tag_configure("highlight", background="yellow")
        self.console_output.tag_configure("error", foreground="red")

    def update_directory_panel(self, path):
        """Update the directory panel with the contents of the selected directory."""
        self.dir_label.config(text=os.path.basename(path))
        self.dir_listbox.delete(0, tk.END)
        for item in os.listdir(path):
            self.dir_listbox.insert(tk.END, item)
        self.current_dir = path

    def highlight_syntax(self):
        """Highlight syntax in the text editor."""
        # Highlight files accordingly
        if self.current_file_path:
            if self.current_file_path.endswith(".py"):
                self.highlight_syntax_python()
                self.highlight_syntax_errors_python()
            elif self.current_file_path.endswith(".html"):
                self.highlight_syntax_html()
            elif self.current_file_path.endswith(".js"):
                self.highlight_syntax_js()
            elif self.current_file_path.endswith(".css"):
                self.highlight_syntax_css()
            elif self.current_file_path.endswith(".json"):
                self.highlight_syntax_json()
            elif self.current_file_path.endswith(".png"):
                self.open_image(self.current_file_path)

    def open_file_from_dir(self, event):
        """Open a file from the directory list."""
        selected_file = self.dir_listbox.get(self.dir_listbox.curselection())
        file_path = os.path.join(self.current_dir, selected_file)
        if os.path.isfile(file_path):
            self.load_file(file_path)
            self.highlight_syntax()
        else:
            self.update_directory_panel(file_path)

    def load_file(self, file_path):
        """Load a file into the text editor."""
        try:
            # Read the file content and insert it into the text editor
            with open(file_path, "r") as file:
                code = file.read()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, code)
            self.current_file_path = file_path
            self.change_file()
            self.status_label.config(text='File Loaded')
        except UnicodeDecodeError:
            if file_path.endswith('.png') | file_path.endswith('.jpeg') | file_path.endswith('.ico'):
                self.open_image(file_path)
            else:
                self.open_explorer(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{e}")

    def run_code(self):
        """Run code"""
        self.console_output.delete("1.0", tk.END)
        # Creates tread to execute the code without lag
        threading.Thread(target=self.execute_code, daemon=True).start()
        self.status_label.config(text="Running...")

    def execute_code(self):
        """Execute the code directly from the text content."""
        if self.current_file_path.endswith(".py"):
            # Run python executable
            executable = "python"
            args = [executable, self.current_file_path]
            self.current_process = subprocess.Popen(
                args,
                cwd=self.current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            def read_stdout():
                # read stdout
                for line in iter(self.current_process.stdout.readline, ''):
                    self.console_output.insert(tk.END, line)
                    self.console_output.see(tk.END)
            def read_stderr():
                # read stderr
                for line in iter(self.current_process.stderr.readline, ''):
                    self.console_output.insert(tk.END, line, "error")
                    self.console_output.see(tk.END)

            # Tread to read stdout and stderr concurrently to avoid blocking the GUI thread.:
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            stdout_thread.join()
            stderr_thread.join()

            self.status_label.config(text="Execution complete")

            self.current_process.stdout.close()
            self.current_process.stderr.close()
            self.current_process.wait()
            self.current_process = None
        elif self.current_file_path.endswith(".html"):
            # Run html file in a web browser
            webbrowser.open(self.current_file_path)

    def kill_process(self):
        """Kill the running process if it exists."""
        if self.current_process is not None:
            # Terminate process
            self.current_process.terminate()  # Gracefully terminate the process
            self.current_process = None  # Reset the process variable
            messagebox.showinfo("Process Terminated", "The running process has been terminated.")
            self.status_label.config(text='Process Terminated')
        else:
            messagebox.showwarning("No Process", "No process is currently running.")

    def save_code(self):
        """Save the current file."""
        code = self.text_editor.get("1.0", tk.END)
        if self.current_file_path:
            file_path = self.current_file_path
        else:
            file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(code)
                self.current_file_path = file_path
                self.change_file()
                self.status_label.config(text='Saved')
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def load_code(self):
        """Open a load file."""
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            self.load_file(file_path)

    def clear_console(self):
        """Clear the console output."""
        self.console_output.delete("1.0", tk.END)
        self.status_label.config(text='Cleared')

    def open_new_window(self):
        """Open a new window"""
        new_root = tk.Toplevel(self.root)
        MyDE(new_root)

    def create_new_project(self):
        """Create a new project."""
        project_name = simpledialog.askstring("New Project", "Enter the project name:")
        if not project_name:
            return

        project_location = filedialog.askdirectory(title="Select Project Location")
        if not project_location:
            return

        # create project, TODO: Make venv
        project_path = os.path.join(project_location, project_name)
        try:
            os.makedirs(project_path, exist_ok=True)
            messagebox.showinfo("Project Created", f"Project '{project_name}' created at {project_path}")
            self.update_directory_panel(project_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not create project directory:\n{e}")

    def create_new_file(self):
        """Create a new file."""
        file_name = simpledialog.askstring("New File", "Enter the file name:")
        if not file_name:
            return

        if not file_name.endswith('.py'):
            file_name += '.py'

        file_path = os.path.join(self.current_dir, file_name)
        try:
            with open(file_path, "x") as f:
                f.close()
            messagebox.showinfo("File Created", f"File '{file_name}' created at {file_path}")
            self.update_directory_panel(self.current_dir)
            self.current_file_path = file_path
            self.change_file()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create project file:\n{e}")

    def go_back_directory(self):
        """ Navigate to the parent directory. """
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:  # Check if we're at the root directory
            self.update_directory_panel(parent_dir)

    def search_in_editor(self):
        """ Search for a specific text in the editor. """
        if not self.searching:
            self.searching = True
            search_term = simpledialog.askstring("Search", "Enter the text to search:")
            if search_term:
                content = self.text_editor.get("1.0", tk.END)
                matches = re.finditer(search_term, content)
                if matches:
                    for match in matches:
                        start_index = f"1.0 + {match.start()} chars"
                        end_index = f"1.0 + {match.end()} chars"
                        self.text_editor.tag_add("found", start_index, end_index)
                        self.text_editor.tag_config("found", background="yellow")
                        self.text_editor.mark_set("insert", start_index)
                        self.text_editor.see(start_index)
                else:
                    messagebox.showinfo("Search", f"'{search_term}' not found.")
        else:
            self.searching = False
            self.text_editor.tag_remove('found', '1.0', tk.END)

    def toggle_theme(self):
        """ Toggle between light and dark theme. """
        # Not correctly implemented
        # TODO: Implement this feature
        current_bg = self.text_editor.cget("background")
        if current_bg == "white":
            # Change to dark theme
            self.text_editor.config(background="black", foreground="white")
            self.console_output.config(background="black", foreground="white")
            self.dir_frame.config(background="#2e2e2e")
            self.dir_label.config(background="#2e2e2e", foreground="white")
            self.back_button.config(background="#3e3e3e", foreground="white")
            self.menu_bar.config(bg="#2e2e2e", fg="white")
        else:
            # Change to light theme
            self.text_editor.config(background="white", foreground="black")
            self.console_output.config(background="#f0f0f0", foreground="black")
            self.dir_frame.config(background="#e0e0e0")
            self.dir_label.config(background="#e0e0e0", foreground="black")
            self.back_button.config(background="#d0d0d0", foreground="black")
            self.menu_bar.config(bg="#e0e0e0", fg="black")

    def highlight_syntax_python(self):
        """ Highlights syntax in the text editor for Python"""
        code = self.text_editor.get("1.0", tk.END)
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("integer", "1.0", tk.END)
        self.text_editor.tag_remove("builtins", "1.0", tk.END)
        self.text_editor.tag_remove("comments", "1.0", tk.END)
        string_builtin = 'self'
        for func in set(dir(builtins)):
            if func not in ['True', 'False', 'None']:
                string_builtin += '|' + str(func)
        string_keywords = 'def'
        for key in set(keyword.kwlist): string_keywords += '|' + str(key)

        # Define simple regex for keywords, strings, and variables
        keywords = fr'\b({string_keywords}|True|False|None)\b|,\\'
        strings = r'(\".*?\"|\'.*?\')'
        integer = r'-?\d+'
        comment = r'^#.*$'
        builtin = fr'\b({string_builtin})\b'

        # Highlight buitlin
        for match in re.finditer(builtin, code):
            self.text_editor.tag_add("builtin", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight keywords
        for match in re.finditer(keywords, code):
            self.text_editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight integers
        for match in re.finditer(integer, code, re.MULTILINE):
            self.text_editor.tag_add("integer", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight strings
        for match in re.finditer(strings, code):
            self.text_editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight comments
        for match in re.finditer(comment, code, re.MULTILINE):
            self.text_editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def highlight_syntax_json(self):
        """ Highlights syntax in the text editor for JSON"""
        code = self.text_editor.get("1.0", tk.END)
        # Clear existing tags
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("variable", "1.0", tk.END)
        string_builtin = 'self'
        for func in set(dir(builtins)):
            if func not in ['True', 'False', 'None']:
                string_builtin += '|' + str(func)
        string_keywords = 'def'
        for key in set(keyword.kwlist): string_keywords += '|' + str(key)

        # Define simple regex for keywords, strings, and variables
        keywords = r'{|}|\\[|\\]|\\,|:'
        strings = r'(\".*?\")'
        integer = r'-?\d+'
        builtin = fr'(: \".*?\")'

        # Highlight buitlin

        # Highlight keywords

        # Highlight integers
        for match in re.finditer(integer, code, re.MULTILINE):
            self.text_editor.tag_add("integer", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight strings
        for match in re.finditer(strings, code):
            self.text_editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight builtins
        for match in re.finditer(builtin, code):
            self.text_editor.tag_add("builtin", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(keywords, code):
            self.text_editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def highlight_syntax_html(self):
        """ Highlights syntax in the text editor for HTML"""
        code = self.text_editor.get("1.0", tk.END)
        # Clear existing tags
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("integer", "1.0", tk.END)
        self.text_editor.tag_remove("builtins", "1.0", tk.END)
        self.text_editor.tag_remove("comments", "1.0", tk.END)
        string_builtin = 'self'
        for func in set(dir(builtins)):
            if func not in ['True', 'False', 'None']:
                string_builtin += '|' + str(func)
        string_keywords = 'def'
        for key in set(keyword.kwlist): string_keywords += '|' + str(key)

        keywords = r'(<[^\/>]+>)|(<\/[^>]+>)|(<[^>]+/>)'
        strings = r"=\s*(\"([^\"]*)\"|'([^']*)'|([^\s>]+))"
        integer = r'-?\d+'
        comment = r'///*.*$'
        builtin = fr'\b([a-zA-Z_][a-zA-Z0-9_-]*)\s*='


        # Highlight comments
        for match in re.finditer(comment, code, re.MULTILINE):
            self.text_editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")


        # Highlight integers
        for match in re.finditer(integer, code, re.MULTILINE):
            self.text_editor.tag_add("integer", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight buitlin
        for match in re.finditer(builtin, code):
            self.text_editor.tag_add("builtin", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight keywords
        for match in re.finditer(keywords, code):
            self.text_editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight strings
        for match in re.finditer(strings, code):
            self.text_editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def highlight_syntax_js(self):
        """ Highlights syntax in the text editor for JavaScript"""
        code = self.text_editor.get("1.0", tk.END)
        # Clear existing tags
        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("integer", "1.0", tk.END)
        self.text_editor.tag_remove("builtins", "1.0", tk.END)
        self.text_editor.tag_remove("comments", "1.0", tk.END)
        string_builtin = 'self'
        for func in set(dir(builtins)):
            if func not in ['True', 'False', 'None']:
                string_builtin += '|' + str(func)
        string_keywords = 'def'
        for key in set(keyword.kwlist): string_keywords += '|' + str(key)

        # Define simple regex for keywords, strings, and variables
        keywords = fr'\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|false|finally|for|function|if|import|in|instanceof|new|null|return|super|switch|this|throw|true|try|typeof|undefined|var|void|while|with|yield|async|await|from|of|get|set|target)\b'
        strings = r'(\".*?\"|\'.*?\')'
        integer = r'-?\d+'
        comment = r'^#.*$'
        builtin = fr'\b({string_builtin})\b'

        # Highlight buitlin
        for match in re.finditer(builtin, code):
            self.text_editor.tag_add("builtin", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight keywords
        for match in re.finditer(keywords, code):
            self.text_editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight integers
        for match in re.finditer(integer, code, re.MULTILINE):
            self.text_editor.tag_add("integer", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight strings
        for match in re.finditer(strings, code):
            self.text_editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        # Highlight comments
        for match in re.finditer(comment, code, re.MULTILINE):
            self.text_editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def highlight_syntax_css(self):
        """Highlights syntax in the text editor for CSS """
        code = self.text_editor.get("1.0", tk.END)

        self.text_editor.tag_remove("keyword", "1.0", tk.END)
        self.text_editor.tag_remove("string", "1.0", tk.END)
        self.text_editor.tag_remove("integer", "1.0", tk.END)
        self.text_editor.tag_remove("builtins", "1.0", tk.END)
        self.text_editor.tag_remove("comments", "1.0", tk.END)

        css_comment_regex = r"/\*.*?\*/"
        selector = r"(\.[a-zA-Z_][a-zA-Z0-9_-]*)|(\#[a-zA-Z_][a-zA-Z0-9_-]*)|([a-zA-Z\*][a-zA-Z0-9\*_-]*)"
        property = r":\s*([^;]+);"
        unit = r"\b(\d+(?:px|em|rem|%|vw|vh|ch|cm|mm|in|pt|pc|ex|deg|rad|turn|s|ms|kHz|MHz|GHz)?)\b"
        media_query = r"@media\s+.*?\b\{"

        for match in re.finditer(css_comment_regex, code, re.DOTALL):
            self.text_editor.tag_add("comment", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(selector, code):
            self.text_editor.tag_add("keyword", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(unit, code):
            self.text_editor.tag_add("int", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(r"\b(#(?:[0-9a-fA-F]{3}){1,2})\b", code):  # Hex codes only
            self.text_editor.tag_add("int", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(property, code):
            self.text_editor.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")


        for match in re.finditer(r"\b(aqua|black|blue|fuchsia|gray|green|lime|maroon|navy|olive|purple|red|silver|teal|white|yellow)\b", code, re.IGNORECASE): # Named colors
            self.text_editor.tag_add("builtins", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

        for match in re.finditer(media_query, code, re.MULTILINE):
            self.text_editor.tag_add("builtins", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    @staticmethod
    def open_image(image_path):
        """Opens the image in MS Paint with the specified path"""
        # TODO: Intergrate this locally in IDE
        try:
            # Construct the command
            command = ["mspaint", image_path]  # mspaint is the executable name

            # Open MS Paint with the file
            subprocess.Popen(command)

        except FileNotFoundError:
            print("Error: MS Paint not found.  Make sure it's in your PATH.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def auto_tab(self, e):
        """Auto-indents the text based on the indentation of the previous line"""
        if e.keysym == 'Return':
            self.text_editor.delete('insert-1char')
            cursor_position = self.text_editor.index("insert")
            line_start = f"{cursor_position} linestart"
            line_end = f"{cursor_position} lineend"
            line_content = self.text_editor.get(line_start, cursor_position)

            # Check for colon at the end of the line
            if line_content.endswith(':'):
                indentation = "\t"
                for char in line_content:
                    if char == '\t':
                        indentation += '\t'

                self.text_editor.insert(line_end, '\n'+indentation)  # Add 4 spaces for indentation

                return "break"  # Prevent default behavior
            elif line_content:
                indentation = ""
                for char in line_content:
                    if char == '\t':
                        indentation += '\t'

                self.text_editor.insert(line_end, '\n'+indentation)  # Add 4 spaces for indentation

                return "break"  # Prevent default behavior
            else:
                self.text_editor.insert(line_end, '\n')
    @staticmethod
    def open_explorer(filepath):
        """Opens Explorer and selects the specified file."""
        # TODO: Integrate as many file types locally in IDE
        try:
            command = f'explorer /select,"{filepath}"'
            subprocess.Popen(command, shell=True)  # shell=True is important here

        except Exception as e:
            print(f"An error occurred: {e}")


class LineNumbers(tk.Canvas):
    """Displays line numbers in the text editor."""
    def __init__(self, master, textwidget, **kwargs):
        # Initialize the Canvas
        super().__init__(master, width=60, highlightthickness=0, **kwargs)
        self.textwidget = textwidget
        self.textwidget.bind("<MouseWheel>", self.redraw)
        self.textwidget.bind("<Configure>", self.redraw)
        self.numbers = []

    def redraw(self, event=None):
        """Redraw the line numbers."""
        self.delete("all")
        self.numbers = []

        top_line = self.textwidget.index("0.1")
        bottom_line = self.textwidget.index(f"end")

        try:  # Handle potential errors if indices are invalid
            first_line_num = int(top_line.split(".")[0])
            last_line_num = int(bottom_line.split(".")[0])

            for line_num in range(first_line_num, last_line_num + 1):
                dlineinfo = self.textwidget.dlineinfo(f"{line_num}.1")
                if dlineinfo:
                    y = dlineinfo[1]
                    self.create_text(5, y, anchor=tk.NW, text=str(line_num), font=self.textwidget["font"])
                    self.numbers.append(line_num)
        except Exception:
            pass



# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    ide = MyDE(root)
    while True:
        try:
            root.mainloop()
        except Exception as e:
            tk.messagebox.showerror('Error', f'An error has occurred if \n{e}')










