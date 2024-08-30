import chardet
import re
from tkinter import font
import platform
import os
import subprocess
from tkinter import filedialog


def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def remove_html(string):
    regex = re.compile(r'<[^>]+>')
    return regex.sub('', string)

def detect_font():
    fonts = font.families()
    if "Vazirmatn" in fonts:
        return "Vazirmatn"
    elif "Vazir" in fonts:
        return "Vazir"
    elif "Times New Roman" in fonts:
        return "Times New Roman"
    else:
        return "Arial"

def open_github(url):
    if platform.system() == 'Windows':
        os.startfile(url)
    elif platform.system() == 'Darwin':
        subprocess.run(['open', url])
    else:
        subprocess.run(['xdg-open', url])

def get_file_via_file_manager():
    if platform.system() == "Linux":
        try:
            file_path = subprocess.check_output(["zenity", "--file-selection"], universal_newlines=True).strip()
            return file_path
        except subprocess.CalledProcessError:
            return None
    else:
        return filedialog.askopenfilename(filetypes=[("Subtitles", "*.srt *.ass *.ssa")])

def get_directory_via_file_manager():
    if platform.system() == "Linux":
        try:
            directory = subprocess.check_output(["zenity", "--file-selection", "--directory"], universal_newlines=True).strip()
            return directory
        except subprocess.CalledProcessError:
            return None
    else:
        return filedialog.askdirectory()
