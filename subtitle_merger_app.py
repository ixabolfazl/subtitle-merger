import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from tkinter import messagebox
from tkinter import filedialog
from tkfontchooser import askfont
from subtitle_merger import SubtitleMerger
from utils import *


VERSION = "v1.0"


class SubtitleMergerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.style = ttk.Style("darkly")
        self.title("Subtitle Merger")
        self.geometry("800x700")

        self.top_sub_entry = tk.StringVar()
        self.bottom_sub_entry = tk.StringVar()
        self.save_dir_entry = tk.StringVar()
        self.save_dir_entry.set(self.load_saved_directory())
        self.font_name_entry = tk.StringVar(value=detect_font())
        self.font_size_entry = tk.StringVar(value="25")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=BOTH, expand=YES)

        self.create_title(main_frame)
        self.create_input_frame(main_frame)
        self.create_output_frame(main_frame)
        self.create_merge_button(main_frame)
        self.create_status_label(main_frame)
        self.create_footer()

    def create_title(self, parent):
        title_label = ttk.Label(parent, text="Subtitle Merger", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

    def create_input_frame(self, parent):
        input_frame = ttk.Labelframe(parent, text="Input Subtitles", padding=20)
        input_frame.pack(fill=X, expand=YES, pady=10)

        self.create_subtitle_input(input_frame, "Top Subtitle", self.top_sub_entry)
        self.create_subtitle_input(input_frame, "Bottom Subtitle", self.bottom_sub_entry)

    def create_output_frame(self, parent):
        output_frame = ttk.Labelframe(parent, text="Output Settings", padding=20)
        output_frame.pack(fill=X, expand=YES, pady=10)

        self.create_directory_input(output_frame)
        self.create_name_input(output_frame)
        self.create_font_input(output_frame)

    def create_subtitle_input(self, parent, label_text, entry_var):
        frame = ttk.Frame(parent)
        frame.pack(fill=X, expand=YES, pady=5)

        label = ttk.Label(frame, text=label_text, width=15)
        label.pack(side=LEFT)

        entry = ttk.Entry(frame, textvariable=entry_var)
        entry.pack(side=LEFT, expand=YES, fill=X, padx=5)

        browse_button = ttk.Button(frame, text= "Browse", command=lambda: self.browse_file(entry_var))
        browse_button.pack(side=LEFT)

    def create_directory_input(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=X, expand=YES, pady=5)

        label = ttk.Label(frame, text= "Save Directory", width=15)
        label.pack(side=LEFT)

        entry = ttk.Entry(frame, textvariable=self.save_dir_entry)
        entry.pack(side=LEFT, expand=YES, fill=X, padx=5)

        browse_button = ttk.Button(frame, text= "Browse", command=self.browse_save_directory)
        browse_button.pack(side=LEFT)

    def create_name_input(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=X, expand=YES, pady=5)

        label = ttk.Label(frame, text="Output Name", width=15)
        label.pack(side=LEFT)

        self.final_name_entry = ttk.Entry(frame)
        self.final_name_entry.pack(side=LEFT, expand=YES, fill=X, padx=5)
        self.final_name_entry.insert(0, "merged_sub.ass")

    def create_font_input(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=X, expand=YES, pady=5)

        label = ttk.Label(frame, text="Font", width=15)
        label.pack(side=LEFT)

        font_entry = ttk.Entry(frame, textvariable=self.font_name_entry)
        font_entry.pack(side=LEFT, expand=YES, fill=X, padx=5)

        browse_button = ttk.Button(frame, text= "Browse", command=lambda: self.browse_font())
        browse_button.pack(side=LEFT)

        size_label = ttk.Label(frame, text= "Size")
        size_label.pack(side=LEFT, padx=(10, 5))

        font_size_entry = ttk.Entry(frame, textvariable=self.font_size_entry, width=5)
        font_size_entry.pack(side=LEFT)

    def create_merge_button(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(pady=20)

        merge_button = ttk.Button(button_frame, text="Merge Subtitles", command=self.merge_button_click, style="success.TButton")
        merge_button.pack(side=LEFT, padx=5)

    def create_status_label(self, parent):
        self.status_label = ttk.Label(parent, text="Select top and bottom subtitles.", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

    def create_footer(self):
        footer_frame = ttk.Frame(self)
        footer_frame.pack(side=BOTTOM, fill=X, padx=20, pady=10)

        attribution_label = ttk.Label(footer_frame, text="Made by Abolfazl Khalili", font=("Helvetica", 10), foreground="#888888")
        attribution_label.pack(side=LEFT)

        version_label = ttk.Label(footer_frame, text=VERSION, font=("Helvetica", 10), foreground="#888888")
        version_label.pack(side=RIGHT)

        github_label = ttk.Label(footer_frame, text="GitHub Repo", font=("Helvetica", 10), cursor="hand2", foreground="#888888", underline=True)
        github_label.pack(side=RIGHT, padx=(0, 10))
        github_label.bind("<Button-1>", lambda e: open_github( 'https://github.com/ixabolfazl/subtitle-merger'))

    def browse_file(self, entry_var):
        file_path = get_file_via_file_manager()
        if file_path:
            entry_var.set(file_path)
            self.guess_out_file_name()


    def browse_font(self):
        font = askfont()
   
        if font:
            self.font_name_entry.set(font['family'])
            self.font_size_entry.set(font['size'])

    def browse_save_directory(self):
        directory = get_directory_via_file_manager()
        if directory:
            self.save_dir_entry.set(directory)
            self.save_directory(directory)

    def save_directory(self, directory):
        with open("save_directory.txt", 'w') as f:
            f.write(directory)

    def load_saved_directory(self):
        if os.path.exists("save_directory.txt"):
            with open("save_directory.txt", 'r') as f:
                return f.read().strip()
        return os.getcwd()

    def guess_out_file_name(self):
        first_name = self.top_sub_entry.get()
        second_name = self.bottom_sub_entry.get()
        guessed_name = SubtitleMerger.guess_name(first_name, second_name)+'.ass'
        self.final_name_entry.delete(0, ttk.END)
        self.final_name_entry.insert(0, guessed_name)

    def merge_button_click(self):
        top_sub = self.top_sub_entry.get()
        bot_sub = self.bottom_sub_entry.get()
        save_dir = self.save_dir_entry.get()
        out_sub = os.path.join(save_dir, self.final_name_entry.get().strip('.ass') + '.ass')

        if not os.path.exists(save_dir):
            messagebox.showerror("Error", "Error! Save directory does not exist.")
            return

        if not top_sub or not bot_sub:
            self.status_label.config(text="Error! Input subtitles not provided.")
            return

        try:
            merger = SubtitleMerger(top_sub, bot_sub, out_sub, self.font_name_entry.get(), self.font_size_entry.get())
            merger.merge_subtitles()
            self.status_label.config(text=f"Done! Saved at: {out_sub}")
        except Exception as e:
            self.status_label.config(text=f"Error! {str(e)}")
