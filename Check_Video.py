import csv
import os
import requests
from moviepy.editor import VideoFileClip
import tkinter as tk
from tkinter import ttk, filedialog
import warnings

# Function to open file dialog and get the file path
def get_file_path():
    file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    return file_path

# Function to open folder dialog and get the folder path
def get_folder_path():
    folder_path = filedialog.askdirectory(title="Select Folder")
    return folder_path

# Read the video URLs from the input CSV file
input_csv_path = get_file_path()

with open(input_csv_path, 'r') as f:
    reader = csv.reader(f)
    video_urls = list(reader)

# Ask for folder location to save output.csv and faulty_urls.csv
output_folder_path = get_folder_path()

# Prepare the output data
output_data = [['Video URL', 'Quality', 'Orientation', 'Duration (s)', 'File Size (MB)', 'Aspect Ratio']]
faulty_urls = [['Faulty URL']]

# Function to print a simple text progress bar
def print_progress(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

# Function to update the progress bar
def update_progress_bar(progress_var, current, total):
    progress = int(100 * (current / float(total)))
    progress_var.set(progress)

# Function to create and show the progress bar popup
def show_progress_popup(total):
    progress_popup = tk.Toplevel()
    progress_popup.title("Progress")

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_popup, variable=progress_var, length=1500, mode='determinate')
    progress_bar.grid(row=0, column=0, padx=10, pady=10)

    for i, url in enumerate(video_urls):
        try:
            # Download the video file
            video_file = requests.get(url[0])

            # Save the video file
            with open('temp.mp4', 'wb') as f:
                f.write(video_file.content)

            # Load the video file
            video = VideoFileClip('temp.mp4')

            # Get the video quality
            quality = f"{video.size[1]}p"

            # Check if the video is in portrait mode
            orientation = 'Portrait' if video.size[0] < video.size[1] else 'Landscape'

            # Get the video duration in seconds
            duration = round(video.duration, 2)

            # Get the video file size in megabytes
            file_size = round(os.path.getsize('temp.mp4') / (1024 * 1024), 2)

            # Get the aspect ratio
            aspect_ratio = round(video.size[0] / video.size[1], 2)

            # Add the data to the output
            output_data.append([url[0], quality, orientation, duration, file_size, aspect_ratio])

            # Close the VideoFileClip to release resources
            video.close()

            # Update the progress bar in the popup
            update_progress_bar(progress_var, i + 1, total)
            progress_popup.update()
            progress_popup.update_idletasks()

        except Exception as e:
            # If there's an error, add the URL to the faulty URLs list
            faulty_urls.append([url[0]])

    # Write the output data to the output CSV file
    output_csv_path = os.path.join(output_folder_path, 'output.csv')
    with open(output_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(output_data)

    # Write the faulty URLs to the faulty URLs CSV file
    faulty_urls_csv_path = os.path.join(output_folder_path, 'faulty_urls.csv')
    with open(faulty_urls_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(faulty_urls)

    # Clean up: Delete the temporary 'temp.mp4' file
    temp_file_path = 'temp.mp4'
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    # Close the progress bar popup when done
    progress_popup.destroy()

# Show the progress bar popup
show_progress_popup(len(video_urls))

# Suppress the warning about the subprocess termination
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed file")
