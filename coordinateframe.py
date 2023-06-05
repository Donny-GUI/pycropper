import customtkinter as ctk
from PIL import ImageTk, Image
import json
from typing import Literal, Tuple
from customtkinter.windows.widgets.font import CTkFont


class CoordinateFrame(ctk.CTkFrame):
    
    def __init__(self, master, x , y, w, h, image_path):
        super().__init__(master, width=600, border_width=1)
        self.master = master
        self.image_path = image_path
        self.x = x 
        self.y = y
        self.w = w 
        self.h = h
        self.x2 = self.x+self.w
        self.y2 = self.y+self.h
        self.xlabel  = ctk.CTkLabel(self, text="x: "+str(self.x))
        self.xlabel.grid(column=0, row=0, padx=(5,2), pady=(2,0), ipadx=0, ipady=0)
        self.ylabel  = ctk.CTkLabel(self, text="y: "+str(self.y))
        self.ylabel.grid(column=1, row=0, padx=(20,2), pady=(2,0), ipadx=0, ipady=0)
        self.wlabel  = ctk.CTkLabel(self, text="width: "+str(self.w))
        self.wlabel.grid(column=2, row=0, padx=(20,2), pady=(2,0))
        self.hlabel  = ctk.CTkLabel(self, text="height: "+str(self.h))
        self.hlabel.grid(column=0, row=1, padx=(5,2), pady=(0,0))
        self.x2label = ctk.CTkLabel(self, text="x2: "+str(self.x2))
        self.x2label.grid(column=1, row=1, padx=(20,2), pady=(0,0))
        self.y2label = ctk.CTkLabel(self, text="y2: "+ str(self.y2))
        self.y2label.grid(column=2, row=1, padx=(20,2), pady=(0,0))
        self.subimage = Image.open(self.image_path)
        self.cropped_image = self.subimage.crop((self.x, self.y, self.x + self.w, self.y + self.h))
        self.cropped_image = self.cropped_image.convert("RGB")
        self.cropped_image= self.cropped_image.resize((self.w, self.h))
        self.sub_photoimage = ImageTk.PhotoImage(self.cropped_image, size=(self.w, self.h))
        self.photoimage = ctk.CTkCanvas(self, width=w, height=h)
        self.photoimage.grid(column=3, row=0, pady=2, padx=2)
        self.photoimage.create_image(w//2, h//2, image=self.sub_photoimage)
        self.remove_button = ctk.CTkButton(self, text="-", width=30, height=30)
        self.remove_button.grid(column=4, row=0, rowspan=3, pady=(2,2), padx=(40,2))
        self.remove_button.bind("<Button-1>", self.remove_me)
    
    def remove_me(self, *args):
        self.destroy()
        self.master.yindex -1
    
    def get_coordinates(self) -> None:
        return {"x":self.x, "y":self.y, "w":self.w, "h":self.h, "x2":self.x2, "y2":self.y2} 



class CoordinatesFrame(ctk.CTkFrame):
    def __init__(self, master: any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, scrollbar_fg_color: str | Tuple[str, str] | None = None, scrollbar_button_color: str | Tuple[str, str] | None = None, scrollbar_button_hover_color: str | Tuple[str, str] | None = None, label_fg_color: str | Tuple[str, str] | None = None, label_text_color: str | Tuple[str, str] | None = None, label_text: str = "", label_font: tuple | CTkFont | None = None, label_anchor: str = "center", orientation: Literal['vertical', 'horizontal'] = "vertical"):
        super().__init__(master, border_width=4, height=600, width=700)
        self.coordinate_frame = ctk.CTkScrollableFrame(self, border_width=2, width=400)
        self.coordinate_frame.grid(column=0, row=0, columnspan=3, padx=(5,5), pady=(5,5), sticky='nsew')
        self.button_frame = ctk.CTkFrame(self, width=700, height=200)
        self.button_frame.grid(column=0, row=1, sticky='nsew')
        self.save_button = ctk.CTkButton(self.button_frame, text="save to json", command=self.save_coords, width=400, state="disabled")
        self.save_button.grid(column=0, row=0, columnspan=3, sticky='nsew')
        self.yindex = 0
        self.xindex = 0
        self.coords = []
        self.save_disabled = True
        
    def add_coordinate(self, x, y ,w, h, image_path):
        if self.save_disabled == True:
            self.save_button.configure(state="normal")
            self.save_disabled = False
        self.new_frame: CoordinateFrame = CoordinateFrame(self.coordinate_frame, x, y, w, h, image_path)
        self.new_frame.grid(column=self.xindex, row=self.yindex, sticky='wens', padx=(3,3), pady=(2,2), columnspan=3)
        self.yindex+=1
        self.coords.append(self.new_frame)
    
    def get_coordinates(self) -> None:
        retv = []
        for coord in self.coords:
            retv.append(coord.get_coordinates())
        return retv
    
    def save_coords(self) -> None:
        coords = self.get_coordinates()
        with open("coordinates.json", "w") as jfile:
            json.dump(coords, jfile)
