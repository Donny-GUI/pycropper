import customtkinter as ctk 
  
class LabeledValue:
    def __init__(self, master, name: str="No Label", value:str="No Value"):
        self.frame = ctk.CTkFrame(master, corner_radius=5)
        self.corner_rad = 50
        self.pad_right = 10
        self.name = name
        self.value = value
        self.name_label = ctk.CTkLabel(self.frame, text=self.name, corner_radius=50)
        self.value_label = ctk.CTkLabel(self.frame, text=self.value, corner_radius=self.corner_rad)
        self.name_label.grid(column=0, row=0, padx=(5,3), pady=2, sticky="ew")
        self.value_label.grid(column=1, row=0, padx=(3,5), pady=2, sticky='ew')
        self.attention_index = 0
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
    
    def show(self):
        self.name_label.grid(column=0, row=0, padx=(5,3), pady=2, sticky="ew")
        self.value_label.grid(column=1, row=0, padx=(3,5), pady=2, sticky='ew')
    
    def attention_value(self):
        self.highlight_value()
        self.frame.after(500, self.unhighlight_value)

    def reset_corner_rad(self):
        self.corner_rad = 50
        
    def attention_name(self):
        self.highlight_name()
        self.frame.after(500, self.unhighlight_name)
    
    def unhighlight_value(self):
        self.frame.configure(fg_color="transparent")
    
    def unhighlight_name(self):
        self.name_label.configure(fg_color="transparent")
        
    def highlight_value(self, color="green"):
        self.frame.configure(fg_color=color)
    
    def highlight_name(self, color="green"):
        self.name_label.configure(fg_color=color)
    
    def hide(self):
        self.name_label.grid_forget()
        self.value_label.grid_forget()
        
    def set_value(self, value: any):
        self.value = value
        self.value_label.configure(text=str(self.value))
        
    def set_name(self, name: str):
        self.name = name
        self.name_label.configure(text=self.name)