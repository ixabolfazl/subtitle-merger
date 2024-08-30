import aeidon
import os
import tempfile
from guessit import guessit

from utils import detect_encoding, remove_html

class SubtitleMerger:
    def __init__(self, in_filename1, in_filename2, out_filename, font_name, font_size):
        self.in_filename1 = in_filename1
        self.in_filename2 = in_filename2
        self.out_filename = out_filename
        self.font_name = font_name
        self.font_size = font_size

    def merge_subtitles(self):
        temp_files = []
        try:
            self.in_filename1 = self.convert_subtitle_to_utf8(self.in_filename1)
            self.in_filename2 = self.convert_subtitle_to_utf8(self.in_filename2)

            temp_files = [f for f in [self.in_filename1, self.in_filename2] if f != self.in_filename1 and f != self.in_filename2]

            project1 = aeidon.Project()
            project2 = aeidon.Project()

            try:
                project1.open_main(self.in_filename1, 'utf-8')
                project2.open_main(self.in_filename2, 'utf-8')
            except Exception as e:
                print(f"An error occurred: {str(e)}.")

            out_format = aeidon.files.new(aeidon.formats.ASS, self.out_filename, "utf_8")
            out_format.header = self.get_ass_header()

            for subtitle in project1.subtitles:
                subtitle.main_text = remove_html(subtitle.main_text)
                subtitle.ssa.style = "Top"
            for subtitle in project2.subtitles:
                subtitle.main_text = remove_html(subtitle.main_text)
                subtitle.ssa.style = "Bot"

            project1.subtitles.extend(project2.subtitles)

            try:
                project1.save_main(out_format)
                print(f"Subtitles successfully merged and saved as {self.out_filename}")
            except aeidon.AeidonError as e:
                raise Exception(f"Error saving merged subtitles: {str(e)}")

        except Exception as e:
            print(f"An error occurred during subtitle merging: {str(e)}")
            raise

        finally:
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                    print(f"Temporary file {temp_file} removed.")
                except OSError as e:
                    print(f"Error removing temporary file {temp_file}: {e}")

    def convert_subtitle_to_utf8(self, input_file):
        detected_encoding = detect_encoding(input_file)
        print(f"Detected encoding: {detected_encoding}")

        input_encoding = detected_encoding if detected_encoding in ['utf-8', 'UTF-8-SIG', 'windows-1256', 'cp1256', 'iso-8859-6', 'mac-farsi'] else 'windows-1256'

        try:
            with open(input_file, 'r', encoding=input_encoding) as file:
                content = file.read()

            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.srt', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            print(f"File successfully converted to UTF-8 and saved as {temp_file_path}")
            return temp_file_path
        except UnicodeDecodeError:
            print(f"Error reading the file with encoding {input_encoding}. Using original file.")
            return input_file
        except Exception as e:
            print(f"An error occurred: {str(e)}. Using original file.")
            return input_file

    def get_ass_header(self):
        return f"""[Script Info]
ScriptType: v4.00+
Collisions: Normal
[V4+ Styles]
        Name,Fontname  ,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style:  Top ,{self.font_name} ,{self.font_size}      ,&H00F9FFFF   ,&H00FFFFFF     ,&H80000000   ,&H80000000,0   ,0     ,0        ,0        ,100   ,100   ,0      ,0    ,1          ,3      ,0     ,8        ,10     ,10     ,10     ,0
Style:  Bot ,{self.font_name} ,{self.font_size}      ,&H00F9FFF9   ,&H00FFFFFF     ,&H80000000   ,&H80000000,0   ,0     ,0        ,0        ,100   ,100   ,0      ,0    ,1          ,3      ,0     ,2        ,10     ,10     ,10     ,0
"""

    @staticmethod
    def guess_name(first_name, second_name):
        first_name = guessit(first_name)
        second_name = guessit(second_name)

        title = first_name.get('title') or second_name.get('title')
        season = first_name.get('season') or second_name.get('season')
        episode = first_name.get('episode') or second_name.get('episode')
        year = first_name.get('year') or second_name.get('year')

        final_name = title.replace(' ', '.') if title else ''

        if season is not None:
            season = str(season).zfill(2)
            final_name += ".S" + season
        if episode is not None:
            episode = str(episode).zfill(2)
            final_name += "E" + episode
        if year is not None:
            final_name += "." + str(year)

        return final_name
