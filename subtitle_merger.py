import aeidon
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from guessit import guessit
from dataclasses import dataclass
from utils import detect_encoding, remove_html
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SubtitleInfo:
    """کلاس برای نگهداری اطلاعات متادیتای زیرنویس"""
    title: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    year: Optional[int] = None
    language: Optional[str] = None

class SubtitleMerger:
    """کلاس اصلی برای ادغام زیرنویس‌ها با قابلیت‌های پیشرفته"""
    
    SUPPORTED_ENCODINGS = ['utf-8', 'UTF-8-SIG', 'windows-1256', 'cp1256', 'iso-8859-6', 'mac-farsi']
    DEFAULT_ENCODING = 'windows-1256'
    
    def __init__(self, in_filename1: str, in_filename2: str, out_filename: str, 
                 font_name: str = "Arial", font_size: int = 20):
        """
        مقداردهی اولیه ادغام‌کننده زیرنویس
        
        Args:
            in_filename1: مسیر فایل زیرنویس اول
            in_filename2: مسیر فایل زیرنویس دوم
            out_filename: مسیر فایل خروجی
            font_name: نام فونت برای زیرنویس خروجی
            font_size: سایز فونت برای زیرنویس خروجی
        """
        self.in_filename1 = Path(in_filename1)
        self.in_filename2 = Path(in_filename2)
        self.out_filename = Path(out_filename)
        self.font_name = font_name
        self.font_size = font_size
        self._temp_files: List[Path] = []

    def __enter__(self):
        """پشتیبانی از context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """حذف فایل‌های موقت هنگام خروج"""
        self.cleanup_temp_files()

    def merge_subtitles(self) -> None:
        """ادغام دو فایل زیرنویس و ذخیره نتیجه"""
        try:
            # تبدیل به UTF-8 به صورت موازی
            with ThreadPoolExecutor() as executor:
                convert_func = partial(self.convert_subtitle_to_utf8, cleanup=False)
                self.in_filename1, self.in_filename2 = list(executor.map(
                    convert_func, [self.in_filename1, self.in_filename2]
                ))

            # پردازش زیرنویس‌ها
            project1, project2 = self._load_subtitle_projects()

            # تنظیم استایل‌ها
            self._prepare_subtitle_styles(project1, project2)

            # ذخیره فایل نهایی
            self._save_merged_subtitles(project1)
            
            logger.info(f"Subtitles successfully merged and saved as {self.out_filename}")

        except Exception as e:
            logger.error(f"Error during subtitle merging: {e}", exc_info=True)
            raise
        finally:
            self.cleanup_temp_files()

    def _load_subtitle_projects(self) -> tuple[aeidon.Project, aeidon.Project]:
        """بارگذاری پروژه‌های زیرنویس"""
        projects = []
        for filename in [self.in_filename1, self.in_filename2]:
            project = aeidon.Project()
            try:
                project.open_main(str(filename), 'utf-8')
                projects.append(project)
            except Exception as e:
                logger.error(f"Error opening subtitle file {filename}: {e}")
                raise
        return tuple(projects)

    def _prepare_subtitle_styles(self, 
                               project1: aeidon.Project, 
                               project2: aeidon.Project) -> None:
        """آماده‌سازی استایل‌های زیرنویس"""
        for subtitle in project1.subtitles:
            subtitle.main_text = remove_html(subtitle.main_text)
            subtitle.ssa.style = "Top"
            
        for subtitle in project2.subtitles:
            subtitle.main_text = remove_html(subtitle.main_text)
            subtitle.ssa.style = "Bot"
            
        project1.subtitles.extend(project2.subtitles)

    def _save_merged_subtitles(self, project: aeidon.Project) -> None:
        """ذخیره زیرنویس‌های ادغام شده"""
        out_format = aeidon.files.new(
            aeidon.formats.ASS, 
            str(self.out_filename), 
            "utf_8"
        )
        out_format.header = self.get_ass_header()
        
        try:
            project.save_main(out_format)
        except aeidon.AeidonError as e:
            logger.error(f"Error saving merged subtitles: {e}")
            raise

    def convert_subtitle_to_utf8(self, 
                               input_file: Path, 
                               cleanup: bool = True) -> Path:
        """
        تبدیل زیرنویس به UTF-8 با تشخیص خودکار انکدینگ
        
        Args:
            input_file: مسیر فایل ورودی
            cleanup: آیا فایل موقت باید بعداً پاک شود
            
        Returns:
            مسیر فایل تبدیل شده
        """
        detected_encoding = detect_encoding(input_file)
        logger.info(f"Detected encoding for {input_file}: {detected_encoding}")

        input_encoding = (
            detected_encoding 
            if detected_encoding in self.SUPPORTED_ENCODINGS 
            else self.DEFAULT_ENCODING
        )

        try:
            # خواندن محتوا با انکدینگ تشخیص داده شده
            content = input_file.read_text(encoding=input_encoding)
            
            # ایجاد فایل موقت
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8', 
                suffix='.srt', 
                delete=False
            )
            temp_file_path = Path(temp_file.name)
            
            with temp_file:
                temp_file.write(content)
            
            if cleanup:
                self._temp_files.append(temp_file_path)
                
            logger.info(f"File converted to UTF-8: {temp_file_path}")
            return temp_file_path
            
        except UnicodeDecodeError:
            logger.warning(f"Decoding failed with {input_encoding}, using original file")
            return input_file
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            return input_file

    def get_ass_header(self) -> str:
        """تهیه هدر فایل ASS با استایل‌های تعریف شده"""
        return f"""[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayResX: 384
PlayResY: 288
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Top, {self.font_name}, {self.font_size}, &H00F9FFFF, &H00FFFFFF, &H80000000, &H80000000, 0, 0, 0, 0, 100, 100, 0, 0, 1, 3, 0, 8, 10, 10, 10, 0
Style: Bot, {self.font_name}, {self.font_size}, &H00F9FFF9, &H00FFFFFF, &H80000000, &H80000000, 0, 0, 0, 0, 100, 100, 0, 0, 1, 3, 0, 2, 10, 10, 10, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def cleanup_temp_files(self) -> None:
        """پاکسازی فایل‌های موقت"""
        for temp_file in self._temp_files:
            try:
                temp_file.unlink()
                logger.info(f"Temporary file removed: {temp_file}")
            except OSError as e:
                logger.warning(f"Error removing temp file {temp_file}: {e}")

    @staticmethod
    def guess_name(first_name: str, second_name: str) -> str:
        """
        حدس نام فایل نهایی بر اساس اطلاعات متادیتا
        
        Args:
            first_name: نام فایل اول
            second_name: نام فایل دوم
            
        Returns:
            نام استاندارد شده فایل
        """
        def parse_info(name: str) -> SubtitleInfo:
            """استخراج اطلاعات از نام فایل"""
            info = guessit(name)
            return SubtitleInfo(
                title=info.get('title'),
                season=info.get('season'),
                episode=info.get('episode'),
                year=info.get('year'),
                language=info.get('language')
            )

        info1 = parse_info(first_name)
        info2 = parse_info(second_name)
        
        # انتخاب بهترین مقادیر از دو فایل
        final_info = SubtitleInfo(
            title=info1.title or info2.title,
            season=info1.season or info2.season,
            episode=info1.episode or info2.episode,
            year=info1.year or info2.year,
            language=info1.language or info2.language
        )

        if not final_info.title:
            raise ValueError("Could not determine title from file names")

        # ساخت نام نهایی
        name_parts = [final_info.title.replace(' ', '.')]
        
        if final_info.season is not None:
            name_parts.append(f"S{final_info.season:02d}")
        if final_info.episode is not None:
            name_parts.append(f"E{final_info.episode:02d}")
        if final_info.year is not None:
            name_parts.append(str(final_info.year))
        if final_info.language is not None:
            name_parts.append(final_info.language.upper())

        return ".".join(name_parts)

    @classmethod
    def from_directory(cls, directory: str, 
                      output_dir: str = None, 
                      **kwargs) -> List['SubtitleMerger']:
        """
        ایجاد ادغام‌کننده‌ها برای تمام فایل‌های زیرنویس در یک دایرکتوری
        
        Args:
            directory: مسیر دایرکتوری حاوی فایل‌های زیرنویس
            output_dir: مسیر دایرکتوری خروجی (اختیاری)
            kwargs: سایر پارامترهای مورد نیاز برای SubtitleMerger
            
        Returns:
            لیستی از SubtitleMergerهای آماده
        """
        dir_path = Path(directory)
        srt_files = list(dir_path.glob('*.srt'))
        
        if len(srt_files) < 2:
            raise ValueError("At least two subtitle files are required")
            
        output_dir = Path(output_dir) if output_dir else dir_path
        output_dir.mkdir(exist_ok=True)
        
        mergers = []
        for i in range(0, len(srt_files)-1, 2):
            file1, file2 = srt_files[i], srt_files[i+1]
            output_name = cls.guess_name(file1.name, file2.name) + ".ass"
            output_path = output_dir / output_name
            mergers.append(cls(file1, file2, output_path, **kwargs))
            
        return mergers
