import os
import sys
import tkinter as tk
from tkinter import messagebox, BooleanVar, Checkbutton
from pathlib import Path
from mwscanner_control import *

# sys.path.append(os.path.join(Path.cwd(), ".."))
# try:
#     from src.mwscanner_control import *
# except (Exception,):
#     raise


class MotorControlApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initial object

        self.motor_control = MotorControl()

        # Colors
        self.bg_color = 'light grey'
        self.txt_color = 'black'
        self.entry_color = 'white'

        # Left padding for all buttons
        self.padx = 10
        self.pady = 5

        self.title('Motor Control Interface')
        self.geometry('1000x1000')
        self.configure(bg=self.bg_color)

        self.init_button = None
        self.head_button = None
        self.show_button = None
        self.move_forward_button = None
        self.move_backward_button = None
        self.create_circle_button = None
        self.circle_distance_entry = None
        self.create_ellipse_button = None
        self.ellipse_distance_entry = None
        self.print_button = None
        self.pauses_checkbutton = None
        self.plot_checkbutton = None
        self.motor_entry = None
        self.distance_entry = None
        self.pauses = None
        self.plot = None
        self.output = None

        self.force_move_forward_button = None
        self.force_move_backward_button = None
        self.force_motor_entry = None
        self.force_distance_entry = None

        self.create_widgets()

    def create_widgets(self):
        # Create widgets

        self.pauses = BooleanVar()
        self.plot = BooleanVar()

        # Init Button
        self.init_button = tk.Button(self, text='Init Motors',
                                     command=self.init_motors, bg=self.bg_color,
                                     fg=self.txt_color)
        self.init_button.grid(row=0, column=0, padx=self.padx, pady=self.pady)

        # Set on Head Button

        self.head_button = tk.Button(self, text='Set on Head',
                                     command=self.set_on_head, bg=self.bg_color,
                                     fg=self.txt_color)
        self.head_button.grid(row=2, column=0, padx=self.padx, pady=self.pady)

        # Move Forward Button
        self.move_forward_button = tk.Button(self, text='Move Forward',
                                             command=self.move_forward,
                                             bg=self.bg_color,
                                             fg=self.txt_color)
        self.move_forward_button.grid(row=4, column=0, padx=self.padx,
                                      pady=self.pady)

        # Move Backward Button
        self.move_backward_button = tk.Button(self, text='Move Backward',
                                              command=self.move_backward,
                                              bg=self.bg_color,
                                              fg=self.txt_color)
        self.move_backward_button.grid(row=4, column=1, padx=self.padx,
                                       pady=self.pady)

        # Motor and Distance Entry Widgets
        tk.Label(self, text="Motor N. (100==all):",
                 bg=self.bg_color, fg=self.txt_color).grid(row=3, column=2,
                                                           padx=self.padx,
                                                           pady=self.pady)
        self.motor_entry = tk.Entry(self, bg=self.entry_color)
        self.motor_entry.grid(row=4, column=2, padx=self.padx,
                              pady=self.pady)

        tk.Label(self, text="Distance (mm):", bg=self.bg_color,
                 fg=self.txt_color).grid(row=3, column=3, padx=self.padx,
                                         pady=self.pady)
        self.distance_entry = tk.Entry(self, bg=self.entry_color)
        self.distance_entry.grid(row=4, column=3, padx=self.padx,
                                 pady=self.pady)

        # Create Circle Button
        self.create_circle_button = tk.Button(self, text='Create Circle',
                                              command=self.create_circle,
                                              bg=self.bg_color,
                                              fg=self.txt_color)
        self.create_circle_button.grid(row=6, column=0, padx=self.padx,
                                       pady=self.pady)

        # Circle Distance Entry Widget
        tk.Label(self, text="Circle Distance from Head (mm):", bg=self.bg_color,
                 fg=self.txt_color).grid(row=5, column=1, padx=self.padx,
                                         pady=self.pady)
        self.circle_distance_entry = tk.Entry(self, bg=self.entry_color)
        self.circle_distance_entry.grid(row=6, column=1, padx=self.padx,
                                        pady=self.pady)

        # Create Ellipse Buton
        self.create_ellipse_button = tk.Button(self, text='Create Ellipse',
                                               command=self.create_ellipse,
                                               bg=self.bg_color,
                                               fg=self.txt_color)
        self.create_ellipse_button.grid(row=8, column=0, padx=self.padx,
                                        pady=self.pady)

        # Ellipse Distance Entry Widget
        tk.Label(self, text="Ellipse Distance from Head (mm):",
                 bg=self.bg_color,
                 fg=self.txt_color).grid(row=7, column=1, padx=self.padx,
                                         pady=self.pady)
        self.ellipse_distance_entry = tk.Entry(self, bg=self.entry_color)
        self.ellipse_distance_entry.grid(row=8, column=1, padx=self.padx,
                                         pady=self.pady)

        # Plot Checkbutton
        self.plot_checkbutton = Checkbutton(self, text='Plot Ellipse?',
                                            variable=self.plot,
                                            bg=self.bg_color, fg=self.txt_color)
        self.plot_checkbutton.grid(row=8, column=2, padx=self.padx,
                                   pady=self.pady)

        # Pause Checkbutton
        self.pauses_checkbutton = Checkbutton(self, text='Pause on every '
                                                         'Antenna?',
                                              variable=self.pauses,
                                              bg=self.bg_color,
                                              fg=self.txt_color)
        self.pauses_checkbutton.grid(row=10, column=0, padx=self.padx,
                                     pady=self.pady)

        # Show Antennas Button

        self.show_button = tk.Button(self, text='Show Antennas',
                                     command=self.show_antennas,
                                     bg=self.bg_color,
                                     fg=self.txt_color)
        self.show_button.grid(row=12, column=0, padx=self.padx,
                              pady=self.pady)

        self.print_button = tk.Button(self, text='Antennas Info',
                                      command=self.print_motor_control,
                                      bg=self.bg_color, fg=self.txt_color)
        self.print_button.grid(row=14, column=0, padx=self.padx,
                               pady=self.pady)

        self.output = tk.Text(self, bg='white')
        self.output.grid(row=16, column=0, columnspan=6, padx=self.padx,
                         pady=self.pady)

        # Force Move Forward Button
        self.force_move_forward_button = tk.Button(self, text='FORCE Move '
                                                              'Forward',
                                                   command=self.force_move_forward,
                                                   bg="red",
                                                   fg=self.txt_color)
        self.force_move_forward_button.grid(row=18, column=0, padx=self.padx,
                                            pady=self.pady)

        # Force Move Backward Button
        self.force_move_backward_button = tk.Button(self, text='FORCE Move '
                                                               'Backward',
                                                    command=self.force_move_backward,
                                                    bg="red",
                                                    fg=self.txt_color)
        self.force_move_backward_button.grid(row=18, column=1, padx=self.padx,
                                             pady=self.pady)

        # Motor and Distance Entry Widgets
        tk.Label(self, text="Motor N.:",
                 bg=self.bg_color, fg=self.txt_color).grid(row=17, column=2,
                                                           padx=self.padx,
                                                           pady=self.pady)
        self.force_motor_entry = tk.Entry(self, bg=self.entry_color)
        self.force_motor_entry.grid(row=18, column=2, padx=self.padx,
                                    pady=self.pady)

        tk.Label(self, text="Distance (mm):", bg=self.bg_color,
                 fg=self.txt_color).grid(row=17, column=3, padx=self.padx,
                                         pady=self.pady)
        self.force_distance_entry = tk.Entry(self, bg=self.entry_color)
        self.force_distance_entry.grid(row=18, column=3, padx=self.padx,
                                       pady=self.pady)

    def print_motor_control(self):
        if self.motor_control is not None:
            self.output.delete('1.0', tk.END)
            self.output.insert(tk.END, str(self.motor_control))
        else:
            messagebox.showerror('Error', 'No MotorControl object to print.')

    def init_motors(self):
        if self.motor_control is not None:
            self.motor_control.init_motors(pauses=self.pauses.get())
        else:
            messagebox.showerror('Error',
                                 'No MotorControl object to initialize.')

    def set_on_head(self):
        if self.motor_control is not None:
            self.motor_control.set_on_head(pauses=self.pauses.get())
        else:
            messagebox.showerror('Error',
                                 'No MotorControl object to set on head.')

    def show_antennas(self):
        if self.motor_control is not None:
            self.motor_control.show_antennas()
        else:
            messagebox.showerror('Error',
                                 'No MotorControl object to show antennas.')

    def move_forward(self):
        if self.motor_control is not None:
            try:
                motor = int(self.motor_entry.get())
                distance = float(self.distance_entry.get())
                self.motor_control.move_forward(motor, distance,
                                                pauses=self.pauses.get())
            except ValueError:
                messagebox.showerror('Error',
                                     'Please input valid motor number and '
                                     'distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')

    def move_backward(self):
        if self.motor_control is not None:
            try:
                motor = int(self.motor_entry.get())
                distance = float(self.distance_entry.get())
                self.motor_control.move_backward(motor, distance,
                                                 pauses=self.pauses.get())
            except ValueError:
                messagebox.showerror('Error',
                                     'Please input valid motor number and '
                                     'distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')

    def create_circle(self):
        if self.motor_control is not None:
            try:
                distance_from_head = float(self.circle_distance_entry.get())
                pauses = self.pauses.get()

                self.motor_control.create_circle(distance_from_head, pauses)
            except ValueError:
                messagebox.showerror('Error',
                                     'Please input valid motor and distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')

    def create_ellipse(self):
        if self.motor_control is not None:
            try:
                distance_from_head = float(self.ellipse_distance_entry.get())
                pauses = self.pauses.get()
                plot = self.plot.get()

                self.motor_control.create_ellipse(distance_from_head, pauses,
                                                  plot)
            except ValueError:
                messagebox.showerror('Error', 'Please input valid distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')

    def force_move_forward(self):
        if self.motor_control is not None:
            try:
                motor = int(self.force_motor_entry.get())
                distance = float(self.force_distance_entry.get())
                self.motor_control.force_forward(motor, distance)
            except ValueError:
                messagebox.showerror('Error',
                                     'Please input valid motor number and '
                                     'distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')

    def force_move_backward(self):
        if self.motor_control is not None:
            try:
                motor = int(self.force_motor_entry.get())
                distance = float(self.force_distance_entry.get())
                self.motor_control.force_backward(motor, distance)
            except ValueError:
                messagebox.showerror('Error',
                                     'Please input valid motor number and '
                                     'distance.')
        else:
            messagebox.showerror('Error', 'No MotorControl object to move.')
