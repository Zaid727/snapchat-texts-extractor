import os
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytesseract
from PIL import Image, ImageOps

# ----------------------------------
# TESSERACT LOCATION
# ----------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ----------------------------------
# OCR IMAGE
# ----------------------------------

def scan_image(image_path):
    image = Image.open(image_path)
    image = ImageOps.grayscale(image)

    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 6"
    )

    return text.strip()

# ----------------------------------
# WORKER FUNCTION
# ----------------------------------

def process_single(image_path, index, total):
    try:
        text = scan_image(image_path)
        return index, image_path, text, None
    except Exception as e:
        return index, image_path, "", str(e)

# ----------------------------------
# PROCESS FOLDER (WITH GPU-FRIENDLY PARALLEL CPU)
# ----------------------------------

def process_folder(folder_path, progress_var, status_label):

    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    image_files.sort()

    total_files = len(image_files)

    output_path = os.path.join(folder_path, "chat_transcript.txt")

    # ----------------------------------
    # OPEN FILE EARLY (CRASH SAFE MODE)
    # ----------------------------------
    f = open(output_path, "w", encoding="utf-8")

    f.write("=" * 60 + "\n")
    f.write("CHAT TRANSCRIPT\n")
    f.write("=" * 60 + "\n\n")

    start_time = time.time()

    max_workers = os.cpu_count() or 4

    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = [
            executor.submit(
                process_single,
                os.path.join(folder_path, img),
                i,
                total_files
            )
            for i, img in enumerate(image_files, start=1)
        ]

        for future in as_completed(futures):

            index, path, text, error = future.result()

            filename = os.path.basename(path)

            f.write(f"\n--- Screenshot {index}/{total_files}: {filename} ---\n\n")

            if error:
                f.write(f"[ERROR] {error}\n")
            else:
                f.write(text + "\n")

            f.write("-" * 60 + "\n")

            completed += 1

            # ----------------------------------
            # PROGRESS BAR UPDATE
            # ----------------------------------
            progress_var.set(int((completed / total_files) * 100))

            # ----------------------------------
            # ETA CALCULATION
            # ----------------------------------
            elapsed = time.time() - start_time
            avg = elapsed / completed
            remaining = (total_files - completed) * avg

            status_label.config(
                text=f"{completed}/{total_files} | "
                     f"ETA: {int(remaining//60)}m {int(remaining%60)}s"
            )

            root.update_idletasks()

    f.close()

    return output_path

# ----------------------------------
# GUI
# ----------------------------------

def select_folder():

    folder = filedialog.askdirectory()

    if not folder:
        return

    try:
        output_file = process_folder(folder, progress_var, status_label)

        messagebox.showinfo(
            "Completed",
            f"Saved to:\n\n{output_file}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ----------------------------------
# MAIN WINDOW
# ----------------------------------

root = tk.Tk()
root.title("Snapchat Screenshot Scanner")
root.geometry("500x260")
root.resizable(False, False)

label = tk.Label(
    root,
    text="Select a folder containing Snapchat screenshots",
    font=("Segoe UI", 10)
)
label.pack(pady=10)

btn = tk.Button(
    root,
    text="Select Folder",
    command=select_folder,
    width=20,
    height=2
)
btn.pack(pady=10)

# ----------------------------------
# PROGRESS BAR UI
# ----------------------------------

progress_var = tk.IntVar()

progress_bar = ttk.Progressbar(
    root,
    length=350,
    mode="determinate",
    variable=progress_var,
    maximum=100
)
progress_bar.pack(pady=10)

status_label = tk.Label(
    root,
    text="Waiting...",
    font=("Segoe UI", 9)
)
status_label.pack(pady=5)

root.mainloop()
