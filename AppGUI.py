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


import numpy as np
import matplotlib.pyplot as plt
import pprint
import plot
from helpers import read_json
from DelaunayTriangulation import DelaunayTriangulation


class AppGUI:
    def __init__(self):
        # ===============GUI items initializarion===============
        self.root = Tk.Tk()
        self.root.wm_title("MathsPhysics")

        self.text_frame = Tk.Frame(master=self.root)
        self.text = Tk.Text(self.text_frame)
        self.text_scrollbar = Tk.Scrollbar(self.text_frame)
        self.text.config(yscrollcommand=self.text_scrollbar.set)
        self.text.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.text_scrollbar.config(command=self.text.yview)
        self.text_scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)

        self.fig = plt.figure(figsize=(5, 5))#(dpi=100) # figsize=(5, 4),
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1) # canvas.draw()
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.text_frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.menubar = Tk.Menu(self.root)
        self.filemenu = Tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load data", command=self._load_data)
        self.filemenu.add_command(label="Triangulate", command=self._triangulate)
        self.filemenu.add_command(label="Compare", command=self._compare)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self._quit)
        self.menubar.add_cascade(label="Menu", menu=self.filemenu)
        self.root.config(menu=self.menubar)
        # ============================================================

        self.delaunay_triangulation = None

    def _load_data(self):
        # open file dialog
        filepath = Tk.filedialog.askopenfilename(title="Select file", filetypes=(("json files", "*.json"), ("all files", "*.*")))
        if filepath is not None:
            self.fig.clear()  # clear everything that was drawn before

            data = read_json(filepath)
            self.delaunay_triangulation = DelaunayTriangulation(**data)

            # display data in the text field
            self._print_info(data)

            # plot the domain
            plot.plot(plt, self.delaunay_triangulation.triangulation_params)
            self.canvas.draw() # redraw the canvas

    def _triangulate(self):
        self.delaunay_triangulation.triangulate()
        self._print_info(self.delaunay_triangulation.triangulated_info)
        plot.plot(plt, self.delaunay_triangulation.triangulated)
        self.canvas.draw()

    def _print_info(self, data):
        self.text.delete('1.0', Tk.END)
        pretty_data = pprint.pformat(data)  # pretty format data before printing
        self.text.insert(Tk.END, pretty_data)

    def _quit(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def _compare(self):
        plot.compare(plt, self.delaunay_triangulation.triangulation_params, self.delaunay_triangulation.triangulated)
        self.canvas.draw()

    def run(self):
        Tk.mainloop()
