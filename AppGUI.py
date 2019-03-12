"""
===============
Embedding In Tk
===============

"""
import json
import math

from six.moves import tkinter as Tk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2TkAgg)
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import tkinter as Tk
from tkinter import filedialog, messagebox


import numpy as np
import matplotlib.pyplot as plt
import pprint
import plot
from helpers import read_json
from DelaunayTriangulation import DelaunayTriangulation
from fem_solver import FemSolver
from tester import Tester
from mpl_toolkits.mplot3d.art3d import Poly3DCollection



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
        self.filemenu.add_command(label="Set conditions", command=self._ask_conds)
        self.filemenu.add_command(label="Solve", command=self._solve)  # Do nothing
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self._quit)
        self.menubar.add_cascade(label="Menu", menu=self.filemenu)
        self.root.config(menu=self.menubar)

        # conditions window
        self.cond_window = None
        # ============================================================

        self.delaunay_triangulation = None
        self.entries = None
        self.fem_solver = None
        self.solver = None
        self.solution = None
        self.x_vertices = None
        self.y_vertices = None

        # =============================================================
        self.tester = None

    def _solve(self):
        self.solver = FemSolver(self.delaunay_triangulation.triangulated_info, self.entries)
        self.solver.prepare_matrices()
        self.solver.form_SofLE()
        print('='*100)
        pprint.pprint(self.solver.element_matrices)
        print('-' * 100)
        pprint.pprint(self.solver.boundary_matrices)
        print('-' * 100)
        #pprint.pprint(self.solver.K)
        # print('\n'.join(['\t\t  '.join([str(cell) for cell in row]) for row in self.solver.K.round(3)]))
        # print('-' * 100)
        # pprint.pprint(self.solver.F)
        # print('-' * 100)
        self.solution = np.linalg.solve(self.solver.K, self.solver.F)
        print('-' * 100)
        print("FEM solution : ")
        pprint.pprint(self.solution)

        self.tester = Tester(self.solution, self.entries, self.delaunay_triangulation.triangulated_info)
        print("L2:")
        print("absolute error: ", self.tester.get_abs_error_L2())
        print("relative error: ", self.tester.get_relative_error_L2())


        filename = 'matrices.json'
        data = {}
        for key in self.solver.element_matrices:
            inner_data = {}
            for subkey in self.solver.element_matrices[key]:
                inner_data[subkey] = self.solver.element_matrices[key][subkey].tolist()
            data[key] = inner_data

        self._write(filename, data)
        self._3Dplot()

    def getRandomColor(self):
        return (np.random.choice(range(2, 9), size=3) / 10)


    def _3Dplot(self):
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        tmp = np.array([[0,0,0]])
        for idx, tri in enumerate(self.solver.triangulated_info['NT']):
            triangle = self.solver.triangulated_info['NT'][idx]
            verts = np.array([
                [self.solver.triangulated_info['CT'][triangle[0]][0], self.solver.triangulated_info['CT'][triangle[0]][1], self.solution[triangle[0], 0]],
                [self.solver.triangulated_info['CT'][triangle[1]][0], self.solver.triangulated_info['CT'][triangle[1]][1], self.solution[triangle[1], 0]],
                [self.solver.triangulated_info['CT'][triangle[2]][0],self.solver.triangulated_info['CT'][triangle[2]][1], self.solution[triangle[2], 0]]

            ])
            ax.add_collection3d(Poly3DCollection([verts.tolist()], facecolors=np.append(self.getRandomColor(),0.25), linewidths=1, edgecolor="k"))
            tmp = np.vstack((tmp, verts))

        ax.scatter(tmp[1:, 0], tmp[1:, 1], tmp[1:, 2], c='k', marker='o')

        ax.set_xlim3d(np.min(tmp[:, 0]), np.max(tmp[:, 0]))
        ax.set_ylim3d(np.min(tmp[:, 1]), np.max(tmp[:, 1]))
        ax.set_zlim3d(np.min(tmp[:, 2])-1, np.max(tmp[:, 2])+1)
        plt.show()

        # self.x_vertices = [point[0] for point in self.delaunay_triangulation.triangulated_info['CT']]
        # self.y_vertices = [point[1] for point in self.delaunay_triangulation.triangulated_info['CT']]
        #
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        #
        # self.x_vertices, self.y_vertices = np.meshgrid(self.x_vertices, self.y_vertices)
        # z = np.array(self.solution)
        #
        # ax.plot_surface(self.x_vertices, self.y_vertices, z)
        # plt.show()


    def _write(self, filename, data):
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def _ask_conds(self):
        # create a child window
        self.cond_window = Tk.Toplevel()
        self.entries = self._makeform()
        Tk.Button(self.cond_window, text="Apply", command=self._consume_entries).pack()

    def _consume_entries(self):
        fields = ['Beta', 'Sigma', 'Uc']
        for key in self.entries:
            if key in self.delaunay_triangulation.triangulated_info['NTG']:
                for sub_key in fields:
                    self.entries[key][sub_key] = float(self.entries[key][sub_key].get())
            else:
                self.entries[key] = float(self.entries[key].get())
        pprint.pprint(self.entries)
        self.cond_window.destroy()

    def _makeform(self):
        entries = {}

        a_row = Tk.Frame(self.cond_window)
        Tk.Label(a_row, width=22, text='a11 :', anchor='w').pack(side=Tk.LEFT)
        a11_ent = Tk.Entry(a_row)
        a11_ent.insert(0, "1")
        a11_ent.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
        Tk.Label(a_row, width=22, text='a22 :', anchor='w').pack(side=Tk.LEFT)
        a22_ent = Tk.Entry(a_row)
        a22_ent.insert(0, "1")
        a22_ent.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
        a_row.pack(side=Tk.TOP, fill=Tk.X, padx=5, pady=5)

        entries['a11'] = a11_ent
        entries['a22'] = a22_ent

        fd_row = Tk.Frame(self.cond_window)
        Tk.Label(fd_row, width=22, text='f :', anchor='w').pack(side=Tk.LEFT)
        f_ent = Tk.Entry(fd_row)
        f_ent.insert(0, "1")
        f_ent.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
        Tk.Label(fd_row, width=22, text='d :', anchor='w').pack(side=Tk.LEFT)
        d_ent = Tk.Entry(fd_row)
        d_ent.insert(0, "1")
        d_ent.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
        fd_row.pack(side=Tk.TOP, fill=Tk.X, padx=5, pady=5)

        entries['f'] = f_ent
        entries['d'] = d_ent

        row = Tk.Frame(self.cond_window)
        fields = ['Beta', 'Sigma', 'Uc']
        Tk.Label(row, width=22, text='Boundaries', anchor='w').pack(side=Tk.LEFT)
        Tk.Label(row, width=22, text=fields[0], anchor='w').pack(side=Tk.LEFT)
        Tk.Label(row, width=22, text=fields[1], anchor='w').pack(side=Tk.LEFT)
        Tk.Label(row, width=22, text=fields[2], anchor='w').pack(side=Tk.LEFT)
        row.pack(side=Tk.TOP, fill=Tk.X, padx=5, pady=5)

        for boundary in self.delaunay_triangulation.triangulated_info['NTG']:
            row = Tk.Frame(self.cond_window)
            lab = Tk.Label(row, width=22, text=str(boundary) + ": ", anchor='w')
            lab.pack(side=Tk.LEFT)

            params = {}
            for key in fields:
                ent = Tk.Entry(row)
                ent.insert(0, "1")
                ent.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.X)
                params[key] = ent

            row.pack(side=Tk.TOP, fill=Tk.X, padx=5, pady=5)
            entries[boundary] = params

        return entries

    def _load_data(self):
        # open file dialog
        filepath = Tk.filedialog.askopenfilename(title="Select file", filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(filepath)
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
        print('+++++++++++++++++++++++++++++++++')
        print(self.delaunay_triangulation.triangulated)
        self._print_info(self.delaunay_triangulation.triangulated_info)
        print('+++++++++++++++++++++++++++++++++')
        print(self.delaunay_triangulation.triangulated_info)
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
