# Needed for making HTTP requests
import requests
# Needed for get downloaded JSON info from the API
import json
# Needed for getting all the downloaded files in the temporary directory
import glob
# Needed for packing all the images in a PDF file
from PIL import Image
# Needed for asking the target directory 
from tkinter import filedialog
# Needed for Tk().withdraw()
from tkinter import Tk
# Needed for creating a temporary directory
import tempfile
# Rich library
from rich.console import Console
from rich.progress import Progress
# Needed for getting the current os
from os import system, name 
# Needed for sys.exit()
import sys

def clear(): 
    # Windows
    if name == 'nt': 
        _ = system('cls') 
  
    # Mac and Linux 
    else: 
        _ = system('clear') 

if __name__ == "__main__":
    console = Console()

    # Clear the console
    clear()

    console.rule("MangaDex Downloader")
    console.print("[cyan1 bold]Created by Michele Lorusso (github.com/michibros/)[/cyan1 bold]", justify="center")
    console.print("\n[wheat1]Need help?[/wheat1] Check the README.md file of the repository.")
    while True:
        console.print("\n[cyan1 bold]Enter the ID of the manga you want to download: [/cyan1 bold]", end="")
        selected_manga = input()

        try:
            # Requesting the selected manga info to the Mangadex API
            r = requests.get(f"https://mangadex.org/api/v2/manga/{selected_manga}/chapters")
        except:
            # There is no internet connection
            console.print("[bold red]An error occurred.[/bold red] [red]Check your internet connection.[/red]")
            sys.exit()
        if r.status_code == 404:
            # The resource doesn't exist
            console.print("[bold red]An error occurred.[/bold red] [red]The selected manga doesn't exist.[/red]")
        elif r.status_code != 200:
            # The server returned some other error code
            console.print(f"[bold red]An error occurred.[/bold red] [red]The server responded with code {r.status_code}.[/red]")
        else:
            # The server returned code 200, it is safe to proceed
            break

    # Turn the information in a json file, then access the chapter list of the manga...
    mangaInfo = r.json()
    chapter_list = mangaInfo["data"]["chapters"]

    chaptersObject = [key for key in chapter_list]
    currentChapter = 0
    # ...English only (for now)
    unique_en_chapters = [chapter for chapter in chapter_list if chapter["language"] == "gb"]

    number_of_chapter = 1
    try:
        # Try to get the manga title from the last chapter avaiable
        mangaTitle = unique_en_chapters[-1]["mangaTitle"]
    except:
        # We didn't find any english chapter or any chapter at all, stop everything
        console.print("[bold red]An error occurred.[/bold red] [red]The selected manga doesn't have any downloadable chapter.[/red]")
        sys.exit()
    console.print(f"[cyan1 bold]Selected manga:[/cyan1 bold] {mangaTitle}")
    console.print("[cyan1 bold]Download mode:[/cyan1 bold] ([cyan]S[/cyan])ingle chapter, ([cyan]M[/cyan])ultiple chapters: ", end="")
    download_mode = input("").lower()

    # I realize that a do-while loop in Python wouldn't be that bad
    while download_mode != "s" and download_mode != "m":
        console.print("[bold red]Invalid input.[/bold red]")
        console.print("[cyan1 bold]Download mode:[/cyan1 bold] ([cyan]S[/cyan])ingle chapter, ([cyan]M[/cyan])ultiple chapters: ", end="")
        download_mode = input("").lower()

    if download_mode == "s":
        console.print("[dark_olive_green2 bold]Enter the chapter you want to download:[/dark_olive_green2 bold] ", end="")
        selected_chapter = input("")
        number_of_chapter = 1

    elif download_mode == "m":
        console.print("[dark_olive_green2 bold]Enter the chapter you want the batch download to start from:[/dark_olive_green2 bold] ", end="")
        selected_chapter = input("")
        console.print("[dark_olive_green2 bold]Enter the number of chapters you want to download:[/dark_olive_green2 bold] ", end="")
        number_of_chapter = eval(input(""))

    # Hide the blank Tk window that spawns when calling any Tkinter-relative function
    Tk().withdraw()
    path_to_save_to = filedialog.askdirectory()
    
    selected_chapter_id = None
    chapter_title = None

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as directory:
        # For every chapter in the batch download
        for i in range(number_of_chapter):
            # Check if desidered chapter exists
            for chap in unique_en_chapters:
                if (chap["chapter"]) == selected_chapter:
                    chapter_title = chap["title"]
                    selected_chapter_id = chap["hash"]
            # Return error if not
            if selected_chapter_id == None:
                console.print("[bold red]An error occurred.[/bold red] [red]The selected chapter doesn't exist or it cannot be downloaded.[/red]")
                sys.exit()

            try:
                r = requests.get(f"https://mangadex.org/api/v2/chapter/{selected_chapter_id}")
                chapter_info = r.json()
            except:
                console.print("[bold red]An error occurred.[/bold red] [red]Check your internet connection.[/red]")
                sys.exit()

            curr_page = 1
            images = []

            # I love Rich's progress bars
            with Progress(transient=True) as progress:
                download = progress.add_task(f"[cyan1 bold]Downloading:[/cyan1 bold] Chapter {selected_chapter}, {chapter_title}", total=len(chapter_info["data"]["pages"]))
                # For every page
                for page in chapter_info["data"]["pages"]:
                    try:
                        # Try do download it
                        r = requests.get(f"{chapter_info['data']['server']}{selected_chapter_id}/{page}")
                    except:
                        console.print("[bold red]An error occurred.[/bold red] [red]Check your internet connection.[/red]")
                        sys.exit()
                    if r.status_code != 200:
                        r = requests.get(f"https://mangadex.org/data/{selected_chapter_id}/{page}")
                    # Save it in the temporary directory
                    with open(f"{directory}/{curr_page}.download", "wb") as file:
                        file.write(r.content)
                        file.close()
                    # Append the downloaded image to the final PDF
                    images.append(Image.open(f"{directory}/{curr_page}.download").convert("RGB"))
                    curr_page += 1
                    # Update the progress bar
                    progress.update(download, advance=1)
                # Save the final PDF
                images[0].save(f"{path_to_save_to}/{selected_chapter} - {chapter_title}.pdf", save_all=True, append_images=images[1:])
            # Chapter downloaded!
            console.print(f"[cyan1 bold]Downloaded successfully:[/cyan1 bold] Chapter {selected_chapter}, {chapter_title}")
            # Go to the next chapter
            selected_chapter = str(eval(selected_chapter) + 1)
    



