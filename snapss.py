import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

import pytesseract
from PIL import Image, ImageOps

# ----------------------------------
# TESSERACT LOCATION
# ----------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ----------------------------------
# TIME PATTERN
# ----------------------------------

TIME_PATTERN = re.compile(
    r'(\d{1,2}:\d{2}\s?(?:AM|PM))',
    re.IGNORECASE
)

# ----------------------------------
# OCR IMAGE
# ----------------------------------

def scan_image(image_path):

    image = Image.open(image_path)

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 6"
    )

    return text.strip()

# ----------------------------------
# PROCESS FOLDER
# ----------------------------------

def process_folder(folder_path):

    image_files = []

    for file in os.listdir(folder_path):

        if file.lower().endswith(
            (".png", ".jpg", ".jpeg", ".webp")
        ):
            image_files.append(file)

    image_files.sort()

    transcript = []

    transcript.append("=" * 60)
    transcript.append("CHAT TRANSCRIPT")
    transcript.append("=" * 60)
    transcript.append("")

    total_files = len(image_files)

    for index, image in enumerate(image_files, start=1):

        full_path = os.path.join(folder_path, image)

        transcript.append("")
        transcript.append(
            f"--- Screenshot {index}/{total_files}: {image} ---"
        )
        transcript.append("")

        try:

            text = scan_image(full_path)

            transcript.append(text)

        except Exception as e:

            transcript.append(
                f"[ERROR READING IMAGE] {e}"
            )

        transcript.append("")
        transcript.append("-" * 60)

    output_path = os.path.join(
        folder_path,
        "chat_transcript.txt"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("\n".join(transcript))

    return output_path

# ----------------------------------
# GUI
# ----------------------------------

def select_folder():

    folder = filedialog.askdirectory()

    if not folder:
        return

    try:

        output_file = process_folder(folder)

        messagebox.showinfo(
            "Completed",
            f"Transcript saved to:\n\n{output_file}"
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            str(e)
        )

# ----------------------------------
# MAIN WINDOW
# ----------------------------------

root = tk.Tk()

root.title("Snapchat Screenshot Scanner")
root.geometry("450x200")
root.resizable(False, False)

label = tk.Label(
    root,
    text="Select a folder containing Snapchat screenshots",
    font=("Segoe UI", 10)
)

label.pack(pady=25)

btn = tk.Button(
    root,
    text="Select Folder",
    command=select_folder,
    width=20,
    height=2
)

btn.pack()

root.mainloop()
   
