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
import math


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def is_between(a, c, b):
    return math.isclose(distance(a, c) + distance(c, b), distance(a, b))


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


        self.fig = plt.figure()#(dpi=100) # figsize=(5, 4),
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
        self.segments = None
        self.data = None
        self.holes = None
        self.labels = False
        self.number_triangles = False

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
            self.area = self.data.get('area')
            self.holes = self.data.get('holes')
            self.points = self.data['points']
            self.labels = True if self.data.get('labels') else False
            self.number_triangles = True if self.data.get('number_triangles') else False

            # display data in the text field
            self._print_info(self.data)


            # get elements
            self.segments = [[i, (i+1) % len(self.points)] for i in range(len(self.points))]

            # declare dict that 'triangle' library require for triangulation
            self.A = {
                'vertices': np.array([(point['x'], point['y']) for point in self.data['points']]),
                'segments': np.array(self.segments)
            }

            if self.labels:
                self.A['labels'] = self.labels

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
            f'pq{self.angle if self.angle else ""}a{self.area if self.area else ""}'
        )

        if self.labels:
            self.B['labels'] = self.labels
        if self.number_triangles:
            self.B['number_triangles'] = True

        raw_info = {key: value.tolist() if isinstance(value, np.ndarray) else value for key,value in self.B.items()}

        info = {
            'CT': raw_info['vertices'],
            'NT':raw_info['triangles'],
            'NTG':[self._boundary_segments(segment, raw_info['vertices']) for segment in self.segments]
        }

        # print('-'*100)
        # print([self._boundary_segments(segment, raw_info['vertices']) for segment in self.segments])
        # print('-' * 100)

        self._print_info(info) #json.dumps(b_info)
        plot.plot(plt, self.B)
        self.canvas.draw()

    def _boundary_segments(self, parent_segment, vertices):
        a, b = vertices[parent_segment[0]][0], vertices[parent_segment[1]][0]
        c, d = vertices[parent_segment[0]][1], vertices[parent_segment[1]][1]
        a, b = (a, b) if a<b else (b, a)
        c, d = (c, d) if c<d else (d, c)
        suspicious_points = []
        for i in range(len(vertices)):
            if a <= vertices[i][0] <= b and c <= vertices[i][1] <= d:
                suspicious_points.append(i)

        segment_points = []
        for i in suspicious_points:
            if is_between(vertices[parent_segment[0]], vertices[i],vertices[parent_segment[1]]):
                segment_points.append(i)
        return segment_points







    def compare(self):
        plot.compare(plt, self.A, self.B)
        self.canvas.draw()

    def run(self):
        Tk.mainloop()


app = Application()
app.run()


