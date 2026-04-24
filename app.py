import flet as ft
import yt_dlp
import os
import ssl

# 1. SSL FIX (Keeps the connection from crashing)
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
import sys

def get_ffmpeg_path():
    # When PyInstaller runs the app, it unpacks files to a temp folder called _MEIPASS
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "ffmpeg")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")

ffmpeg_bin = get_ffmpeg_path()

def main(page: ft.Page):
    # 2. WINDOW CONFIG
    page.title = "YouTube to MP3 Converter"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 500
    page.window_height = 500
    page.theme_mode = ft.ThemeMode.DARK

    # 3. FFMPEG PATHING
    base_path = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_bin = os.path.join(base_path, 'ffmpeg')

    # 4. UI ELEMENTS
    url_input = ft.TextField(label="Paste YouTube URL here", width=400)
    status_text = ft.Text(value="Ready to download", color="grey")
    progress_ring = ft.ProgressRing(visible=False)

    def download_click(e):
        if not url_input.value:
            status_text.value = "Please enter a URL!"
            status_text.color = "red"
            page.update()
            return

        status_text.value = "Downloading... please wait."
        status_text.color = "blue"
        progress_ring.visible = True
        page.update()

        # Get the path to your Mac's Downloads folder
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

        ydl_opts = {
            'format': 'bestaudio/best',
            'nocheckcertificate': True,
            'ffmpeg_location': ffmpeg_bin,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # This saves it to /Users/reans/Downloads/
            'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url_input.value])
            status_text.value = "Success! MP3 saved to folder."
            status_text.color = "green"
        except Exception as err:
            status_text.value = f"Error: {str(err)}"
            status_text.color = "red"
        
        progress_ring.visible = False
        page.update()
    
    # 5. UI LAYOUT
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Icon("play_circle_filled_rounded", size=60, color="red"),
                    ft.Text("YouTube MP3 Converter", size=28, weight="bold"),
                    ft.Divider(height=20, color="transparent"),
                    url_input,
                    ft.ElevatedButton(
                        "Convert to MP3", 
                        on_click=download_click, 
                        icon="download",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                    ),
                    ft.Divider(height=10, color="transparent"),
                    progress_ring,
                    status_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30
        )
    )
    
    # CRITICAL: Tell Flet to refresh the page with the new content
    page.update()

# 6. START THE APP
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)