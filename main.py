"""
===============
Embedding In Tk
===============

"""

from six.moves import tkinter as Tk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2TkAgg)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import tkinter as Tk
from tkinter import filedialog, messagebox


import json
import numpy as np
import matplotlib.pyplot as plt
import pprint
import triangle
import plot


class Application:
    def __init__(self):
        self.root = Tk.Tk()
        self.root.wm_title("MathsPhysics")

        self.text_frame = Tk.Frame(master=self.root)
        self.text = Tk.Text(self.text_frame)
        self.text_scrollbar = Tk.Scrollbar(self.text_frame)
        self.text.config(yscrollcommand=self.text_scrollbar.set)
        self.text.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.text_scrollbar.config(command=self.text.yview)
        self.text_scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)


        self.fig = plt.figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1) # canvas.draw()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.text_frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.menubar = Tk.Menu(self.root)
        self.filemenu = Tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load data", command=self.load_data)
        self.filemenu.add_command(label="Triangulate", command=self.triangulate)
        self.filemenu.add_command(label="Compare", command=self.compare)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self._quit)
        self.menubar.add_cascade(label="Menu", menu=self.filemenu)
        self.root.config(menu=self.menubar)

        self.A = None
        self.B = None
        self.filepath = None
        self.angle = None
        self.area = None
        self.points = None
        self.boundary_segments = None
        self.data = None
        self.holes = None

    def read_data(self):
        with open(self.filepath) as f:
            return json.load(f)

    def load_data(self):
        # open file dialog
        self.filepath = Tk.filedialog.askopenfilename(title="Select file", filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if self.filepath is not None:
            self.fig.clear()  # clear everything that was drawn before

            # read data
            self.data = self.read_data()
            self.angle = self.data.get('angle')
            self.angle = 0 if self.angle > 17.5 else self.angle  # check if angle is bad for triangulation algorithm
            self.area = self.data.get('area')
            self.holes = self.data.get('holes')
            self.points = self.data['points']

            # display data in the text field
            self._print_info(self.data)


            # get boundary elements
            self.boundary_segments = [[i, (i+1) % len(self.points)] for i in range(len(self.points))]

            # declare dict that 'triangle' library require for triangulation
            self.A = {
                'vertices': np.array([(point['x'], point['y']) for point in self.data['points']]),
                'segments': np.array(self.boundary_segments)
            }

            # if holes are specified add them to dict
            if self.holes:
                self.A['holes'] = np.array(self.holes)

            # plot the domain
            plot.plot(plt, self.A)
            self.canvas.draw() # redraw the canvas

    def _print_info(self, data):
        self.text.delete('1.0', Tk.END)
        pretty_data = pprint.pformat(data)  # pretty format data before printing
        self.text.insert(Tk.END, pretty_data)

    def _quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def triangulate(self):
        # triangulate domain

        self.B = triangle.triangulate(
            self.A,
            f'pq{self.angle if self.angle else ""}a{self.area if self.area else ""}')
        b_info = {key: value.tolist() if isinstance(value, np.ndarray) else value for key,value in self.B.items()}
        self._print_info(json.dumps(b_info))
        plot.plot(plt, self.B)
        self.canvas.draw()

    def compare(self):
        plot.compare(plt, self.A, self.B)
        self.canvas.draw()

    def run(self):
        Tk.mainloop()


app = Application()
app.run()


