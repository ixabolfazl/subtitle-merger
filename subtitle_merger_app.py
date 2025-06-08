import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from tkinter import messagebox
from tkfontchooser import askfont
from subtitle_merger import SubtitleMerger
from utils import *
from typing import Optional
import webbrowser
from pathlib import Path
import logging

VERSION = "v2.0"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModernSubtitleMergerApp(ttk.Window):
    def __init__(self):
        """Initialize the main application window with modern styling."""
        super().__init__(themename="darkly")
        self.title("Subtitle Merger Pro")
        self.geometry("900x750")
        self.minsize(800, 700)
        
        try:
            self.iconbitmap(default='assets/icon.ico') if os.path.exists('assets/icon.ico') else None
        except:
            pass
        
        self.top_sub_entry = tk.StringVar()
        self.bottom_sub_entry = tk.StringVar()
        self.save_dir_entry = tk.StringVar(value=self.load_saved_directory())
        self.font_name_entry = tk.StringVar(value=detect_font())
        self.font_size_entry = tk.StringVar(value="25")
        self.progress_var = tk.DoubleVar()
        
        self.create_widgets()
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.style.configure('success.TButton', font=('Helvetica', 12, 'bold'))
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        
        logger.info("Application initialized successfully")

    def create_widgets(self):
        """Create all GUI widgets with modern layout."""
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        self.canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient=VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.create_title_section()
        self.create_input_section()
        self.create_output_section()
        self.create_merge_section()
        self.create_status_section()
        self.create_footer_section()
        
        if not os.path.exists("first_run.flag"):
            self.show_quick_guide()
            Path("first_run.flag").touch()

    def create_title_section(self):
        """Create the title section with modern styling."""
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(pady=(10, 20), fill=X)
        
        title_label = ttk.Label(
            title_frame, 
            text="SUBTITLE MERGER PRO", 
            font=("Helvetica", 24, "bold"),
            foreground="#4fc3f7"
        )
        title_label.pack(side=LEFT)
        
        version_badge = ttk.Label(
            title_frame,
            text=VERSION,
            font=("Helvetica", 10),
            bootstyle="inverse-primary",
            padding=(5, 2)
        )
        version_badge.pack(side=RIGHT, padx=5)
        
        help_btn = ttk.Button(
            title_frame,
            text="?",
            command=self.show_quick_guide,
            width=2,
            bootstyle="outline-light"
        )
        help_btn.pack(side=RIGHT)

    def create_input_section(self):
        """Create the input section with file selection."""
        input_frame = ttk.Labelframe(
            self.scrollable_frame, 
            text="INPUT SUBTITLES",
            padding=20,
            bootstyle="primary"
        )
        input_frame.pack(fill=X, pady=10, padx=10)
        
        self.create_file_input(
            input_frame, 
            "Top Subtitle:", 
            self.top_sub_entry,
            filetypes=[("Subtitle Files", "*.ass *.srt *.ssa"), ("All Files", "*.*")]
        )
        
        self.create_file_input(
            input_frame, 
            "Bottom Subtitle:", 
            self.bottom_sub_entry,
            filetypes=[("Subtitle Files", "*.ass *.srt *.ssa"), ("All Files", "*.*")]
        )
        
        swap_btn = ttk.Button(
            input_frame,
            text="↕ Swap Subtitles ↕",
            command=self.swap_subtitles,
            bootstyle="outline-light",
            width=20
        )
        swap_btn.pack(pady=(10, 0))

    def create_output_section(self):
        """Create the output settings section."""
        output_frame = ttk.Labelframe(
            self.scrollable_frame,
            text="OUTPUT SETTINGS",
            padding=20,
            bootstyle="info"
        )
        output_frame.pack(fill=X, pady=10, padx=10)
        
        self.create_directory_input(output_frame)
        
        self.create_name_input(output_frame)
        
        self.create_font_settings(output_frame)
        
        self.create_advanced_options(output_frame)

    def create_merge_section(self):
        """Create the merge button section."""
        button_frame = ttk.Frame(self.scrollable_frame)
        button_frame.pack(pady=20)
        
        self.merge_btn = ttk.Button(
            button_frame,
            text="🚀 MERGE SUBTITLES",
            command=self.merge_button_click,
            bootstyle="success",
            width=20,
            padding=10
        )
        self.merge_btn.pack(side=LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(
            button_frame,
            variable=self.progress_var,
            bootstyle="success-striped",
            length=200,
            mode='determinate'
        )
        self.progress_bar.pack(side=LEFT, padx=5, fill=X, expand=True)

    def create_status_section(self):
        """Create the status display section."""
        status_frame = ttk.Frame(self.scrollable_frame)
        status_frame.pack(fill=X, pady=10)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to merge subtitles...",
            font=("Helvetica", 11),
            bootstyle="light",
            anchor=CENTER,
            relief="sunken",
            padding=10
        )
        self.status_label.pack(fill=X, expand=True)
        
        self.recent_files_label = ttk.Label(
            status_frame,
            text="Recent files will appear here",
            font=("Helvetica", 9),
            bootstyle="secondary",
            anchor=W,
            padding=(5, 2)
        )
        self.recent_files_label.pack(fill=X)

    def create_footer_section(self):
        """Create the footer with credits and links."""
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(side=BOTTOM, fill=X, pady=20)
        
        author_frame = ttk.Frame(footer_frame)
        author_frame.pack(side=LEFT, fill=X, expand=True)
        
        ttk.Label(
            author_frame,
            text="Developed by Abolfazl Khalili",
            font=("Helvetica", 9),
            bootstyle="secondary"
        ).pack(side=LEFT)
        
        links_frame = ttk.Frame(footer_frame)
        links_frame.pack(side=RIGHT)
        
        self.create_link_button(
            links_frame, 
            "GitHub", 
            "https://github.com/ixabolfazl/subtitle-merger"
        )
        
        self.create_link_button(
            links_frame,
            "Report Issue",
            "https://github.com/ixabolfazl/subtitle-merger/issues"
        )
        
        self.create_link_button(
            links_frame,
            "Donate",
            "https://paypal.me/ixabolfazl"
        )

    def create_file_input(self, parent, label_text, entry_var, filetypes=None):
        """Create a file input widget with modern styling."""
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=5)
        
        ttk.Label(
            frame, 
            text=label_text,
            width=15,
            anchor=E
        ).pack(side=LEFT)
        
        entry = ttk.Entry(
            frame,
            textvariable=entry_var,
            bootstyle="light"
        )
        entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        
        browse_btn = ttk.Button(
            frame,
            text="📂 Browse",
            command=lambda: self.browse_file(entry_var, filetypes),
            bootstyle="outline-light",
            width=10
        )
        browse_btn.pack(side=LEFT)
        
        clear_btn = ttk.Button(
            frame,
            text="✕",
            command=lambda: entry_var.set(""),
            bootstyle="outline-danger",
            width=2
        )
        clear_btn.pack(side=LEFT, padx=2)

    def create_directory_input(self, parent):
        """Create directory input widget."""
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=5)
        
        ttk.Label(
            frame,
            text="Save Directory:",
            width=15,
            anchor=E
        ).pack(side=LEFT)
        
        entry = ttk.Entry(
            frame,
            textvariable=self.save_dir_entry,
            bootstyle="light"
        )
        entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        
        browse_btn = ttk.Button(
            frame,
            text="📁 Browse",
            command=self.browse_save_directory,
            bootstyle="outline-light",
            width=10
        )
        browse_btn.pack(side=LEFT)
        
        open_btn = ttk.Button(
            frame,
            text="↗ Open",
            command=lambda: os.startfile(self.save_dir_entry.get()),
            bootstyle="outline-info",
            width=8
        )
        open_btn.pack(side=LEFT, padx=2)

    def create_name_input(self, parent):
        """Create output name input widget."""
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=5)
        
        ttk.Label(
            frame,
            text="Output Name:",
            width=15,
            anchor=E
        ).pack(side=LEFT)
        
        self.final_name_entry = ttk.Entry(
            frame,
            bootstyle="light"
        )
        self.final_name_entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        self.final_name_entry.insert(0, "merged_sub.ass")
        
        suggest_btn = ttk.Button(
            frame,
            text="Suggest Name",
            command=self.guess_out_file_name,
            bootstyle="outline-secondary",
            width=12
        )
        suggest_btn.pack(side=LEFT, padx=2)

    def create_font_settings(self, parent):
        """Create font selection widgets."""
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=5)
        
        ttk.Label(
            frame,
            text="Font Settings:",
            width=15,
            anchor=E
        ).pack(side=LEFT)
        
        font_entry = ttk.Entry(
            frame,
            textvariable=self.font_name_entry,
            bootstyle="light"
        )
        font_entry.pack(side=LEFT, expand=True, fill=X, padx=5)
        
        browse_btn = ttk.Button(
            frame,
            text="✎ Choose Font",
            command=self.browse_font,
            bootstyle="outline-light",
            width=12
        )
        browse_btn.pack(side=LEFT)
        
        ttk.Label(
            frame,
            text="Size:",
            padding=(10, 0, 5, 0)
        ).pack(side=LEFT)
        
        font_size_spin = ttk.Spinbox(
            frame,
            from_=8,
            to=72,
            textvariable=self.font_size_entry,
            width=4,
            bootstyle="light"
        )
        font_size_spin.pack(side=LEFT)

    def create_advanced_options(self, parent):
        """Create advanced options section."""
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=10)
        
        self.preserve_formatting_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Preserve original formatting",
            variable=self.preserve_formatting_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=2)
        
        self.backup_files_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Create backup files",
            variable=self.backup_files_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=2)

    def create_link_button(self, parent, text, url):
        """Create a clickable link button."""
        btn = ttk.Button(
            parent,
            text=text,
            command=lambda: webbrowser.open(url),
            bootstyle="link",
            padding=(5, 0)
        )
        btn.pack(side=LEFT, padx=5)
        return btn

    def browse_file(self, entry_var, filetypes=None):
        """Open file dialog to select subtitle file."""
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            entry_var.set(file_path)
            self.guess_out_file_name()
            self.update_status(f"Selected: {os.path.basename(file_path)}")

    def browse_font(self):
        """Open font chooser dialog."""
        font = askfont(self)
        if font:
            self.font_name_entry.set(font['family'])
            if font['size'] > 0:
                self.font_size_entry.set(font['size'])
            self.update_status(f"Font set to: {font['family']} {font['size']}")

    def browse_save_directory(self):
        """Open directory dialog to select save location."""
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_entry.set(directory)
            self.save_directory(directory)
            self.update_status(f"Save location: {directory}")

    def save_directory(self, directory: str):
        """Save the selected directory to a file."""
        try:
            with open("save_directory.txt", 'w') as f:
                f.write(directory)
            logger.info(f"Saved directory: {directory}")
        except Exception as e:
            logger.error(f"Error saving directory: {e}")

    def load_saved_directory(self) -> str:
        """Load the last used directory from file."""
        try:
            if os.path.exists("save_directory.txt"):
                with open("save_directory.txt", 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading saved directory: {e}")
        return os.getcwd()

    def guess_out_file_name(self):
        """Generate a suggested output filename based on inputs."""
        first_name = self.top_sub_entry.get()
        second_name = self.bottom_sub_entry.get()
        
        if first_name and second_name:
            try:
                guessed_name = f"{SubtitleMerger.guess_name(first_name, second_name)}.ass"
                self.final_name_entry.delete(0, tk.END)
                self.final_name_entry.insert(0, guessed_name)
                self.update_status(f"Suggested filename: {guessed_name}")
            except Exception as e:
                logger.error(f"Error guessing filename: {e}")

    def swap_subtitles(self):
        """Swap the top and bottom subtitle entries."""
        top = self.top_sub_entry.get()
        bottom = self.bottom_sub_entry.get()
        
        self.top_sub_entry.set(bottom)
        self.bottom_sub_entry.set(top)
        self.update_status("Swapped top and bottom subtitles")

    def merge_button_click(self):
        """Handle the merge button click event."""
        top_sub = self.top_sub_entry.get()
        bot_sub = self.bottom_sub_entry.get()
        save_dir = self.save_dir_entry.get()
        out_sub = os.path.join(save_dir, self.final_name_entry.get().strip('.ass') + '.ass')

        if not self.validate_inputs(top_sub, bot_sub, save_dir, out_sub):
            return

        try:
            self.merge_btn.config(state=tk.DISABLED)
            self.progress_var.set(10)
            self.update_status("Starting merge process...")
            self.update()
            
            merger = SubtitleMerger(
                top_sub, 
                bot_sub, 
                out_sub, 
                self.font_name_entry.get(), 
                self.font_size_entry.get()
            )
            
            merger.merge_subtitles()
            
            self.progress_var.set(100)
            self.update_status(f"Success! Merged subtitle saved to:\n{out_sub}", success=True)
            self.add_to_recent_files(out_sub)
            
        except Exception as e:
            logger.error(f"Merge error: {e}")
            self.update_status(f"Error! {str(e)}", error=True)
            messagebox.showerror(
                "Merge Error",
                f"An error occurred during merging:\n\n{str(e)}",
                parent=self
            )
        finally:
            self.merge_btn.config(state=tk.NORMAL)
            self.after(3000, lambda: self.progress_var.set(0))

    def validate_inputs(self, top_sub: str, bot_sub: str, save_dir: str, out_sub: str) -> bool:
        """Validate user inputs before merging."""
        if not top_sub or not bot_sub:
            self.update_status("Error! Please select both subtitle files.", error=True)
            return False
            
        if not os.path.exists(save_dir):
            self.update_status("Error! Save directory does not exist.", error=True)
            messagebox.showerror(
                "Directory Error",
                "The specified save directory does not exist.\nPlease choose a valid directory.",
                parent=self
            )
            return False
            
        if os.path.exists(out_sub):
            response = messagebox.askyesno(
                "File Exists",
                "The output file already exists. Do you want to overwrite it?",
                parent=self
            )
            if not response:
                self.update_status("Merge canceled - file exists")
                return False
                
        return True

    def update_status(self, message: str, success: bool = False, error: bool = False):
        """Update the status label with appropriate styling."""
        style = "default"
        if success:
            style = "success"
        elif error:
            style = "danger"
            
        self.status_label.config(text=message)
        self.status_label.config(bootstyle=style)
        logger.info(f"Status update: {message}")

    def add_to_recent_files(self, filepath: str):
        """Add the merged file to recent files list."""
        recent_text = f"Last merged: {os.path.basename(filepath)}"
        self.recent_files_label.config(text=recent_text)
        
        try:
            with open("recent_files.log", 'a') as f:
                f.write(f"{filepath}\n")
        except:
            pass

    def show_quick_guide(self):
        """Show a quick start guide dialog."""
        guide_text = """
        📝 Subtitle Merger Pro - Quick Guide
        
        1. Select your top and bottom subtitle files
        2. Choose where to save the merged file
        3. Adjust font settings if needed
        4. Click 'MERGE SUBTITLES' button
        
        Tips:
        - Use 'Suggest Name' for automatic naming
        - Swap subtitles if their order is wrong
        - Check 'Preserve formatting' to keep original styles
        """
        
        messagebox.showinfo(
            "Quick Start Guide",
            guide_text.strip(),
            parent=self
        )

    def on_close(self):
        """Handle window close event."""
        logger.info("Application closing")
        self.destroy()

if __name__ == "__main__":
    app = ModernSubtitleMergerApp()
    app.mainloop()
