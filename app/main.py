import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory
from pytube import YouTube
from time import sleep
from threading import Thread,Lock

class UI(tk.Frame):

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent 
        self.init_ui()
        self.lock = Lock()
        self.download_threads = []
        self.index_downloading = 0

    def init_ui(self):
        self.parent.title("Youtube Downloader")
        self.main_frame = tk.Frame(self.parent,padx=10,pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # url entry text
        self.url_label = tk.Label(self.main_frame,text="Write a Youtube Url: ")
        self.url_label.pack()
        self.url_label2 = tk.Label(self.main_frame,text="'https://www.youtube.com/...' or 'https://youtube.com/... or 'https://youtu.be'")
        self.url_label2.pack()
        
        style = ttk.Style()
        style.configure(
            "MyEntry.TEntry",
            padding=10
        )
        self.url_text = ttk.Entry(self.main_frame,style="MyEntry.TEntry")
        self.url_text.pack(fill=tk.X)
        self.url_text.focus_set()
        # url add/delete buttons
        self.buttons_add_Frame = self.init_ui_add_delete_buttons()
        self.buttons_add_Frame.pack()
        # url list
        self.urls_list = tk.Listbox(self.main_frame,width=50)
        self.urls_list.pack(fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.urls_list)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.urls_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.urls_list.yview)
        # Download Button
        self.download_button_frame = tk.Frame(self.parent,padx=10,pady=5)
        self.download_button_frame.pack()
        self.download_button = tk.Button(self.download_button_frame, text="Download Videos",
                                    command=self.download_all_videos,
                                    padx=10, pady=10)
                                    #padx=10, pady=10, bg="#c1f0b6")
        self.download_button.pack()
        # Quit
        self.quit_button_frame = tk.Frame(self.parent,padx=10,pady=5)
        self.quit_button_frame.pack()
        self.quit_button = tk.Button(self.quit_button_frame, text="Quit", command=self.quit_app, padx=5)
        self.quit_button.pack()
    
    def init_ui_add_delete_buttons(self):
        buttons_add_Frame = tk.Frame(self.main_frame,padx=10,pady=10)
        self.add_url_button = tk.Button(buttons_add_Frame, text="Add URL", command=self.add_URL, padx=10)
        self.add_url_button.grid(row=0,column=0,sticky = tk.W)  
        self.remove_last_url_button = tk.Button(buttons_add_Frame, text="Remove Last", command=self.remove_last_URL, padx=10)
        self.remove_last_url_button.grid(row=0,column=1,sticky = tk.W) 
        self.remove_selected_url_button = tk.Button(buttons_add_Frame, text="Remove Selected", command=self.remove_selected_URL, padx=10)
        self.remove_selected_url_button.grid(row=0,column=2,sticky = tk.W) 
        self.remove_all_url_button = tk.Button(buttons_add_Frame, text="Remove All", command=self.remove_all_URL, padx=10)
        self.remove_all_url_button.grid(row=0,column=3,sticky = tk.W)  
        return buttons_add_Frame
    
    def add_URL(self):
        url = self.url_text.get()
        if self.valid_URL(url):
            self.urls_list.insert(tk.END,self.url_text.get())
            self.url_text.delete(0, tk.END)
    
    def remove_last_URL(self):
        try:
            self.urls_list.delete(tk.END)
        except:
            pass

    def remove_selected_URL(self):
        try:
            self.urls_list.delete(self.urls_list.curselection())
        except:
            pass
    
    def remove_all_URL(self):
        try:
            self.urls_list.delete(0,tk.END)
        except:
            pass

    def valid_URL(self,URL:str):
        if not (URL.startswith("https://www.youtube.com/") or URL.startswith("https://youtube.com") or URL.startswith("https://youtu.be")):
            messagebox.showwarning(title=None, message="A valid YouTube Video URL format is required")
            return False
        return True
    
    def activate_buttons(self):
        self.download_button["state"] = "active"
        self.add_url_button["state"] = "active"
        self.remove_last_url_button["state"] = "active"
        self.remove_selected_url_button["state"] = "active"
        self.remove_all_url_button["state"] = "active"

    def deactivate_buttons(self):
        self.download_button["state"] = "disabled"
        self.add_url_button["state"] = "disabled"
        self.remove_last_url_button["state"] = "disabled"
        self.remove_selected_url_button["state"] = "disabled" 
        self.remove_all_url_button["state"]= "disabled"

    def download_all_videos(self):
        self.deactivate_buttons()
        self.error_counter = 0
        if len(self.urls_list.get(0,tk.END)):
            directory = askdirectory()
            for i,url in enumerate(self.urls_list.get(0,tk.END)):
                self.urls_list.delete(i)
                self.urls_list.insert(i,f"Waiting... \t 0% \t {url}")
                new_Thread = Thread(target=self.download_video, args=(directory,url,i))
                self.download_threads.append(new_Thread)
                #self.download_video(directory,url,i)
            for th in self.download_threads:
                th.start()
        else:
            messagebox.showwarning(title=None, message="First Add a YouTube Video URL")
            return False

    def download_video(self,directory,url,index):
        with self.lock:
            self.url_downloading = url
            self.index_downloading = index
            try:
                # Crear objeto YouTube
                yt = YouTube(url,
                            on_progress_callback=self.on_progress,
                            on_complete_callback=self.on_complete)
                video = yt.streams.get_highest_resolution()
                #video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                video.download(directory)
            except Exception as e:
                self.error_counter +=1
                self.urls_list.delete(self.index_downloading)
                self.urls_list.insert(self.index_downloading,f"Error {self.url_downloading}") 
                self.urls_list.itemconfig(self.index_downloading, foreground="red")
                print(e)
    
    def on_progress(self,stream, datachunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        print(percentage_of_completion)
        self.update_url_text(percentage_of_completion)
    
    def update_url_text(self,percentage_of_completion):
        self.urls_list.delete(self.index_downloading)
        self.urls_list.insert(self.index_downloading,f"Downloading... \t {percentage_of_completion:.0f}% \t {self.url_downloading}") 

    def on_complete(self,stream, path):
        self.urls_list.delete(self.index_downloading)
        self.urls_list.insert(self.index_downloading,f"Downloaded \t 100% \t {self.url_downloading}") 
        self.urls_list.itemconfig(self.index_downloading, foreground="green")
        if (self.index_downloading + 1) == len(self.urls_list.get(0,tk.END)):
            sleep(1)
            if self.error_counter == 0:
                messagebox.showinfo(title=None, message="Downloading Completed")
            else:
                messagebox.showwarning(title=None, message="Downloading Completed with Errors")
            self.remove_all_URL()
            self.activate_buttons()

    def quit_app(self):
        self.quit()
        self.destroy()

if __name__ == "__main__": 
    ROOT = tk.Tk()
    ROOT.geometry("600x500") 
    # Fijamos el tamaño mínimo de la ventana en 300x200
    ROOT.minsize(600, 500)
    APP = UI(parent=ROOT) 
    APP.mainloop() 
    ROOT.destroy()
