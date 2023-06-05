import subprocess
from typing import Optional, Tuple, Union
import customtkinter as ctk
import webcolors
from PIL import ImageTk, Image
import sys
import win32com.client
from fontTools import ttLib
from coordinateframe import CoordinatesFrame

  
class ImageViewer(ctk.CTk):
    colors = list(webcolors.CSS3_NAMES_TO_HEX.keys())
    color_max = len(colors) - 1
    
    
    def __init__(self) -> None:
        
        super().__init__()
        self.configure(width=1000, height=1200)
        # VIEW
        self.tab_view = ctk.CTkTabview(master=self, width=1100, height=900)
        self.tab_view.grid(column=0, row=0, sticky="nsew")
        self.tab_cropper = self.tab_view.add("Cropper")
        self.tab_slicer = self.tab_view.add("Slicer")
        self.tab_settings = self.tab_view.add("Settings")
        self.settings_tab = SettingsTab(self)
        self.cropper_tab = CropperTab(self)
        

class CropperTab:
    def __init__(self, master: ImageViewer) -> None:
        self.master = master
        from images import Photos
        # VARIABLES
        self.fonts = []
        self.saved_coordinates_box_color = "blue"
        self._get_usable_fonts()
        self.font_name = self.fonts[0]
        self.font_object = ctk.CTkFont(family=self.fonts[2], size=16)
        self.italic_font = ctk.CTkFont(family=self.fonts[2], size=16, slant="italic")
        self.bold_font = ctk.CTkFont(family=self.fonts[2], size=16, weight="bold")
        self.image_uploaded = False
        self.buttons_enabled = False
        self.subimage_zoom_factor = 4
        self.rectx = 0; self.recty = 0; self.rectw = 16; self.recth = 16
        self.pixel_count = 0
        self.row_count = 0
        self.column_count = 0
        self.image = None
        self.image_path = None 
        self.matrix = None
        self.image_width = None
        self.image_height = None
        self.image_center_width = None
        self.image_center_height = None
        self.subimage_matrixes = []
        self.subimage = None
        self.subimage_path = None 
        self.subimage_matrix = None
        self.subimage_width = None
        self.subimage_height = None
        self.subimage_center_width = None
        self.subimage_center_height = None
        self.current_color = "red"
        self.current_appearance = "system"
        self.color_index = 0
        self.boxes = []
        # FRAMES
        self.main_frame = ctk.CTkFrame(self.master.tab_view.tab("Cropper"), width=1200, height=1000)
        self.main_frame.grid(column=0, row=0, sticky='nsew')
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.grid(column=0, row=0, sticky='nw')
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.grid(column=1, row=0, sticky='ne')
        self.subframe_bottom = ctk.CTkFrame(self.left_frame, border_width=4)
        self.subframe_bottom.grid(column=0, row=1, sticky='nesw', padx=5, pady=5)
        self.subframe_right = ctk.CTkFrame(self.right_frame)
        self.subframe_right.grid(column=0, row=0, sticky='nwse', padx=5, pady=5)
        self.subframe_right_top = ctk.CTkFrame(self.subframe_right, border_width=4)
        self.subframe_right_top.grid(row=0, column=0, sticky='nwse', padx=2, pady=2)
        self.subframe_right_bottom = ctk.CTkFrame(self.subframe_right, width=700, height=400, border_width=4)
        self.subframe_right_bottom.grid(row=1, column=0, sticky='swne', padx=2, pady=2)
        # WIDGETS
        self.image_canvas                   = ctk.CTkCanvas(    self.subframe_bottom,    width=400, height=400, borderwidth=0, background="black")
        self.subimage_canvas                = ctk.CTkCanvas(    self.subframe_right_top, width=60,  height=60,  borderwidth=0,)
        self.load_image_button              = ctk.CTkButton(    self.subframe_right_top,image=Photos.upload_image, text="Load Image", command=self.get_image, border_width=10, font=self.font_object)
        self.coordinates_frame              = CoordinatesFrame( self.subframe_right_top)
        self.move_left_button               = ctk.CTkButton(    self.subframe_right_bottom, width=60, text= "", image=Photos.arrow_left, command=self.move_box_left, font=self.font_object)
        self.add_coordinate_button          = ctk.CTkButton(    self.subframe_right_bottom, text="save coordinate", command=self.mark_coordinate, font=self.font_object)
        self.move_right_button              = ctk.CTkButton(    self.subframe_right_bottom, width=60, text= "", image=Photos.arrow_right, command=self.move_box_right, font=self.font_object)
        self.move_up_button                 = ctk.CTkButton(    self.subframe_right_bottom, width=60, text= "", image=Photos.arrow_up, command=self.move_box_up, font=self.font_object)
        self.move_down_button               = ctk.CTkButton(    self.subframe_right_bottom, width=60, text= "", image=Photos.arrow_down, command=self.move_box_down, font=self.font_object)
        self.increase_box_width_button      = ctk.CTkButton(    self.subframe_right_bottom, image=Photos.plus,  text="box width", command=self.increase_box_width, font=self.font_object)
        self.decrease_box_width_button      = ctk.CTkButton(    self.subframe_right_bottom, image=Photos.minus, text="box width", command=self.increase_box_width, font=self.font_object)
        self.increase_box_height_button     = ctk.CTkButton(    self.subframe_right_bottom, image=Photos.plus,  text="box height", command=self.increase_box_height, font=self.font_object)
        self.decrease_box_height_button     = ctk.CTkButton(    self.subframe_right_bottom, image=Photos.minus, text="box height", command=self.increase_box_height, font=self.font_object)
        self.save_crop_button               = ctk.CTkButton(    self.subframe_right_bottom, image=Photos.save,  text="Save Crop", command=self.save_crop, font=self.font_object)
        self.save_image_name_label          = ctk.CTkLabel(     self.subframe_right_bottom, text="Image Name: ", font=self.font_object)
        self.save_image_name                = ctk.CTkEntry(     self.subframe_right_bottom, placeholder_text="cropped_image", font=self.font_object)
        self.save_image_extension_combo     = ctk.CTkComboBox(  self.subframe_right_bottom, values=["PNG", "GIF", "JPG"],  font=self.font_object)
        # placement
        self.image_canvas.grid(                 column=0, row=0, padx=(2, 2), pady=(2,2))
        self.subimage_canvas.grid(              row=4, column=2, padx=(20, 2), pady=(10,10), sticky='w')
        self.load_image_button.grid(            column=2, row=0, padx=(20, 20), pady=(5,5))
        self.coordinates_frame.grid(            column=5, row=0, padx=(120, 0), sticky='e')
        self.move_left_button.grid(             column=0, row=1, padx=(2, 2), pady=(2, 2), sticky='e')
        self.add_coordinate_button.grid(        column=1, row=1, pady=(0, 0), padx=(0, 0), sticky='nwse')
        self.move_right_button.grid(            column=2, row=1, padx=(2, 2), pady=(2, 2), sticky='w')
        self.move_up_button.grid(               column=1, row=0, padx=(2, 2), pady=(2, 2), sticky='s')
        self.move_down_button.grid(             column=1, row=2, padx=(2, 2), pady=(2, 2), sticky='n')
        self.increase_box_width_button.grid(    column=3, row=1, padx=(2, 2), pady=(2, 2))
        self.decrease_box_width_button.grid(    column=3, row=2, padx=(2, 2), pady=(2, 2))
        self.increase_box_height_button.grid(   column=4, row=1, padx=(2, 2), pady=(2, 2))
        self.decrease_box_height_button.grid(   column=4, row=2, padx=(2, 2), pady=(2, 2))
        self.save_crop_button.grid(             column=0, row=3, padx=(2, 2), pady=(2, 2))
        self.save_image_name_label.grid(        column=1, row=3, padx=(2, 2), pady=(2, 2))
        self.save_image_name.grid(              column=2, row=3, padx=(2, 2), pady=(2, 2))
        self.save_image_extension_combo.grid(   column=3, row=3)
        
        self.save_image_name.insert(0, "cropped_image")
        
        self.save_image_extension_combo.bind("<Button-1>", lambda cbo: self.set_save_extension())
        self.save_image_extension_combo.set("PNG")
        
        self.disable_until_image_loaded()

    

    def get_windows_fonts(self):
        shell = win32com.client.Dispatch("Shell.Application")
        fonts_folder = shell.Namespace(0x14)  # 0x14 represents the Fonts folder
        for item in fonts_folder.Items():
            self.fonts.append(item.Name)
    
    def get_linux_fonts(self):
        try:
            output = subprocess.check_output(['fc-list'])
            fonts = output.decode().splitlines()
            return fonts
        except subprocess.CalledProcessError:
            print("Error: Unable to retrieve fonts.")
            return []
    
    def get_mac_fonts(self):
        # Get the paths to the font files on your Mac
        font_paths = ttLib.getInstalledFonts()
        for path in font_paths:
            try:
                font = ttLib.TTFont(path)
                font_name = str(font['name'].getName(1, 3, 1, 1033))
                # Add the font name to the list
                self.fonts.append(font_name)

            except Exception as e:
                print(f"Error processing font: {path}")
                print(e)

    def _get_usable_fonts(self) -> None:
        if sys.platform.startswith("w"):
            self.get_windows_fonts()
        elif sys.platform.startswith('l'):
            self.get_linux_fonts()
        elif sys.platform.startswith('d'):
            return self.get_mac_fonts()
        print(self.fonts)
    
    def disable_until_image_loaded(self) -> None:
        """ 
        Disables the buttons that would cause harm if pressed before image uploaded
        """
        self.move_left_button.configure(            state="disabled")
        self.add_coordinate_button.configure(       state="disabled")
        self.move_right_button.configure(           state="disabled")
        self.move_up_button.configure(              state="disabled")
        self.move_down_button.configure(            state="disabled")
        self.save_crop_button.configure(            state="disabled")
        self.increase_box_width_button.configure(   state="disabled")
        self.decrease_box_width_button.configure(   state="disabled")
        self.increase_box_height_button.configure(  state="disabled")
        self.decrease_box_height_button.configure(  state="disabled")
        
    def enabled_after_image_loaded(self) -> None:
        """ 
        Enables the buttons that would cause harm if pressed before an image is uploaded
        """
        self.move_left_button.configure(                state="normal")
        self.add_coordinate_button.configure(           state="normal")
        self.move_right_button.configure(               state="normal")
        self.move_up_button.configure(                  state="normal")
        self.move_down_button.configure(                state="normal")
        self.increase_box_width_button.configure(       state="normal")
        self.increase_box_height_button.configure(      state="normal")
        self.save_crop_button.configure(                state="normal")
        self.increase_box_width_button.configure(       state="normal")
        self.decrease_box_width_button.configure(       state="normal")
        self.increase_box_height_button.configure(      state="normal")
        self.decrease_box_height_button.configure(      state="normal")
        
        self.load_image_button.configure(border_width=0)
    
    def mark_coordinate(self) -> None:
        """ 
        if the main image is set, creates a box of the current selector coordinates and appends the box to the list of boxes,
        then adds the coordinates to the coordinates frame
        """
        if self.main_image_path != None:
            box = (self.rectx, self.recty, self.rectw, self.recth)
            self.boxes.append(box)
            self.coordinates_frame.add_coordinate(self.rectx, self.recty, self.rectw, self.recth, self.main_image_path)
    
    def set_save_extension(self, *args) -> None:
        """ 
        gets the value of the extension combo box and makes the extension.
        """
        self.save_image_extension = self.save_image_extension_combo.get()
        self.save_image_extension_lower = "." + self.save_image_extension.lower()
        
    def save_crop(self) -> None:
        """ 
        opens the main image and crops it, gets the extension used and makes the filename,
        then saves the file that is cropped as the given filename
        """
        self.subimage = Image.open(self.main_image_path)
        self.cropped_image = self.subimage.crop((self.rectx, self.recty, self.rectx + self.rectw, self.recty + self.recth))
        self.set_save_extension()
        self.save_image_extension_filename = self.save_image_name.get() + self.save_image_extension_lower
        self.cropped_image.save(fp=self.save_image_extension_filename, format=self.save_image_extension)
    
    def increase_box_width(self) -> None:
        """ 
        increases the rectange width of the selector and refreshes the image
        """
        self.rectw +=1
        self.refresh_image()
    
    def increase_box_height(self) -> None:
        """
        increases the rectange height of the selector and refreshes the image
        """
        self.recth +=1
        self.refresh_image()
        
    def move_box_down(self, *args) -> None:
        """
        moves the box DOWN a height length of the box, then refreshes the image
        """
        self.recty+=self.recth 
        if self.recty > self.image_height:
            self.recty = 0
        self.refresh_image()
        
    def move_box_up(self, *args) -> None:
        """
        moves the box UP a height length of the box, then refreshes the image
        """
        self.recty = self.recty - self.recth 
        if self.recty < 0:
            self.recty = self.image_height
        self.refresh_image()
    
    def move_box_left(self, *args) -> None:
        """
        moves the select box one width length to the left, 
        if its off the screen goes to the previous row and at the end.
        """
        self.rectx = self.rectx - self.rectw
        if self.rectx < 0:
            self.rectx = self.image_width - self.rectw
            self.recty+=self.recth
        if self.recty == self.image_height:
            self.recty = self.image_height + self.recth
        self.refresh_image()
    
    def move_box_right(self, *args) -> None:
        """
        moves the select box one width length to the right, 
        if its off the screen goes to the next row and at the beginning.
        """
        self.rectx+=self.rectw
        if self.rectx == self.image_width:
            self.rectx = 0
            self.recty+=self.recth
        if self.recty == self.image_height:
            self.recty = 0
        self.refresh_image()
        
    def get_image(self) -> None:
        """
        called when the browse file has achieved completion. sets the flag for the buttons to be 
        set to undisabled. sets the flag for the buttons to not be checked again
        """
        image_file = ctk.filedialog.askopenfilename()
        if image_file is not None:
            self.image_uploaded = True
            self.set_image(image_file)
        if self.buttons_enabled == False:
            if self.image_uploaded == True:
                self.enabled_after_image_loaded()
                self.buttons_enabled = True
    
    def set_image(self, image_path: str):
        """ 
        takes the used filepath and create the main image and subimages
        then refreshes the images

        Args:
            image_path (str): chosen filepath
        """
        self.main_image_path = image_path
        self.image, self.matrix, self.image_width, self.image_height, self.image_center_width, self.image_center_height = self.image_to_photo(image_path)
        self.reset_box_location()
        self.refresh_image()
    
    def reset_box_location(self) -> None:
        """
        sets the rect x and y coordinate to 0
        """
        self.rectx = 0
        self.recty = 0
    
    def calculate_subimage_width_height(self) -> None:
        """
        calculates half of the subimage using floor division or regular division if mod 2
        """
        self.subimage_canvas_width = self.rectw/2 if self.rectw%2==0 else self.rectw//2
        self.subimage_canvas_height = self.recth/2 if self.recth%2==0 else self.recth//2
    
    def refresh_image(self) -> None:
        """
        refreshes the cursor, the image, the subimage and draws the cursor and rectangles selected
        """
        self.image_canvas.create_image(self.image_center_width, self.image_center_height, image=self.image)
        self.image_canvas.configure(height=self.image_height, width=self.image_width)
        self.calculate_subimage_width_height()
        self.draw_subimage()
        self.draw_all_rectangles()
    
    def draw_subimage(self) -> None:
        """
        draws the subimage in its canvas. First by opening the image, then getting the selector location as an image
        """
        self.subimage = Image.open(self.main_image_path)
        self.cropped_image = self.subimage.crop((self.rectx, self.recty, self.rectx + self.rectw, self.recty + self.recth))
        self.cropped_image = self.cropped_image.convert("RGB")
        self.cropped_image= self.cropped_image.resize((self.rectw*self.subimage_zoom_factor, self.recth*self.subimage_zoom_factor))
        self.sub_photoimage = ImageTk.PhotoImage(self.cropped_image, size=(self.rectw, self.recth))
        self.subimage_canvas.create_image(self.subimage_canvas_width*self.subimage_zoom_factor, self.subimage_canvas_height*self.subimage_zoom_factor, image=self.sub_photoimage)
        self.subimage_canvas.configure(height=self.recth*self.subimage_zoom_factor, width=self.rectw*self.subimage_zoom_factor)
    
    def draw_all_rectangles(self) -> None:
        """
        draws all the rectanges including previously selected and what not
        """
        self.draw_rectangle()
        self.draw_saved_coordinates()
    
    def draw_rectangle(self, *args) -> None:
        """
        draws the selector and its outer layer, calls itself as an after call to continue changing its color
        """
        self.get_next_color()
        self.image_canvas.create_rectangle(self.rectx,  self.recty, self.rectx+self.rectw, self.recty+self.recth,  outline=self.current_color)
        self.image_canvas.create_rectangle(self.rectx-1,  self.recty+1, self.rectx+self.rectw+1, self.recty+self.recth+1,  outline=self.second_color)
        #self.image_canvas.create_line(self.rectx,  self.recty, 0, 0)
        #self.image_canvas.create_line(self.rectx+self.rectw, self.recty+self.recth, self.image_width, self.image_width)
        self.image_canvas.after(1000, self.draw_rectangle)
        
    
    def draw_saved_coordinates(self):
        """
        iterates over the saved boxes and draws them on the main image
        """
        for box in self.boxes:
            rect = self.image_canvas.create_rectangle(box[0],  box[1], box[0]+box[2], box[1]+box[3],  outline=self.saved_coordinates_box_color)
    
        
    def get_next_color(self):
        """
        gets the next color in the sequence, also sets the secondary color to the last color
        """
        self.second_color= self.master.colors[self.color_index]
        self.color_index+=1
        if self.color_index > self.master.color_max:
            self.color_index = 0
        self.current_color = self.master.colors[self.color_index]
    
    def image_to_photo(self, image_path: str) -> tuple:
        """
        takes an image path and returns a ImageTk.PhotoImage from it

        Args:
            image_path (str): path to the image file

        Returns:
            ImageTk.PhotoImage
        """
        img = Image.open(image_path)
        width, height = img.size
        img.convert("RGB")
        im = ImageTk.PhotoImage(img, size=(width, height))
        rimgdata = img.getdata()
        img.close()
        return im, rimgdata, width, height, width//2, height//2   
    
    def make_photo(self, image_path: str) -> tuple:
        """
        better version of image_to_photo

        Args:
            image_path (str): path to the image file

        Returns:
            ImageTk.PhtoImage
        """
        img = Image.open(image_path)
        width, height = img.size
        img.convert("RGB")
        im = ImageTk.PhotoImage(img, size=(width, height))
        img.close()
        return im, width, height


class SettingsTab:
    def __init__(self, master: ImageViewer) -> None:
        self.move_box_left_key = ""
        self.move_box_left_key_denote = ""
        self.move_box_right_key = ""
        self.move_box_right_key_denote = ""
        self.move_box_up_key = ""
        self.move_box_up_key_denote = ""
        self.move_box_down_key = ""
        self.move_box_down_key_denote = ""
        self.fonts = []
        self.font_name = ""
        self.font_size = 16
        self.font_slant = "roman"
        self.font_weight = "normal"
        self.master = master
        self.settings_frame = ctk.CTkFrame(self.master.tab_view.tab("Settings"), width=1200, height=1000)
        self.settings_frame.grid(column=0, row=0, sticky='nswe')
        self.set_window_mode_label = ctk.CTkLabel(self.settings_frame, text="Set Window Appearance")
        self.set_window_mode_label.grid(column=0, row=0)
        self.set_window_mode_combo = ctk.CTkComboBox(self.settings_frame, values=["system", "dark", "light"], command=self.set_window_appearance)
        self.set_window_mode_combo.grid(column=1, row=0)
        self.set_window_mode_combo.bind("<<ComboboxSelected>>", self.set_window_appearance)
        self.set_font_name_label = ctk.CTkLabel(self.settings_frame, text="Font Family")
        self.set_font_name_label.grid(column=0, row=1)
        self.set_font_name_combo = ctk.CTkComboBox(self.settings_frame, values=self.fonts, command=self.set_default_font_name)
        self.set_font_name_combo.grid(column=1, row=1)
        self.set_font_size_label = ctk.CTkLabel(self.settings_frame, text="Font Size")
        self.set_font_size_label.grid(column=0, row=2)
        self.set_font_size_combo = ctk.CTkComboBox(self.settings_frame, values=[str(x) for x in range(0, 50)], command=self.set_font_size)
        self.set_font_size_combo.grid(column=1, row=2)
        self.set_button_color_label = ctk.CTkLabel(self.settings_frame, text="Button Color")
        self.set_button_color_label.grid(column=0, row=3)
        self.set_button_color_combo = ctk.CTkComboBox(self.settings_frame, values=self.master.colors, command=self.set_button_color)
        self.set_button_color_combo.grid(column=1, row=3)
        self.set_left_box_motion_key_label = ctk.CTkLabel(self.settings_frame, text="Move Box Left Key")
        self.set_left_box_motion_key_label.grid(column=0, row=3)
        self.set_left_box_motion_key_button = ctk.CTkButton(self.settings_frame, text="Bind", command=self.wait_key_and_bind)
        self.set_left_box_motion_key_button.grid(column=1, row=3)
        self.set_right_box_motion_key_label = ctk.CTkLabel(self.settings_frame, text="Move Box Right Key")
        self.set_right_box_motion_key_label.grid(column=0, row=4)
        self.set_right_box_motion_key_button = ctk.CTkButton(self.settings_frame, text="Bind", command= self.wait_key_and_bind)
        self.set_right_box_motion_key_button.grid(column=1, row=4)
        self.set_up_box_motion_key_label = ctk.CTkLabel(self.settings_frame, text="Move Box Up Key")
        self.set_up_box_motion_key_label.grid(column=0, row=5)
        self.set_up_box_motion_key_button = ctk.CTkButton(self.settings_frame, text="Bind", command= self.wait_key_and_bind)
        self.set_up_box_motion_key_button.grid(column=1, row=5)
        self.set_down_box_motion_key_label = ctk.CTkLabel(self.settings_frame, text="Move Box Down Key")
        self.set_down_box_motion_key_label.grid(column=0, row=6)
        self.set_down_box_motion_key_button = ctk.CTkButton(self.settings_frame, text="Bind", command=self.wait_key_and_bind)
        self.set_down_box_motion_key_button.grid(column=1, row=6)  
        self.event_index = 0
        self.event_info = {}
        self.bind_event_data = {}
    
    def wait_key_and_bind(self, *args):
        """
        Listens for a key press event and binds it to the specified button.
        Returns:
            None
        """
        print(args)
        self.bind_event_data = {
            "left": (self.master.cropper_tab.move_left_button, self.set_left_box_motion_key_button, self.master.cropper_tab.move_box_left), 
            "right":(self.master.cropper_tab.move_right_button, self.set_right_box_motion_key_button, self.master.cropper_tab.move_box_right),
            "up": (self.master.cropper_tab.move_up_button, self.set_up_box_motion_key_button, self.master.cropper_tab.move_box_up), 
            "down":(self.master.cropper_tab.move_down_button, self.set_down_box_motion_key_button, self.master.cropper_tab.move_box_down)
        } 
        self.bind_event_data[key][1].bind("<Key>", lambda e: self.key_press_event(e, key))
    
    def key_press_event(self, e, key):
        self.bind_event_data = {
            "left": (self.master.cropper_tab.move_left_button, self.set_left_box_motion_key_button, self.master.cropper_tab.move_box_left), 
            "right":(self.master.cropper_tab.move_right_button, self.set_right_box_motion_key_button, self.master.cropper_tab.move_box_right),
            "up": (self.master.cropper_tab.move_up_button, self.set_up_box_motion_key_button, self.master.cropper_tab.move_box_up), 
            "down":(self.master.cropper_tab.move_down_button, self.set_down_box_motion_key_button, self.master.cropper_tab.move_box_down)
        }
        kk = e.keysym
        self.bind_event_data[key][0].configure(text=kk)
        self.bind_event_data[key][0].bind(f"<Key-{kk}>", self.bind_event_data[key][2])
        self.bind_event_data[key][1].unbind("<Key>")
        self.bind_event_data[key][1].configure(text="Bind") 
        print("binded")

    def set_button_color(self, *args):
        """ 
        Set all the buttons to the color in the set_button_color_combo
        """
        self.button_color = self.set_button_color_combo.get()
        self.master.cropper_tab.load_image_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.move_left_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.add_coordinate_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.move_right_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.move_up_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.move_down_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.increase_box_width_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.decrease_box_width_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.increase_box_height_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.decrease_box_height_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.save_crop_button.configure(fg_color=self.button_color)
        self.master.cropper_tab.coordinates_frame.save_button.configure(fg_color=self.button_color)
        
    def set_font_size(self, *args):
        """ 
        Set the font size of available text to the value in set_font_size_combo
        """
        self.font_size = int(self.set_font_size_combo.get())
        self.master.cropper_tab.set_font()
    
    def set_window_appearance(self, *args):
        """
        set the window color to one of three "system" "dark" or "light",
        dependent on the value in set_window_mode_combo
        """
        self.current_appearance = self.set_window_mode_combo.get()
        ctk.set_appearance_mode(self.current_appearance)
    
    def set_default_font_name(self, *args):
        """ Sets the default font to the value in set_font_name_combo
        """
        self.font_name = self.set_font_name_combo.get()
        print(self.font_name)
        self.set_font()
    
    def set_font(self):
        """ 
        called by one of the font methods after an update
        """
        self.master.cropper_tab.font_object = ctk.CTkFont(family=self.font_name, size=self.font_size, weight=self.font_weight, slant=self.font_slant)
        self.master.cropper_tab.load_image_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.move_left_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.add_coordinate_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.move_right_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.move_up_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.move_down_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.increase_box_width_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.decrease_box_width_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.increase_box_height_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.decrease_box_height_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.save_crop_button.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.save_image_name_label.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.save_image_name.configure(font=self.master.cropper_tab.font_object)
        self.master.cropper_tab.save_image_extension_combo.configure(font=self.master.cropper_tab.font_object)



def main():
    image_viewer = ImageViewer()
    image_viewer.mainloop()
  
     
if __name__ == '__main__':
    main()
    