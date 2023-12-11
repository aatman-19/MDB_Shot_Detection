import customtkinter as ctk
from PIL import Image
import os


def button_event(path):
    print(f"button pressed at {path}")


def create_image_grid(frame, row, col, image_path, callback):
    img = ctk.CTkImage(dark_image=Image.open(image_path), size=(200, 200))
    label = ctk.CTkButton(frame, image=img, text=image_path[-13:], compound="top", command=lambda: callback(image_path))
    label.grid(row=row, column=col, padx=5, pady=5)


cut_img_folder = "outputs/cuts/"
transition_img_folder = "outputs/transitions/"
cut_imgs = [f for f in os.listdir(cut_img_folder) if f.endswith('.jpg')]
cut_imgs = [os.path.join(cut_img_folder, f) for f in cut_imgs]
transition_imgs = [f for f in os.listdir(transition_img_folder) if f.endswith('.jpg')]
transition_imgs = [os.path.join(transition_img_folder, f) for f in transition_imgs]

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

sc1 = ctk.CTkScrollableFrame(tabView.tab("Cut Scenes"),height=700, width=700)
sc2 = ctk.CTkScrollableFrame(tabView.tab("Gradual Transitions"), height=700, width= 700)
sc1.pack()
sc2.pack()

num_columns = 3

# Create image labels and arrange them in a grid
for i, p in enumerate(cut_imgs):
    row = i // num_columns
    col = i % num_columns
    create_image_grid(sc1, row, col, p, button_event)

for i, p in enumerate(transition_imgs):
    row = i // num_columns
    col = i % num_columns
    create_image_grid(sc2, row, col, p, button_event)

app.mainloop()
