import os
import sys
import datetime
import winsound

import tkintermapview
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from idlelib.tooltip import Hovertip
# Project package — used for paths, i18n, logging, parsers, services, and
# config IO. Older call sites still read `lcat` and `application_path` as
# module-level globals; the `config()` function below populates those from
# the package modules so the legacy widget code keeps working unchanged.
from surveyscraper import paths as _sp_paths
from surveyscraper import parsers as _parsers
from surveyscraper.core.errors import NetworkError as _NetworkError
from surveyscraper.core.errors import ParseError as _ParseError
from surveyscraper.core.errors import SpeleolitiError as _SpeleolitiError
from surveyscraper.logging_setup import configure_logging, get_logger
from surveyscraper.services import config_store as _config_store
from surveyscraper.services import exporter as _exporter
from surveyscraper.services import magdec as _magdec
from surveyscraper.services.speleoliti import SpeleolitiOnline as _SpeleolitiOnline
from surveyscraper.__init__ import __version__ as _version

ctk.set_appearance_mode('light')
ctk.set_default_color_theme('green')

_log = configure_logging()


def config():
    """Read configuration settings."""
    global application_path
    application_path = _sp_paths.APPLICATION_PATH

    global lcat
    try:
        lcat = _config_store.read_config()
        _log.info("Loaded config_settings.json (lang=%s, last_used=%s)",
                  lcat.get('language_setting'), lcat.get('last_used_software'))
        return lcat['language_setting'], lcat['last_used_software']
    except Exception as ex:
        _log.exception("Failed to read config_settings.json")
        messagebox.showerror('Error', f'There was an error while reading the file: {ex}')

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
        self.version = 'v'+_version

        if lc == 'HR':
            self.lc = 0
        elif lc == 'EN':
            self.lc = 1
        self.last_used_software = last_used

        # Set path to a current cave survey data
        self.survey_data_file_path = os.path.join(application_path, 'survey_data.json')
        
        # Store commonly used values
        self.image_size = (20, 20)
        self.img_path = os.path.join(application_path, 'img')
        
        # Cache loaded images for better performance
        self.images = {
            'compass': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'compass.png')), size=self.image_size),
            'coordinates': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'coordinates.png')), size=self.image_size),
            'export_csv': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'export_csv.png')), size=self.image_size),
            'generate': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'generate.png')), size=self.image_size),
            'open_file': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'open_file.png')), size=self.image_size),
            'speleoliti': ctk.CTkImage(Image.open(os.path.join(self.img_path, 'speleoliti.png')), size=self.image_size),
        }

        # TITLE
        self.gui_title = ctk.CTkLabel(self.gui, text=f'SurveyScraper {self.version}', font=('Roboto', 18))
        self.gui_title.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.open_speleoliti_btn = ctk.CTkButton(self.gui, text=f'Speleoliti Online', width=20, font=('Roboto', 15),
                                                 command=self.open_speleoliti, compound='left', image=self.images['speleoliti'])
        self.open_speleoliti_btn.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.lang_var = ctk.StringVar(self.gui)
        self.lang_var.set(lc)
        language_choice = ctk.CTkOptionMenu(self.gui, values=['HR', 'EN'], variable=self.lang_var, anchor='center', 
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
        self.import_frm_lbl = ctk.CTkLabel(self.import_frm, text=f'{lcat["import_frm_lbl"][self.lc]}:', font=("Roboto", 14), fg_color='darkgray', corner_radius=5)
        self.import_frm_lbl.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        self.open_file = ctk.CTkButton(self.import_frm, text=f'{lcat["open_file"][self.lc]}', 
                                    command=self.open_file_event, compound='left', image=self.images['open_file'])
        self.open_file.grid(row=1, column=0, padx=(5,5), pady=10, columnspan=2)

        self.opened_file = ctk.CTkLabel(self.import_frm, text='', width=200, height=25, fg_color='white', corner_radius=5)
        self.opened_file.grid(row=2, column=0, padx=5, pady=5, columnspan=2)
        self.opened_file.configure(state='disabled')

        self.survey_sign_lbl = ctk.CTkLabel(self.import_frm, text=f'{lcat["survey_sign_lbl"][self.lc]}')
        self.survey_sign_lbl.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.shot_prefix_fld = ctk.CTkEntry(self.import_frm, width=50, height=25)
        self.shot_prefix_fld.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        self.show_md_value_lbl = ctk.CTkLabel(self.import_frm, text=f'{lcat["show_md_value_lbl"][self.lc]}:')
        self.show_md_value_lbl.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.show_md_value = ctk.CTkEntry(self.import_frm, width=50, height=25, fg_color='white', corner_radius=5)
        self.show_md_value.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        self.apply_fix_md_btn = ctk.CTkButton(self.import_frm, text=f'{lcat["apply_fix_md_btn"][self.lc]}', command=self.save_json,
                                              compound='left', image=self.images['generate'])
        self.apply_fix_md_btn.grid(row=5, column=0, padx=(5,5), pady=5, columnspan=2)
        self.apply_fix_md_btn.configure(state='disabled')

        #   EXPORT FILE SUBFRAME - LEFT
        self.export_frm = ctk.CTkFrame(self.main_tab_frame)
        self.export_frm.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        #
        self.export_frm_lbl = ctk.CTkLabel(self.export_frm, text=f'{lcat["export_frm_lbl"][self.lc]}:', font=("Roboto",14), fg_color='darkgray', corner_radius=5)
        self.export_frm_lbl.pack(padx=5, pady=5, fill='both')
        self.save_csv_file = ctk.CTkButton(self.export_frm, text=f'{lcat["save_csv_file"][self.lc]}', command=self.store_to_csv,
                                        compound='left', image=self.images['export_csv'])
        self.save_csv_file.pack(padx=5, pady=5)
        self.save_csv_file.configure(state='disabled')
        self.export_original_angle_var = ctk.StringVar(value="on")
        self.export_original_angle = ctk.CTkSwitch(self.export_frm, text=f'{lcat["export_original_angle"][self.lc]}', font=("Roboto",10),
                                 variable=self.export_original_angle_var, onvalue="on", offvalue="off")
        self.export_original_angle.pack(padx=5, pady=5)
        self.export_original_angle.deselect()
        self.export_original_angle.configure(state='disabled')
        self.keep_splays_var = ctk.StringVar(value="off")
        self.keep_splays = ctk.CTkSwitch(self.export_frm, text=f'{lcat["keep_splays"][self.lc]}', font=("Roboto",10),
                                 variable=self.keep_splays_var, onvalue="on", offvalue="off")
        self.keep_splays.pack(padx=5, pady=5)
        self.keep_splays.deselect()
        self.keep_splays.configure(state='disabled')
        self.success_run = ctk.CTkLabel(self.export_frm, text='', height=25, width=200, fg_color='white', corner_radius=5)
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
        self.cave_name_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["cave_name_lbl"][self.lc]}: ', font=("Roboto", 14), 
                                          fg_color='darkgray', corner_radius=5)
        self.cave_name_lbl.grid(row=0, column=0, padx=5, pady=5, ipadx=35, sticky='e')
        self.cave_name_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.cave_name_fld.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        # X
        self.X_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["X_lbl"][self.lc]}: ')
        self.X_lbl.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.X = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.X.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        # Y
        self.Y_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["Y_lbl"][self.lc]}: ')
        self.Y_lbl.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.Y = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.Y.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        # Z
        self.Z_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["Z_lbl"][self.lc]}: ')
        self.Z_lbl.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.Z = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.Z.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        # File Name
        self.file_name_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["file_name_lbl"][self.lc]}: ')
        self.file_name_lbl.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.file_name_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width+30, height=25)
        self.file_name_fld.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        # Fixed point
        self.fixed_station_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["fixed_station_lbl"][self.lc]}: ')
        self.fixed_station_lbl.grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.fixed_station_fld = ctk.CTkEntry(self.cave_data_frame, width=mtf_entry_width, height=25, fg_color='white', corner_radius=5)
        self.fixed_station_fld.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        # Poly Length
        self.poly_length_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["poly_length_lbl"][self.lc]}: ')
        self.poly_length_lbl.grid(row=7, column=0, padx=5, pady=5, sticky='e')
        self.poly_length_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.poly_length_fld.grid(row=7, column=1, padx=5, pady=5, sticky='w')
        # Horizontal Length
        self.hor_length_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["hor_length_lbl"][self.lc]}: ')
        self.hor_length_lbl.grid(row=8, column=0, padx=5, pady=5, sticky='e')
        self.hor_length_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.hor_length_fld.grid(row=8, column=1, padx=5, pady=5, sticky='w')
        # Elevation
        self.elevation_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["elevation_lbl"][self.lc]}: ')
        self.elevation_lbl.grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.elevation_fld = ctk.CTkLabel(self.cave_data_frame, width=50, height=25, text='')
        self.elevation_fld.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        # Depth
        self.depth_lbl = ctk.CTkLabel(self.cave_data_frame, text=f'{lcat["depth_lbl"][self.lc]}: ')
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
                                        command=lambda: self.get_location(self.location_input.get()),
                                        compound='left', image=self.images['coordinates'])
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

        self.calc_md_btn = ctk.CTkButton(self.decl_frame, width=125, text=f'{lcat["calc_md_btn"][self.lc]}',
                                        command=lambda: self.get_md(self.model.get(),self.year_combo.get(),self.month_combo.get(),self.day_combo.get()),
                                        compound='left', image=self.images['compass'])
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
        self.readme_text = ctk.CTkTextbox(self.help_tab_frame, height=425, wrap='word')
        self.readme_text.pack(padx=5, pady=5, expand=True, fill="both")
        try:
            with open(readme_file_path,'r', encoding='utf-8') as readme_file:
                self.readme_text.insert('0.0', readme_file.read())
        except IOError as error:
            self.readme_text.insert('0.0',f'{lcat["readme_text"][self.lc]}\n{error}')
        self.readme_text.configure(state='disabled')

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
            self.speleoliti_app = _SpeleolitiOnline(headless=False, survey_path=self.survey_data_file_path)
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
        # Update self.lc based on language
        if language == 'HR': 
            self.lc = 0
        elif language == 'EN':
            self.lc = 1
        
        # Update all GUI text elements
        self.update_gui_language()
        
        # Store language setting to a language catalog file
        _config_store.write_config(lcat)
    
    def update_gui_language(self):
        """Update all GUI text elements when language changes"""
        # Main tab elements
        self.import_frm_lbl.configure(text=f'{lcat["import_frm_lbl"][self.lc]}')
        self.open_file.configure(text=f'{lcat["open_file"][self.lc]}')
        self.survey_sign_lbl.configure(text=f'{lcat["survey_sign_lbl"][self.lc]}')
        self.show_md_value_lbl.configure(text=f'{lcat["show_md_value_lbl"][self.lc]}:')
        self.apply_fix_md_btn.configure(text=f'{lcat["apply_fix_md_btn"][self.lc]}')
        self.export_frm_lbl.configure(text=f'{lcat["export_frm_lbl"][self.lc]}:')
        self.save_csv_file.configure(text=f'{lcat["save_csv_file"][self.lc]}')
        self.export_original_angle.configure(text=f'{lcat["export_original_angle"][self.lc]}')
        self.keep_splays.configure(text=f'{lcat["keep_splays"][self.lc]}')
        
        # Cave data frame
        self.cave_name_lbl.configure(text=f'{lcat["cave_name_lbl"][self.lc]}: ')
        self.X_lbl.configure(text=f'{lcat["X_lbl"][self.lc]}: ')
        self.Y_lbl.configure(text=f'{lcat["Y_lbl"][self.lc]}: ')
        self.Z_lbl.configure(text=f'{lcat["Z_lbl"][self.lc]}: ')
        self.file_name_lbl.configure(text=f'{lcat["file_name_lbl"][self.lc]}: ')
        self.fixed_station_lbl.configure(text=f'{lcat["fixed_station_lbl"][self.lc]}: ')
        self.poly_length_lbl.configure(text=f'{lcat["poly_length_lbl"][self.lc]}: ')
        self.hor_length_lbl.configure(text=f'{lcat["hor_length_lbl"][self.lc]}: ')
        self.elevation_lbl.configure(text=f'{lcat["elevation_lbl"][self.lc]}: ')
        self.depth_lbl.configure(text=f'{lcat["depth_lbl"][self.lc]}: ')
        
        # MagDec tab elements
        self.location_frm_label.configure(text=f'{lcat["location_frm_label"][self.lc]}:')
        self.location_label.configure(text=f'{lcat["location_label"][self.lc]}: ')
        self.get_coord_btn.configure(text=f'{lcat["get_coord_btn_label"][self.lc]}')
        self.lat_label.configure(text=f'{lcat["lat_label"][self.lc]}: ')
        self.lon_label.configure(text=f'{lcat["lon_label"][self.lc]}: ')
        self.date_label.configure(text=f'{lcat["date_label"][self.lc]}: ')
        self.date_day.configure(text=f'{lcat["date_day"][self.lc]}:')
        self.date_month.configure(text=f'{lcat["date_month"][self.lc]}:')
        self.date_year.configure(text=f'{lcat["date_year"][self.lc]}:')
        self.calc_md_btn.configure(text=f'{lcat["calc_md_btn"][self.lc]}')
        self.md_value_lbl.configure(text=f'{lcat["md_value_lbl"][self.lc]}:')
        
        # Help tab - update README content
        readme_file_path = os.path.join(application_path, f'{lcat["readme_file_path"][self.lc]}')
        self.readme_text.configure(state='normal')
        self.readme_text.delete('0.0', 'end')
        try:
            with open(readme_file_path,'r', encoding='utf-8') as readme_file:
                self.readme_text.insert('0.0', readme_file.read())
        except IOError as error:
            self.readme_text.insert('0.0',f'{lcat["readme_text"][self.lc]}\n{error}')
        self.readme_text.configure(state='disabled')

    #   CAVE SURVEY FILE IMPORT
    def open_file_event(self):
        """Open raw cave survey data file csv or txt, create json and execute parsing"""

        # Suggest the recent software to open file from
        filetypes = (("CSV file","*.csv"), ("Text file","*.txt*"), ("Walls file","*.srv*"), ("All files","*"))
        software_to_file = {
            "None":"All files",
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
            self.file_path = None
        # Continue with reading and processing the file
        if self.file_path:
            # Set the last used software and store to config file
            lcat['last_used_software'] = self.software
            _config_store.write_config(lcat)
            # Make changes if the file opens correctly
            file_base_name = os.path.basename(self.file_path)
            self.suggested_name_for_file = os.path.splitext(file_base_name)[0] + f'{lcat["sufix"][self.lc]}'
            self.cave_survey_json_data = {"fix": "","x": "","y": "","z": "","dcl": "","name": "","descr": "","viz": ["null"]}
            # Clear cached attributes from previous file
            if hasattr(self, 'original_shots'):
                delattr(self, 'original_shots')
            if hasattr(self, 'original_fixed_station_name'):
                delattr(self, 'original_fixed_station_name')
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
                # Enable keep_splays only for TopoDroid
                if self.software == 'TopoDroid':
                    self.keep_splays.configure(state='normal')
                else:
                    self.keep_splays.configure(state='disabled')
                self.gui.update()
            # Generic error is no longer shown here - specific errors shown in parse functions
    
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
            # Handle asterisk prefix for splays - keep it at the beginning
            if original_shot['t2'].startswith('*'):
                # Move asterisk to the beginning: "*az_1" instead of "az_*1"
                shot['t2'] = f"*{new_shot_prefix}{original_shot['t2'][1:]}"
            else:
                shot['t2'] = f"{new_shot_prefix}{original_shot['t2']}"
            shot['a'] = round((float(original_shot['a']) + self.md_val) % 360,2)
            shot['l'] = round(float(shot['l']),3)
            shot['f'] = round(float(shot['f']),2)
        # save to json
        _exporter.write_survey_json(self.cave_survey_json_data, write_json_file_path)
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
        write_json_file_path = _sp_paths.SURVEY_DATA_PATH
        _exporter.write_survey_json(self.cave_survey_json_data, write_json_file_path)

    def store_to_csv(self):
        """Pick a destination and delegate the write to the exporter service."""

        shot_prefix = self.cave_survey_json_data['descr']
        if hasattr(self, 'file_name_fld'):
            self.suggested_name_for_file = self.file_name_fld.get()
        if shot_prefix == '' and self.software == 'PocketTopo':
            messagebox.showwarning('Warning', f'{lcat["sign_warning"][self.lc]}')
        write_csv_file_path = ctk.filedialog.asksaveasfilename(
            initialdir='SurveyScraper',
            title=f'{lcat["write_csv_file_path"][self.lc]}',
            defaultextension=".csv",
            initialfile=f'{self.suggested_name_for_file}',
        )
        if not write_csv_file_path:
            return

        dimensions = None
        if not self.offline:
            dimensions = (self.poly_length, self.hor_length, self.elevation, self.depth)

        try:
            _exporter.export_to_csv(
                survey=self.cave_survey_json_data,
                path=write_csv_file_path,
                software=self.software,
                keep_splays=(self.keep_splays_var.get() == 'on'),
                include_original_angles=(self.export_original_angle_var.get() == 'on'),
                original_shots=getattr(self, 'original_shots', None),
                dimensions=dimensions,
            )
        except IOError:
            messagebox.showerror('Error', f'{lcat["IOError"][self.lc]}')
            return
        self.success_run.configure(text='CSV pohranjen!')
        winsound.MessageBeep()
        
    # SPELEOLITI CALCULATION FUNCTION
    def run_speleoliti_calculation(self):
        self.speleoliti_app_headless = _SpeleolitiOnline(headless=True, survey_path=self.survey_data_file_path)
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
            self.cave_survey_json_data['fix'] = self.fixed_station # set fixed station by default
            self.cave_survey_json_data['name'] = self.cave_name
        else:
            self.offline = True
            messagebox.showwarning('Warning','Preskačem obradu u Speleoliti Online jer nema internet veze!')

    # CAVE SURVEY FILE PARSE FUNCTIONS
    def parse_event(self, software):
        """Parse the survey file, persist for Speleoliti, and run dimension calc."""
        global parsed
        parsed = False
        # load processing window in GUI and begin process
        self.loading_window = ctk.CTkToplevel(self.gui)
        self.loading_window.title('SurveyScraper')
        self.loading_window.attributes('-topmost', True)
        self.gui.eval(f'tk::PlaceWindow {str(self.loading_window)} center')
        loading_label = ctk.CTkLabel(self.loading_window, text="Obrađujem, molim pričekaj...")
        loading_label.pack(padx=50, pady=(25,25), expand=True, fill="x")
        self.gui.update()

        # Parse via the package parser registry. Failures raise; nothing is
        # written to disk before we know the parse succeeded.
        try:
            result = _parsers.parse_file(software, self.file_path)
        except _ParseError as e:
            _log.exception("Parse failed for %s file %s", software, self.file_path)
            messagebox.showerror(f'{software} Parsing Error', f'Error details:\n\n{e}')
            self.loading_window.destroy()
            return

        # Adopt parser output into the GUI's working state
        self.cave_survey_json_data = result.survey
        if result.cave_name is not None:
            self.cave_name = result.cave_name
        if result.survey_date is not None:
            self.survey_date = result.survey_date

        # Persist the Speleoliti-friendly view (splays filtered out for TopoDroid).
        # Speleoliti Online cannot render splay shots, so the upload-to-web
        # version drops them; the GUI keeps the full version in memory for CSV export.
        speleoliti_view = result.survey_for_speleoliti()
        _exporter.write_survey_json(speleoliti_view, write_json_file_path)

        parsed = True

        # Speleoliti calculation. Note: the legacy code wrapped this in a
        # threading.Thread but called the method synchronously by mistake
        # (`target=self.run_speleoliti_calculation()`), so the Thread was a
        # no-op. The downstream GUI in open_file_event reads attributes set
        # inside run_speleoliti_calculation, so it relies on synchronous
        # execution. Keeping it synchronous here; truly async execution is
        # a Phase 5 (UI rewrite) concern.
        try:
            self.run_speleoliti_calculation()
            winsound.MessageBeep()
            self.success_run.configure(text='Uspješan uvoz i obrada!')
        except Exception:
            _log.exception("Speleoliti calculation failed")
            parsed = False
            self.success_run.configure(text='Neuspješan uvoz i obrada!')
        self.loading_window.destroy()
        self.gui.update()


    #   MAGNETIC DECLINATION FUNCTIONS
    def get_location(self, location):
        if not location:
            messagebox.showerror('Error', f'{lcat["location_error"][self.lc]}')
            return
        try:
            latitude, longitude = _magdec.geocode(location)
        except _NetworkError:
            messagebox.showerror('Error', 'Nije moguće dohvatiti koordinate! Provjeri internet vezu!')
            return
        self.lat_input.delete(0, ctk.END)
        self.lon_input.delete(0, ctk.END)
        self.lat_input.insert(0, f'{latitude:.4f}')
        self.lon_input.insert(0, f'{longitude:.4f}')
        # Delete previous marker if it exists
        if hasattr(self, 'location_marker') and self.location_marker:
            self.location_marker.delete()
        self.map.set_position(latitude, longitude)
        self.location_marker = self.map.set_marker(latitude, longitude, text=location)
        self.map.set_zoom(13)

    def get_md(self, model, year, month, day):
        try:
            datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            messagebox.showerror('Error', f'{lcat["datetime.ValueError"][self.lc]}')
            return
        if self.lat_input.get() == '' or self.lon_input.get() == '':
            messagebox.showerror('Error', f'{lcat["lat_lon_input_error"][self.lc]}')
            return
        try:
            decl = _magdec.magnetic_declination(
                float(self.lat_input.get()), float(self.lon_input.get()),
                model, year, month, day,
            )
        except _NetworkError:
            messagebox.showerror('Error', 'Nije moguće izračunati magnetsku deklinaciju! Provjeri internet vezu!')
            return

        self.md_val = float(f'{decl:.3f}')
        self.md_value.configure(state='normal')
        if self.md_value.get():
            self.md_value.delete(0, 'end')
        self.md_value.insert(0, f'{self.md_val}°')
        self.md_value.configure(state='disabled')
        if self.show_md_value.get():
            self.show_md_value.delete(0, 'end')
        self.show_md_value.insert(0, f'{self.md_val}°')

if __name__ == '__main__':
    lang, last_used = config() # Run config right at the start
    SurveyScraper(lang, last_used)