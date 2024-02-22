import re
import os
import csv
import sys
import json
import tkintermapview
import datetime
import winsound
import threading
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from idlelib.tooltip import Hovertip
from mag_decl_webscrape import Retrieve_lat_lon, Retrieve_magn_decl
from speleoliti_handler import Speleoliti_online

ctk.set_appearance_mode('light')
ctk.set_default_color_theme('green')

def config():
    """Read configuration settings"""
    global application_path
    """Set the directory of the original file for a path to any other file"""
    if getattr(sys,'frozen', False): #check if the app runs as a script or as a frozen exe file
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    """Read language catalog"""
    global lcat
    file_path = os.path.join(application_path, 'config_settings.json')
    try:
        with open(file_path,'r', encoding='utf-8') as file:
            lcat = json.load(file)
            return lcat['language_setting'], lcat['last_used_software']
    except Exception as ex:
        messagebox.showerror('Error',f'There was an error while reading the file: {ex}')

class SurveyScraper():
    def __init__(self, lc, last_used):
        """Initialise GUI screen"""

        self.gui = ctk.CTk()
        self.gui.title('SurveyScraper')
        self.gui.geometry(f"540x525+200+200") # height x width
        self.gui.resizable(False,False)
        self.gui.columnconfigure(0, weight=6)
        self.gui.columnconfigure(1, weight=1)
        self.md_val = 0 # default value of mag decl
        self.speleoliti_app = None
        self.survey_date = None
        self.cave_name = None
        self.cave_survey_opened = False
        self.original_angles = []
        self.offline = False
        if lc == 'HR':
            self.lc = 0
        elif lc == 'EN':
            self.lc = 1
        self.last_used_software = last_used

        def resource_path(relative_path):
            """ Get absolute path to resource, works for dev and for PyInstaller."""
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                #base_path = os.path.abspath(".")
                base_path = os.path.dirname(__file__)
            return os.path.join(base_path, relative_path)
        # Set path to a current cave survey data
        self.survey_data_file_path = resource_path('survey_data.json') 
        
        # TITLE
        self.gui_title = ctk.CTkLabel(self.gui, text='SurveyScraper v3.0', font=('Roboto', 18))
        self.gui_title.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        # self.use_offline_var = ctk.StringVar(value="off")
        # self.use_offline = ctk.CTkSwitch(self.gui, text="Offline", font=("Roboto",14),
        #                          variable=self.use_offline_var, onvalue="on", offvalue="off")
        # self.use_offline.grid(row=0, column=1, padx=5, pady=5, sticky='e')
        # self.use_offline.deselect()

        self.open_speleoliti_btn = ctk.CTkButton(self.gui, text=f'Speleoliti Online', width=20, font=('Roboto', 15),
                                                 command=self.open_speleoliti)
        self.open_speleoliti_btn.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.lang_var = ctk.StringVar(self.gui)
        self.lang_var.set(lc)
        language_choice = ctk.CTkOptionMenu(self.gui, values=['HR'], variable=self.lang_var, anchor='center', 
                                            font=('Roboto', 15), width=20, command=self.set_language)
        language_choice.grid(row=0, column=3, padx=0, pady=5, sticky='e')

        # TABVIEW
        self.tabview = ctk.CTkTabview(self.gui)
        self.tabview.grid(row=1, column=0, columnspan=4, sticky='ew')
        self.tabview.add('Main')
        self.tabview.add('MagDec')
        self.tabview.add('Help')
        self.tabview._segmented_button.grid(sticky='w')

        ##############################
        #   MAIN TAB FRAME
        self.main_tab_frame = ctk.CTkFrame(self.tabview.tab('Main'))
        self.main_tab_frame.pack(padx=5, pady=5, expand=True, fill="both")
        #
        #   IMPORT FILE SUBFRAME - LEFT
        self.import_frm = ctk.CTkFrame(self.main_tab_frame)
        self.import_frm.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        #
        self.import_frm_lbl = ctk.CTkLabel(self.import_frm, text=f'Uvoz:', font=("Roboto", 14), fg_color='darkgray', corner_radius=5)
        self.import_frm_lbl.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.open_file_img = ctk.CTkImage(Image.open(resource_path(os.path.join('img','open_file.png'))), size=(15,15))
        self.open_file = ctk.CTkButton(self.import_frm, text=f'Otvori vlakove', 
                                    command=self.open_file_event, compound='left', image=self.open_file_img)
        self.open_file.grid(row=1, column=0, padx=(5,5), pady=10, columnspan=2)

        self.opened_file = ctk.CTkLabel(self.import_frm, text='', width=200, height=25, fg_color='white', corner_radius=5)
        self.opened_file.grid(row=2, column=0, padx=5, pady=5, columnspan=2)
        self.opened_file.configure(state='disabled')

        self.survey_sign_lbl = ctk.CTkLabel(self.import_frm, text='Prefiks točaka')
        self.survey_sign_lbl.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.shot_prefix_fld = ctk.CTkEntry(self.import_frm, width=50, height=25)
        self.shot_prefix_fld.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.calc_md_img = ctk.CTkImage(Image.open(resource_path('img/compass.png')), size=(15,15))
        self.show_md_value_lbl = ctk.CTkLabel(self.import_frm, text=f'{lcat["show_md_value_lbl"][self.lc]}:')
        self.show_md_value_lbl.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.show_md_value = ctk.CTkEntry(self.import_frm, width=50, height=25, fg_color='white', corner_radius=5)
        self.show_md_value.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        self.parse_img = ctk.CTkImage(Image.open(resource_path('img/generate.png')), size=(15,15))
        self.apply_fix_md_btn = ctk.CTkButton(self.import_frm, text='Pohrani postavke', command=self.save_json,
                                              compound='left', image=self.parse_img)
        self.apply_fix_md_btn.grid(row=5, column=0, padx=(5,5), pady=5, columnspan=2)
        self.apply_fix_md_btn.configure(state='disabled')

        #   EXPORT FILE SUBFRAME - LEFT
        self.export_frm = ctk.CTkFrame(self.main_tab_frame)
        self.export_frm.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        #
        self.export_frm_lbl = ctk.CTkLabel(self.export_frm, text=f'Izvoz:', font=("Roboto",14), fg_color='darkgray', corner_radius=5)
        self.export_frm_lbl.pack(padx=5, pady=5, fill='both')
        # self.save_json_file = ctk.CTkButton(self.export_frm, text='Pohrani', command=self.save_json,
        #                                 compound='left', image=self.parse_img)
        #self.save_json_file.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        # self.save_json_file.pack(padx=5, pady=5)
        # self.save_json_file.configure(state='disabled')
        self.save_csv_file = ctk.CTkButton(self.export_frm, text='Izvezi u CSV', command=self.store_to_csv,
                                        compound='left', image=self.parse_img)
        self.save_csv_file.pack(padx=5, pady=5)
        self.save_csv_file.configure(state='disabled')
        self.export_original_angle_var = ctk.StringVar(value="on")
        self.export_original_angle = ctk.CTkSwitch(self.export_frm, text="Dodaj stupac izvornih azimuta", font=("Roboto",10),
                                 variable=self.export_original_angle_var, onvalue="on", offvalue="off")
        self.export_original_angle.pack(padx=5, pady=5)
        self.export_original_angle.deselect()
        self.export_original_angle.configure(state='disabled')
        # self.open_gen_file = ctk.CTkButton(self.export_frm, text=f'{lcat["open_gen_file"][self.lc]}', 
        #                                 #command=lambda: os.system('"%s"' % write_csv_file_path),
        #                                 command=open_subprocess,
        #                                 compound='left', image=self.open_file_img)
        # self.open_gen_file.grid(row=5, column=0, padx=5, pady=5)
        # self.open_gen_file.configure(state='disabled')
        self.success_run = ctk.CTkLabel(self.export_frm, text='', height=25, width=200, fg_color='white', corner_radius=5)
        #self.success_run.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        self.success_run.pack(padx=5, pady=5, fill='both')
        self.success_run.configure(state='disabled')

        ##############################
        #   MAIN TAB FRAME - RIGHT
        #   CAVE DATA SUBFRAME
        mtf_entry_width = 120
        self.cave_data_frame = ctk.CTkFrame(self.main_tab_frame, height=450)
        self.cave_data_frame.grid(row=0, rowspan=2, column=1, padx=5, pady=5, sticky='nsew')
        #
        # Cave name
        self.cave_name_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'Ime objekta: ', font=("Roboto", 14), 
                                          fg_color='darkgray', corner_radius=5)
        self.cave_name_lbl.grid(row=0, column=0, padx=5, pady=5, ipadx=35, sticky='e')
        self.cave_name_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.cave_name_fld.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        # X
        self.X_lbl = ctk.CTkLabel(self.cave_data_frame, text='Koordinata X: ')
        self.X_lbl.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.X = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.X.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        # Y
        self.Y_lbl = ctk.CTkLabel(self.cave_data_frame, text='Koordinata Y: ')
        self.Y_lbl.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.Y = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.Y.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        # Z
        self.Z_lbl = ctk.CTkLabel(self.cave_data_frame, text='Nadmorska visina Z: ')
        self.Z_lbl.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.Z = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.Z.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        # File Name
        self.file_name_lbl = ctk.CTkLabel(self.cave_data_frame, text='Ime datoteke za pohranu: ')
        self.file_name_lbl.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.file_name_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width+30, height=25)
        self.file_name_fld.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        # Description
        # self.description_lbl = ctk.CTkLabel(self.cave_data_frame, text='Opis: ')
        # self.description_lbl.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        # self.description = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        # self.description.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        # Fixed point
        self.fixed_station_lbl = ctk.CTkLabel(self.cave_data_frame, text='Fiksna točka: ')
        self.fixed_station_lbl.grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.fixed_station_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.fixed_station_fld.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        # Poly Length
        self.poly_length_lbl = ctk.CTkLabel(self.cave_data_frame, text='Poligonalna duljina: ')
        self.poly_length_lbl.grid(row=7, column=0, padx=5, pady=5, sticky='e')
        self.poly_length_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.poly_length_fld.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        # Horizontal Length
        self.hor_length_lbl = ctk.CTkLabel(self.cave_data_frame, text='Horizontalna duljina: ')
        self.hor_length_lbl.grid(row=8, column=0, padx=5, pady=5, sticky='e')
        self.hor_length_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.hor_length_fld.grid(row=8, column=1, padx=5, pady=5, sticky='w')
        # Elevation
        self.elevation_lbl = ctk.CTkLabel(self.cave_data_frame, text='Visinska razlika: ')
        self.elevation_lbl.grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.elevation_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.elevation_fld.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        # Depth
        self.depth_lbl = ctk.CTkLabel(self.cave_data_frame, text='Dubina od fiksne točke: ')
        self.depth_lbl.grid(row=10, column=0, padx=5, pady=5, sticky='e')
        self.depth_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.depth_fld.grid(row=10, column=1, padx=5, pady=5, sticky='w')

        ##############################
        #   MAG DECL TAB FRAME
        self.mag_decl_tab_frame = ctk.CTkFrame(self.tabview.tab('MagDec'))
        self.mag_decl_tab_frame.pack(padx=5, pady=5, expand=True, fill="both")
        #
        #   LOCATION SUBFRAME - LEFT
        self.location_frame = ctk.CTkFrame(self.mag_decl_tab_frame)
        self.location_frame.grid(row=0, column=0, rowspan=4, padx=(5,5), pady=5, sticky='nsew')
        #
        self.location_frm_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["location_frm_label"][self.lc]}:', font=('Roboto', 14))
        self.location_frm_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(5,0), sticky='ew')
        self.location_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["location_label"][self.lc]}: ', font=('Roboto', 12))
        self.location_label.grid(row=1, column=0, padx=10, pady=(5,0), sticky='e')
        self.location_input = ctk.CTkEntry(self.location_frame, width=150, height=20, font=('Roboto', 12))
        self.location_input.grid(row=1, column=1, padx=10, pady=(5,0))
        self.get_coord_btn = ctk.CTkButton(self.location_frame, width=150, text=f'{lcat["get_coord_btn_label"][self.lc]}',
                                        command=lambda: self.get_location(self.location_input.get()))
        self.get_coord_btn.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        Hovertip(self.location_input,f'{lcat["hovertip"][self.lc]}', hover_delay=500)
        self.lat_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["lat_label"][self.lc]}: ', font=('Roboto', 12))
        self.lat_label.grid(row=3, column=0, padx=(5,0), pady=(5,0), sticky='e')
        self.lat_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lat_input.grid(row=3, column=1, padx=0, pady=(5,0))
        self.lat_N = ctk.CTkLabel(self.location_frame, text="N", font=('Roboto', 12))
        self.lat_N.grid(row=3, column=2, padx=(5,10), pady=(5,0), sticky='ew')
        self.lon_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["lon_label"][self.lc]}: ', font=('Roboto', 12))
        self.lon_label.grid(row=4, column=0, padx=(5,0), pady=(5,0), sticky='e')
        self.lon_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lon_input.grid(row=4, column=1, padx=0, pady=(5,0))
        self.lon_E = ctk.CTkLabel(self.location_frame, text="E", font=('Roboto', 12))
        self.lon_E.grid(row=4, column=2, padx=(5,10), pady=(5,0), sticky='ew')

        self.map = tkintermapview.TkinterMapView(self.location_frame, width=150, height=300, corner_radius=15)
        self.map.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.map.set_position(float(lcat["map.set_position_x"][self.lc]), float(lcat["map.set_position_y"][self.lc]))
        self.map.set_zoom(int(lcat["map.set_zoom"][self.lc]))

        #   MODEL SUBFRAME - RIGHT
        self.model_frame = ctk.CTkFrame(self.mag_decl_tab_frame)
        self.model_frame.grid(row=0, column=1, padx=(0,5), pady=5, sticky='nsew')
        self.model_frame.columnconfigure((0,1), weight=1)
        #
        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:", font=('Roboto', 14))
        self.model_label.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        self.model = ctk.StringVar()
        current_date = datetime.date.today()
        current_day = current_date.strftime('%d')
        current_month = current_date.strftime('%m')
        current_year = current_date.strftime('%Y')
        def refresh_year():
            if self.model.get() == 'WMM':
                year_range = [str(y) for y in range(2019,int(current_year)+2)]
            elif self.model.get() == 'IGRF':
                year_range = [str(y) for y in range(1590,int(current_year)+2)]
            self.year_combo.configure(values=sorted(year_range, reverse=True))

        self.model_wmm = ctk.CTkRadioButton(self.model_frame, text='WMM (2019-2024)', value='WMM', variable=self.model, command=refresh_year)
        self.model_wmm.grid(row=1, column=0, padx=30, pady=5, sticky='w')
        self.model_wmm.select()
        self.model_igrf = ctk.CTkRadioButton(self.model_frame, text='IGRF (1590-2024)', value='IGRF', variable=self.model, command=refresh_year)
        self.model_igrf.grid(row=2, column=0, padx=30, pady=5, sticky='w')

        #   DATE SUBFRAME
        self.date_frame = ctk.CTkFrame(self.mag_decl_tab_frame)
        self.date_frame.grid(row=1, column=1, padx=(0,5), pady=5, sticky='nsew')
        self.date_frame.columnconfigure((0,1), weight=1)
        #
        self.date_label = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_label"][self.lc]}: ', font=('Roboto', 14))
        self.date_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
        self.date_day = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_day"][self.lc]}:')
        self.date_day.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.selected_day = ctk.StringVar(value=current_day)
        self.day_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,32)], variable=self.selected_day)
        self.day_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.date_month = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_month"][self.lc]}:')
        self.date_month.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.selected_month = ctk.StringVar(value=current_month)
        self.month_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,13)], variable=self.selected_month)
        self.month_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.date_year = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_year"][self.lc]}:')
        self.date_year.grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.selected_year = ctk.StringVar(value=current_year)
        year_range = [str(y) for y in range(2019,int(current_year)+2)]
        self.year_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=sorted(year_range, reverse=True), variable=self.selected_year)
        self.year_combo.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        #   CALCULATION SUBFRAME
        self.decl_frame = ctk.CTkFrame(self.mag_decl_tab_frame)
        self.decl_frame.grid(row=2, column=1, padx=(0,5), pady=5, sticky='nsew')
        self.decl_frame.columnconfigure((0,1), weight=1)
        #
        self.calc_md_btn = ctk.CTkButton(self.decl_frame, width=125, text=f'{lcat["calc_md_btn"][self.lc]}',
                                        command=lambda: self.get_md(self.model.get(),self.year_combo.get(),self.month_combo.get(),self.day_combo.get()))
        self.calc_md_btn.grid(row=0, column=0, columnspan=3, padx=5, pady=10)
        self.md_value_lbl = ctk.CTkLabel(self.decl_frame, text=f'{lcat["md_value_lbl"][self.lc]}:')
        self.md_value_lbl.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.md_value = ctk.CTkEntry(self.decl_frame, width=50, height=25, fg_color='white', corner_radius=5)
        self.md_value.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.md_value.configure(state='disabled')

        ##############################
        #   HELP TAB FRAME
        self.help_tab_frame = ctk.CTkFrame(self.tabview.tab('Help'))
        self.help_tab_frame.pack(padx=5, pady=5, expand=True, fill="both")

        # find the readme file against dynamic app location
        readme_file_path = os.path.join(application_path, f'{lcat["readme_file_path"][self.lc]}') 
        readme_text = ctk.CTkTextbox(self.help_tab_frame, height=425, wrap='word')
        readme_text.pack(padx=5, pady=5, expand=True, fill="both")
        try:
            with open(readme_file_path,'r', encoding='utf-8') as readme_file:
                text = readme_file.read()
            #processed_text = text.replace('\n', ' ')    
            readme_text.insert('0.0', text)
        except IOError as error:
            readme_text.insert('0.0',f'{lcat["readme_text"][self.lc]}\n{error}')
        readme_text.configure(state='disabled')

        #   RUN GUI
        self.gui.mainloop()
        
    #   MAIN MENU BUTTONS
    def open_speleoliti(self):
        # open loading window in GUI and begin process
        self.loading_window = ctk.CTkToplevel(self.gui)
        self.loading_window.title('SurveyScraper')
        self.loading_window.attributes('-topmost', True)
        self.gui.eval(f'tk::PlaceWindow {str(self.loading_window)} center')
        loading_label = ctk.CTkLabel(self.loading_window, text="Otvaram Speleoliti online...", font=("Roboto",14))
        loading_label.pack(padx=50, pady=(25,25), expand=True, fill="x")
        self.gui.update()
        try:
            self.speleoliti_app = Speleoliti_online(headless=False, survey_path=self.survey_data_file_path)
            if self.speleoliti_app.online:
                self.speleoliti_app.driver.get('chrome://settings/')
                self.speleoliti_app.driver.execute_script('chrome.settingsPrivate.setDefaultZoom(1.5);')   # Set zoom level to 150%
                if self.cave_survey_opened: # If there is a cave survey opened, open it
                    self.speleoliti_app.open_object()
                    self.speleoliti_app.update_fixed_station(self.fixed_station)
                else:
                    self.speleoliti_app.open_empty_object()
                self.speleoliti_app.restore_window()
            else:
                messagebox.showerror('Error', f'Nije moguće otvoriti Speleoliti Online bez internet veze!')
            self.loading_window.destroy()
        except Exception as e:
            messagebox.showerror('Error', f'Pogreška prilikom otvaranja Speleoliti online\n\n{e}\n Molim pokušaj ponovo kasnije.')
    
    def set_language(self, language='HR'):
        # Change language 
        lcat['language_setting'] = language
        if language == 'HR': 
             messagebox.showinfo(message='Za promjenu jezika molim ponovno pokreni program!')
        elif language == 'EN':
             messagebox.showinfo(message='For changing the language please restart the program!')
        # store language setting to a language catalog file
        file_path = os.path.join(application_path, 'config_settings.json')
        with open(file_path, 'w') as fileWriter:
            json.dump(lcat, fileWriter, indent=4)

    #   CAVE SURVEY FILE IMPORT
    def open_file_event(self):
        """Open raw cave survey data file csv or txt, create json and execute parsing"""

        # Suggest the recent software to open file from
        filetypes = (("CSV file","*.csv"), ("Text file","*.txt*"), ("Walls file","*.srv*"), ("All files","*"))
        software_to_file = {
            "TopoDroid":"CSV file",
            "PocketTopo":"Text file",
            "Qave":"Walls file"
        }
        filetypes = sorted(filetypes, key=lambda ft: ft[0] != software_to_file[self.last_used_software])
        self.file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', 
                    title=f'{lcat["file_path"][self.lc]}', filetypes = filetypes)
        if self.file_path.endswith('.csv'):
            self.software = 'TopoDroid'
        elif self.file_path.endswith('.txt'):
            self.software = 'PocketTopo'    
        elif self.file_path.endswith('.srv'):
            self.software = 'Qave'
        else:
            #messagebox.showerror('Error',f'{lcat["file_path_error"][self.lc]}')
            self.file_path = None
        # Continue with reading and processing the file
        if self.file_path:
            # Set the last used software and store to config file
            lcat['last_used_software'] = self.software
            file_path = os.path.join(application_path, 'config_settings.json')
            with open(file_path, 'w') as fileWriter:
                json.dump(lcat, fileWriter, indent=4)
            # Make changes if the file opens correctly
            file_base_name = os.path.basename(self.file_path)
            self.suggested_name_for_file = os.path.splitext(file_base_name)[0] + f'{lcat["sufix"][self.lc]}'
            self.cave_survey_json_data = {"fix": "","x": "","y": "","z": "","dcl": "","name": "","descr": "","viz": ["null"]}
            self.create_json() # create empty json file
            self.parse_event(self.software)
            # continue if parsed successfully
            if parsed:
                self.cave_survey_opened = True
                # Update GUI
                if self.cave_name:
                    self.cave_name_fld.delete(0, ctk.END)   # overwrite
                    self.cave_name_fld.insert(0, self.cave_name) #missing for pockettopo and qave
                if self.file_name_fld:
                    self.file_name_fld.delete(0, ctk.END)   # overwrite
                    self.file_name_fld.insert(0, f'{self.suggested_name_for_file}')
                if not self.offline:
                    self.fixed_station_fld.delete(0, ctk.END)
                    self.fixed_station_fld.insert(0, self.fixed_station)
                    self.poly_length_fld.configure(text=f'{float(self.poly_length):.1f} m')
                    self.hor_length_fld.configure(text=f'{float(self.hor_length):.1f} m')
                    self.elevation_fld.configure(text=f'{float(self.elevation):.1f} m')
                    self.depth_fld.configure(text=f'{float(self.depth):.1f} m')
                if self.survey_date:
                    self.selected_day.set(str(self.survey_date.day))
                    self.selected_month.set(str(self.survey_date.month))
                    self.selected_year.set(str(self.survey_date.year))
                self.opened_file.configure(text=file_base_name)
                self.apply_fix_md_btn.configure(state='normal')
                self.save_csv_file.configure(state='normal')
                self.gui.update()
            else:
                messagebox.showerror('Error','Error due to failed cave survey file parsing!')
    
    # APPLY CHANGES
    def save_json(self):
        """Apply prefix and mag decl to cave_survey_json_data and save"""

        self.cave_survey_json_data['name'] = self.cave_name_fld.get()
        self.cave_survey_json_data['x'] = self.X.get()
        self.cave_survey_json_data['y'] = self.Y.get()
        self.cave_survey_json_data['z'] = self.Z.get()
        # save prefix
        if not hasattr(self, 'original_fixed_station_name'):
            self.original_fixed_station_name = self.fixed_station_fld.get()
        new_shot_prefix = self.shot_prefix_fld.get()
        self.cave_survey_json_data['descr'] = new_shot_prefix
        if self.original_fixed_station_name:
            new_fixed_station_name = f"{new_shot_prefix}{self.original_fixed_station_name}"
            self.cave_survey_json_data['fix'] = new_fixed_station_name
        # save md val
        if not hasattr(self, 'original_shots'):
            self.original_shots = [{'t1': shot['t1'], 't2': shot['t2'], 'a': shot['a']} for shot in self.cave_survey_json_data['viz'][1:]]
        if self.show_md_value.get():
            try:
                md_value_str = self.show_md_value.get().split('°')[0]
                self.md_val = float(md_value_str.replace(',', '.')) % 360
                if float(md_value_str) >= 360:
                    self.show_md_value.delete(0, 'end')
                    self.show_md_value.insert(0,f'{self.md_val}°')
            except ValueError:
                messagebox.showerror('Error',f'Pogrešan unos magnetske deklinacije!')
            self.cave_survey_json_data['dcl'] = self.md_val
            self.export_original_angle.configure(state='normal') # enable option for storing original angles if md is set
        for original_shot, shot in zip(self.original_shots, self.cave_survey_json_data['viz'][1:]):
            shot['t1'] = f"{new_shot_prefix}{original_shot['t1']}"
            shot['t2'] = f"{new_shot_prefix}{original_shot['t2']}"
            shot['a'] = round((float(original_shot['a']) + self.md_val) % 360,2)
            shot['l'] = round(float(shot['l']),3)
            shot['f'] = round(float(shot['f']),2)
        # save to json
        with open(write_json_file_path, 'w') as file:
            json.dump(self.cave_survey_json_data, file, indent=4) 
        # update gui
        if self.fixed_station_fld.get():
            self.fixed_station_fld.delete(0, ctk.END)
            self.fixed_station_fld.insert(0, new_fixed_station_name)
        self.success_run.configure(text='Pohranjeno!')
        winsound.MessageBeep()
        self.gui.update()

    # CAVE SURVEY FILE EXPORT 
    def create_json(self):
        """Create empty cave survey data JSON file"""
        global write_json_file_path
        write_json_file_path = os.path.join(application_path, 'survey_data.json')
        with open(write_json_file_path, 'w') as file:
            json.dump(self.cave_survey_json_data, file, indent=4)      

    def store_to_csv(self):
        """Store cave survey data to CSV file"""

        shot_prefix = self.cave_survey_json_data['descr']
        if hasattr(self,'file_name_fld'):
            self.suggested_name_for_file = self.file_name_fld.get()
        if shot_prefix == '' and self.software == 'PocketTopo': # raise warning if exporting shots from Speleoliti without prefix
            messagebox.showwarning('Warning',f'{lcat["sign_warning"][self.lc]}')
        write_csv_file_path = ctk.filedialog.asksaveasfilename(initialdir='SurveyScraper', title=f'{lcat["write_csv_file_path"][self.lc]}', 
                                                    defaultextension=".csv", initialfile=f'{self.suggested_name_for_file}')
        try:
            with open(write_csv_file_path, 'w', newline='') as csv_file:
                if not self.offline:
                    description = (f"Ime objekta:,{self.cave_survey_json_data['name']}\n"
                                    f"X:,{self.cave_survey_json_data['x']}\n"
                                    f"Y:,{self.cave_survey_json_data['y']}\n"
                                    f"Z:,{self.cave_survey_json_data['z']}\n"
                                    f"Fiksna točka:,{self.cave_survey_json_data['fix']}\n"
                                    f"Magn. deklinacija:,{self.cave_survey_json_data['dcl']}\n"
                                    f"Poligonalna duljina:,{float(self.poly_length):.1f}\n"
                                    f"Horizontalna duljina:,{float(self.hor_length):.1f}\n"
                                    f"Visinska razlika:,{float(self.elevation):.1f}\n"
                                    f"Dubina od fiksne točke:,{float(self.depth):.1f}\n")
                else:
                    description = (f"Ime objekta:,{self.cave_survey_json_data['name']}\n"
                                    f"X:,{self.cave_survey_json_data['x']}\n"
                                    f"Y:,{self.cave_survey_json_data['y']}\n"
                                    f"Z:,{self.cave_survey_json_data['z']}\n"
                                    f"Fiksna točka:,{self.cave_survey_json_data['fix']}\n")
                csv_file.write(description)
                fieldnames = list(self.cave_survey_json_data['viz'][1].keys())
                if self.export_original_angle_var.get() == 'on':
                    fieldnames += ['a_original']
                    shots_to_process = zip(self.cave_survey_json_data['viz'][1:], self.original_shots)
                else:
                    # Create an iterator of shots without pairing with original_shots
                    shots_to_process = ((shot, None) for shot in self.cave_survey_json_data['viz'][1:])  
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for shot, original_shot in shots_to_process:
                    shot_copy = shot.copy()
                    if original_shot is not None:
                        shot_copy['a_original'] = round(float(original_shot['a']),2)
                    writer.writerow(shot_copy)
                fieldnames = []
            self.success_run.configure(text='CSV pohranjen!')
            winsound.MessageBeep()
        except IOError:
            messagebox.showerror('Error',f'{lcat["IOError"][self.lc]}')
        
    # SPELEOLITI CALCULATION FUNCTION
    def run_speleoliti_calculation(self):
        #try:
        self.speleoliti_app_headless = Speleoliti_online(headless=True, survey_path=self.survey_data_file_path)
        if self.speleoliti_app_headless.online:
            # refresh toplevel window GUI
            opening_speleoliti_label = ctk.CTkLabel(self.loading_window, text="Povezujem se sa Speleoliti online...")
            opening_speleoliti_label.pack(padx=10, pady=(0,25), fill="both")
            self.gui.update()
            # continue with Speleoliti process
            self.speleoliti_app_headless.open_object()
            self.fixed_station = self.speleoliti_app_headless.find_highest_point()
            self.speleoliti_app_headless.update_fixed_station(self.fixed_station)
            self.poly_length, self.hor_length, self.elevation, self.depth = self.speleoliti_app_headless.retrieve_cave_data()
            self.speleoliti_app_headless.close_driver()
            # except Exception as e:
            #     messagebox.showerror('Error', f'Pogreška prilikom obrade u Speleolitima!\n\n{e}')
            self.cave_survey_json_data['fix'] = self.fixed_station # set fixed station by default
            self.cave_survey_json_data['name'] = self.cave_name
        else:
            self.offline = True
            messagebox.showwarning('Warning','Preskačem obradu u Speleoliti Online jer nema internet veze!')

    # CAVE SURVEY FILE PARSE FUNCTIONS
    def parse_event(self, software):
        """Parse event executes cave survey file parsing, speleoliti calculation and saving into json"""
        global parsed
        parsed = False
        # load processing window in GUI and begin process
        self.loading_window = ctk.CTkToplevel(self.gui)
        self.loading_window.title('SurveyScraper')
        self.loading_window.attributes('-topmost', True)
        self.gui.eval(f'tk::PlaceWindow {str(self.loading_window)} center')
        #self.loading_window.eval('tk::PlaceWindow . center')
        loading_label = ctk.CTkLabel(self.loading_window, text="Obrađujem, molim pričekaj...")
        loading_label.pack(padx=50, pady=(25,25), expand=True, fill="x")
        self.gui.update()
        # start parsing
        if software == 'TopoDroid':
            parsed = self.parse_topodroid()
        elif software == 'Qave':
            parsed = self.parse_qave()
        elif software == 'PocketTopo':
            parsed = self.parse_pockettopo()
        if parsed:
            try:
                threading.Thread(target=self.run_speleoliti_calculation()).start()
                winsound.MessageBeep()
                self.success_run.configure(text='Uspješan uvoz i obrada!')
            except Exception as e:
                parsed = False
                self.success_run.configure(text='Neuspješan uvoz i obrada!')
            self.loading_window.destroy()
        self.gui.update()

    def parse_pockettopo(self):
        with open(self.file_path,'r') as file:
            for _ in range(6):
                next(file)   
            three_shots = [] #a temporary shot list
            for row in file:
                row_data = re.sub(r'\[.\]','',row) # remove brackets
                row_data = re.sub(r'<','',row_data) # remove arrows
                shot = row_data.split() #a list of shot data
                if len(shot) == 5: #filter for main shots (5 fields - from, to, l, angl, incl)
                    three_shots.append(shot) # store first shot of main shots
                    #if the next shot name is different than the previous shot, save the single shot in three_shots, else append to the list
                    if len(three_shots) == 2 and (three_shots[1][0] != three_shots[0][0] or three_shots[1][1] != three_shots[0][1]): 
                        main_shot = {
                            "t1": three_shots[0][0],
                            "t2": three_shots[0][1],
                            "l": f'{float(three_shots[0][2]):.3f}',
                            "a": f'{float(three_shots[0][3]):.3f}',
                            "f": f'{float(three_shots[0][4]):.3f}',
                            "left": "null",
                            "right": "null",
                            "up": "null",
                            "down": "null",
                            "note": "",
                            "flags": ""
                        }
                        self.cave_survey_json_data["viz"].append(main_shot)
                        three_shots.pop(0) # remove first shot from the list
                    elif len(three_shots) == 3:
                        mean_len = (float(three_shots[0][2])+float(three_shots[1][2])+float(three_shots[2][2]))/3
                        mean_dir = (float(three_shots[0][3])+float(three_shots[1][3])+float(three_shots[2][3]))/3
                        mean_inc = (float(three_shots[0][4])+float(three_shots[1][4])+float(three_shots[2][4]))/3
                        main_shot = {
                            "t1": three_shots[0][0],
                            "t2": three_shots[0][1],
                            "l": mean_len,
                            "a": mean_dir,
                            "f": mean_inc,
                            "left": "null",
                            "right": "null",
                            "up": "null",
                            "down": "null",
                            "note": "",
                            "flags": ""
                        }
                        self.cave_survey_json_data["viz"].append(main_shot)
                        three_shots.clear()                    
        with open(write_json_file_path, 'w') as file:
            json.dump(self.cave_survey_json_data, file, indent=4) 
        parsed = True
        return parsed

    def parse_topodroid(self):
        with open(self.file_path,'r') as file:
            date = next(file).split(',')[0][2:12]
            self.survey_date = datetime.datetime.strptime(date, "%Y.%m.%d")
            self.cave_name = next(file).split(',')[0][2:]
            next(file)
            next(file)
            for row in file:
                shot = row.split(',')         
                if shot[1] != '-': #filter for main shots
                    shot_from = shot[0][0:shot[0].find('@')]
                    shot_to = shot[1][0:shot[1].find('@')]
                    main_shot = {
                                "t1": shot_from,
                                "t2": shot_to,
                                "l": float(shot[2]),
                                "a": float(shot[3]),
                                "f": float(shot[4]),
                                "left": "null",
                                "right": "null",
                                "up": "null",
                                "down": "null",
                                "note": "",
                                "flags": ""
                            }
                    self.cave_survey_json_data["viz"].append(main_shot)
        with open(write_json_file_path, 'w') as file:
            json.dump(self.cave_survey_json_data, file, indent=4) 
        parsed = True
        return parsed
    
    def parse_qave(self):
        with open(self.file_path,'r') as file:
            for _ in range(4):
                next(file)
            date = next(file).split(' ')[1].strip()
            self.survey_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            next(file)
            next(file)
            for row in file:
                shot = row.strip().split('\t')         
                if shot[1] != '-': #filter for main shots
                    main_shot = { 
                                "t1": shot[0],
                                "t2": shot[1],
                                "l": float(shot[2]),
                                "f": float(shot[4]),
                                "a": float(shot[3]),
                                "left": "null",
                                "right": "null",
                                "up": "null",
                                "down": "null",
                                "note": "",
                                "flags": ""
                            }
                    self.cave_survey_json_data["viz"].append(main_shot)
                else:
                    break
        with open(write_json_file_path, 'w') as file:
            json.dump(self.cave_survey_json_data, file, indent=4) 
        parsed = True
        return parsed

    #   MAGNETIC DECLINATION FUNCTIONS
    def get_location(self, location):
        global latitude, longitude
        if location != '':
            try:
                self.lat_input.delete(0, ctk.END)
                self.lon_input.delete(0, ctk.END)
                lat_lon_app = Retrieve_lat_lon(location)
                latitude, longitude = lat_lon_app.retrieve_lat_lon()
                self.lat_input.insert(0, f'{latitude:.4f}')
                self.lon_input.insert(0, f'{longitude:.4f}')
                self.map.set_address(location, marker=True)
                self.map.set_zoom(13)
            except:
                messagebox.showerror('Error','Nije moguće dohvatiti koordinate! Provjeri internet vezu!')
        else:
            messagebox.showerror('Error',f'{lcat["location_error"][self.lc]}')

    def get_md(self, model, year, month, day):
        try:
            datetime.datetime(int(year),int(month),int(day))
        except ValueError:
            messagebox.showerror('Error',f'{lcat["datetime.ValueError"][self.lc]}')
        if self.lat_input.get() == '' or self.lon_input.get() == '':
            messagebox.showerror('Error',f'{lcat["lat_lon_input_error"][self.lc]}')
        else:
            try:
                magn_decl_app = Retrieve_magn_decl(float(self.lat_input.get()), float(self.lon_input.get()), model, year, month, day)
                self.md_val = float(f'{magn_decl_app.retrieve_magn_decl():.3f}')
                self.md_value.configure(state='normal')
                current_text = len(self.md_value.get())
                if current_text > 0:
                    self.md_value.delete(0, 'end') # override whatever present  
                self.md_value.insert(0,f'{self.md_val}°') # show md in magdec window
                self.md_value.configure(state='disabled') # which you cannot change
                current_text = len(self.show_md_value.get())
                if current_text > 0:
                    self.show_md_value.delete(0, 'end') # override whatever present  
                self.show_md_value.insert(0,f'{self.md_val}°') # refresh the md value in the main gui window
            except:
                messagebox.showerror('Error','Nije moguće izračunati magnetsku deklinaciju! Provjeri internet vezu!')

if __name__ == '__main__':
    lang, last_used = config() # Run config right at the start
    SurveyScraper(lang, last_used)