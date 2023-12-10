import customtkinter
import tkinter

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("1080x720")
app.title("Shot Detection")

tabView = customtkinter.CTkTabview(app)
tabView.pack()
tabView.add("Load Video")
tabView.add("Cut Scenes")
tabView.add("Gradual Transitions")

app.mainloop()
