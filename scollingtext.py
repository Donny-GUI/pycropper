import customtkinter as ctk

class ScrollingTextBox(ctk.CTkTextbox):
    def __init__(self, master, width, message: str="") -> None:
        super().__init__(master=master, width=width, height=1, bg_color="black", text_color="green")
        
        self.message = message
        self.displayed_message = ""
        self.displayed_message_index = 0
        self._message_length = len(self.message)
        self.message_reversed = self.message[::-1]
        pad = " "*self._message_length
        self.message_reversed = pad+ pad + self.message_reversed
        self.message_length = len(self.message_reversed)
        self.speed = 100
        
    def set_message(self, message: str):
        self.message = message
        self.displayed_message = ""
        self.displayed_message_index = 0
        self.message_length = len(self.message)
        self.message_reversed = self.message[::-1]
        pad = " "*self.message_length
        self.message_reversed = "." + pad + pad + self.message_reversed
        self.message_length = len(self.message_reversed)
        self.speed = 100
    
    def set_speed(self, speed: int):
        self.speed = speed
    
    def left_to_right_update(self):
        self.delete("0.0", "end")
        for i in range(0, len(self.displayed_message)):
            self.insert(f"0.{i}", self.message_reversed[i])
        
        self.displayed_message_index += 1
        if self.displayed_message_index == self.message_length*2:
            self.displayed_message_index = 0
        
        
        self.displayed_message = self.message_reversed[:self.displayed_message_index]
        self.after(self.speed, self.left_to_right_update)
        
    def start(self):
        self.after(self.speed, self.left_to_right_update)


import tkinter as tk

class TypingTextBox(tk.Text):
    def __init__(self, master, width, message=""):
        super().__init__(master=master, width=width, height=1, bg="black", fg="green")
        
        self.message = message
        self.displayed_message = ""
        self.displayed_message_index = 0
        self.message_length = len(self.message)
        self.speed = 100
        
    def set_message(self, message):
        self.message = message
        self.displayed_message = ""
        self.displayed_message_index = 0
        self.message_length = len(self.message)
        self.speed = 100
    
    def set_speed(self, speed):
        self.speed = speed
    
    def left_to_right_update(self):
        self.delete("1.0", "end")
        self.displayed_message_index += 1
        if self.displayed_message_index <= self.message_length:
            self.displayed_message = self.message[:self.displayed_message_index]
            self.insert("1.0", self.displayed_message)
            self.after(self.speed, self.left_to_right_update)
        else:
            self.displayed_message = self.message
            self.insert("1.0", self.displayed_message)
            self.displayed_message_index = 0

    def start(self):
        self.after(self.speed, self.left_to_right_update)


