# Copyright (c) Peter Majko.

"""
Rhapsody's GUI console library - all the consoles for your tkinter needs :)
"""
import tkinter as tk
# TODO - properly document!!!


class ConsoleFrame(tk.Frame):

    def __init__(self, master=None, on_input_handle=None):
        super().__init__(master)
        self._on_input_handle = on_input_handle
        self.config(background='grey')

        self._output_widget = tk.Text(self, font=('Consolas', 11), bg='black', fg='#1ec503', state=tk.DISABLED)
        # self._output_widget.configure()
        self._output_widget.pack(fill='both', side='top', expand=True)

        self._input_label = tk.Label(self, bg='black', fg='#1ec503', text=' >')
        self._input_label.pack(side='left')

        self._input_content = tk.StringVar()
        self._input_history = ['']
        self._input_history_current_index = 0

        self._input_widget = tk.Entry(self)
        self._input_widget.bind('<Key-Return>', self._input, )
        self._input_widget.bind('<Key-Up>', self._input_history_prev)
        self._input_widget.bind('<Key-Down>', self._input_history_next)
        self._input_widget.configure(textvariable=self._input_content,
                                     font=('Consolas', 11),
                                     bg='black', fg='#1ec503',
                                     insertbackground='#1ec503',
                                     insertwidth=1,
                                     exportselection=0,
                                     validate='key',
                                     validatecommand=(self.register(self._input_on_key), '%P'))
        self._input_widget.pack(fill='both', side='right', expand=True)
        self._input_widget.focus_set()

    def write(self, data):
        self._output_widget.configure(state=tk.NORMAL)
        self._output_widget.insert('end', data)
        self._output_widget.see('end')
        self._output_widget.configure(state=tk.DISABLED)

    def _input(self, event):
        user_input = self._input_content.get()
        if user_input != '':
            self._input_history.insert(-1, user_input)
            self._input_history_current_index = len(self._input_history) - 1
            self._input_history[self._input_history_current_index] = ''
            self._input_widget.delete(0, 'end')
            # TODO - console commands
            if user_input == '~clear':
                self.clear()
            else:
                if not self._on_input_handle:
                    self.write(user_input)
                else:
                    self._on_input_handle(user_input)

    def change_on_input_handle(self, handle):
        self._on_input_handle = handle

    def _input_history_prev(self, event):
        if len(self._input_history) > 0 and self._input_history_current_index - 1 >= 0:
            self._input_history_current_index -= 1
            self._input_content.set(self._input_history[self._input_history_current_index])
            self._input_widget.icursor('end')

    def _input_history_next(self, event):
        if self._input_history_current_index + 1 < len(self._input_history):
            self._input_history_current_index += 1
            self._input_content.set(self._input_history[self._input_history_current_index])
            self._input_widget.icursor('end')

    def _input_on_key(self, entry_text_after_key):
        if self._input_history_current_index == len(self._input_history) - 1:
            self._input_history[len(self._input_history) - 1] = entry_text_after_key
        return True

    def clear(self):
        self._output_widget.configure(state=tk.NORMAL)
        try:
            self._output_widget.delete(1.0, 'end')
        except tk.TclError as err:
            print(err)
        self._output_widget.see('end')
        self._output_widget.configure(state=tk.DISABLED)
