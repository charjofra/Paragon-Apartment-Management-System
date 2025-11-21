from customtkinter import *

root = CTk()

def initialise(SCREEN_WIDTH, SCREEN_HEIGHT):
    
    root.geometry(f"{int(SCREEN_WIDTH)}x{int(SCREEN_HEIGHT)}")
    root.after(1, root.wm_state, "zoomed")
    root.title("Paragon Apartment Management System")
    set_appearance_mode("dark")

    root.mainloop()