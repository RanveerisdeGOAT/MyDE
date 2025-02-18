# MyDE

A custom Integrated Development Environment (IDE) built with Python and Tkinter.

## How It Works

MyDE utilizes the following core components:

*   **Text Editor:**
    *   `tk.ScrolledText`:  Provides a scrollable text area for displaying and editing code files.
    *   `tk.Text` Tags: Implements syntax highlighting for various programming languages, enhancing code readability.
*   **Console/Terminal:**
    *   `tk.Text`: A `Text` widget is used to create a terminal-like interface within the IDE.
    *   `subprocess`: The `subprocess` module is used to execute code in a separate process, allowing for interaction with the running program (including handling `input()` calls).
    *   `threading`:  Threading is used to manage the execution of code and the display of output in the console concurrently, preventing the GUI from freezing.
    *   displaying output in the console.
*   **File Handling:**
    *   Standard Python file I/O operations are used to open, save, and manage files.
*   **Hotkeys:**
    *   Tkinter's event binding is used to implement hotkeys for common actions (e.g., Ctrl+S for save, Ctrl+O for open).
*   **Cross-Platform Support:**
    *   MyDE is designed to be cross-platform, leveraging Tkinter's inherent cross-platform capabilities.

## Features

*   Syntax highlighting for various programming languages (configurable).
*   Integrated console for code execution and interaction.
*   Support for running Python and HTML files directly from the editor.
*   Clean and user-friendly interface. (I think) ;)

## Getting Started

1.  **Prerequisites:**
    *   Python 3.x
    *   Tkinter (usually included with Python)

2.  **Installation:**
    *   Clone the repository: `git clone https://github.com/RanveeristdeGOAT/MyDE.git`
    *   Navigate to the directory: `cd MyDE`

3.  **Running MyDE:**
    *   Run the main script: `python main.py`

## Usage

1.  Open a file using the "File" menu.
2.  Edit the code in the text editor.
3.  Save the file using the "File".
4.  Run the code.
5.  Interact with the running program in the integrated console.

## Contributing

Contributions are welcome!  Please feel free to submit pull requests or open issues.

## Screenshots

![Screenshot 1](screenshots/screenshot1.png)
![Screenshot 2](screenshots/screenshot2.jpg)

## TODO

*   Implement support for more programming languages.
*   Add debugging features.
*   Improve syntax highlighting.
*   Implement a more robust file management system.
*   Create a settings/configuration dialog.
