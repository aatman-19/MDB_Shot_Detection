import customtkinter as ctk
from VideoShot import VideoShot
from tkinter import filedialog
from threading import Thread
import cv2
from PIL import Image
import os

VID_PATH = None
OBJ = None
cut_imgs = None
transition_imgs = None


# Load the video file & Init the OBJ

def load_object(video_path):
    global OBJ
    OBJ = VideoShot(video_path)


def load_video(p_l, button):
    global VID_PATH, OBJ
    video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4;*.avi;*.mpg")])
    VID_PATH = video_path
    print(f"Selected Video File: {VID_PATH}")
    # Initialize the VideoShot Object
    button.configure(state="disabled")
    Thread(target=load_object(video_path)).start()
    button.configure(state="normal")
    p_l.configure(text="Elements loaded, can view in alternate tabs!!", text_color="yellow")
    load_files()


def load_files():
    global cut_imgs, transition_imgs
    cut_img_folder = "outputs/cuts/"
    transition_img_folder = "outputs/transitions/"
    cut_imgs = [f for f in os.listdir(cut_img_folder) if f.endswith('.jpg')]
    cut_imgs = [os.path.join(cut_img_folder, f) for f in cut_imgs]
    transition_imgs = [f for f in os.listdir(transition_img_folder) if f.endswith('.jpg')]
    transition_imgs = [os.path.join(transition_img_folder, f) for f in transition_imgs]
    num_columns = 3
    for i, p in enumerate(cut_imgs):
        row = i // num_columns
        col = i % num_columns
        create_image_grid(sc1, row, col, p, open_shot_window)

    for i, p in enumerate(transition_imgs):
        row = i // num_columns
        col = i % num_columns
        create_image_grid(sc2, row, col, p, open_shot_window)


def show_video_shot(frame, path):
    video_frame = ctk.CTkToplevel(frame)
    video_frame.title(f"Shot from frame {path[-8:-4]}")
    video_frame.attributes("-topmost",True)
    img = ctk.CTkImage(dark_image=Image.open(path), size=(500, 500))
    label = ctk.CTkLabel(video_frame, image=img, text=path[-13:-4], compound="top")
    label.pack()
    start_frame = int(path[-8:-4])

    if OBJ:
        end_frame = OBJ.get_nearest_end_frame(start_frame, OBJ.cuts, OBJ.transitions)
    else:
        end_frame = start_frame # function call to get_nearest_end_frame

    if VID_PATH:
        video_path = VID_PATH
    else:
        video_path = '20020924_juve_dk_02a.mpg'

    play_button = ctk.CTkButton(video_frame, text="Play Shot",
                                command=lambda: play_video(label, start_frame, end_frame, video_path))
    play_button.pack()


def play_video(parent_label, start_frame, end_frame, video_path):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    def update_label():
        nonlocal cap
        ret, frame = cap.read()
        if ret and start_frame <= cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ctk.CTkImage(dark_image=img, size=(500, 500))
            parent_label.configure(image=img)
            parent_label.image = img
            parent_label.after(30, update_label)
        else:
            # Video playback is finished or an error occurred
            cap.release()

    update_label()


def open_shot_window(frame, path):
    show_video_shot(frame, path)
    print(f"shot window opened for [{path}]")


def create_image_grid(frame, row, col, image_path, callback):
    img = ctk.CTkImage(dark_image=Image.open(image_path), size=(200, 200))
    label = ctk.CTkButton(frame, image=img, text=image_path[-13:], compound="top",
                          command=lambda: callback(frame, image_path))
    label.grid(row=row, column=col, padx=5, pady=5)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1080x1080")
app.title("Shot Detection")

tabView = ctk.CTkTabview(app, height=750, width=700)
tabView.pack()
tabView.add("Load Video")
tabView.add("Cut Scenes")
tabView.add("Gradual Transitions")
tabView.set('Load Video')

# Load Video Tab
p_label = ctk.CTkLabel(tabView.tab("Load Video"),
                       width=100, height=50,
                       text_color="white",
                       text="Please wait 10 secs after selecting video")

p_label.pack(padx=50, pady=50)
Load_vid = ctk.CTkButton(tabView.tab("Load Video"),
                         text="Select the video file",
                         height=50,
                         width=100,
                         command=lambda: load_video(p_label, Load_vid))

Load_vid.pack(padx=50, pady=50)

# Cut & Transition Tabs
sc1 = ctk.CTkScrollableFrame(tabView.tab("Cut Scenes"), height=700, width=700)
sc2 = ctk.CTkScrollableFrame(tabView.tab("Gradual Transitions"), height=700, width=700)
sc1.pack()
sc2.pack()


app.mainloop()
