import tkinter as tk
from ui import Ui


# Create class that extends Tk()
class Application(tk.Tk):
    def __init__(self):
        # Call parent constructor
        super().__init__()

        # Set Window Title and Size
        self.title('Easy Deploy')
        self.geometry('300x700')

        # Initialize UI and set it to variable for
        # easy property access.
        Ui(self)


app = Application()
app.mainloop()
