import re
import os
import sys
import json
import tkintermapview
import datetime
import winsound
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from idlelib.tooltip import Hovertip
from mag_decl_webscrape import Retrieve_lat_lon, Retrieve_magn_decl

ctk.set_appearance_mode('light')
ctk.set_default_color_theme('green')

def config():
    """Read configuration settings"""
    global application_path
    """Set the directory of the original file for a path to any other file"""
    if getattr(sys,'frozen',False): #check if the app runs as a script or as a frozen exe file
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    """Read language catalog"""
    global lcat
    file_path = os.path.join(application_path, 'config_settings.json')
    try:
        with open(file_path,'r', encoding='utf-8') as file:
            lcat = json.load(file)
            return lcat['language_setting']
    except Exception as ex:
        messagebox.showerror('Error',f'There was an error while reading the file: {ex}')

class SurveyScraper():
    def __init__(self, lc):
        self.gui = ctk.CTk()
        self.gui.title('SurveyScraper')
        self.gui.geometry("250x360")
        self.gui.columnconfigure(0, weight=6)
        self.gui.columnconfigure(1, weight=1)
        self.md_val = 0
        if lc == 'HR':
            self.lc = 0
        elif lc == 'EN':
            self.lc = 1

        def resource_path(relative_path):
            """ Get absolute path to resource, works for dev and for PyInstaller """
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                #base_path = os.path.abspath(".")
                base_path = os.path.dirname(__file__)
            return os.path.join(base_path, relative_path)
        
        #       MAIN FRAME
        self.lang_var = ctk.StringVar(self.gui)
        self.lang_var.set(lc)
        self.gui_title = ctk.CTkLabel(self.gui, text='SurveyScraper', font=('Roboto', 18))
        self.gui_title.grid(row=0, column=0, rowspan=2, padx=0, pady=5, sticky='ew')
        language_choice = ctk.CTkOptionMenu(self.gui, values=['HR','EN'], variable=self.lang_var, anchor='center', font=('Roboto', 12), width=20,
                                            command=self.set_language)
        language_choice.grid(row=0, column=1, padx=0, pady=5, sticky='w')
        self.readme = ctk.CTkButton(self.gui, text='?', width=20, font=('Roboto', 12), command=self.open_readme)
        self.readme.grid(row=0, column=2, padx=5, pady=5, sticky='e')

        #       SOFTWARE FRAME
        self.software_frm = ctk.CTkFrame(self.gui)
        self.software_frm.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')
        self.software_lbl = ctk.CTkLabel(self.software_frm, text=f'{lcat["software_lbl"][self.lc]}', font=('Roboto', 14))
        self.software_lbl.pack(padx=5, pady=5)
        self.software = ctk.StringVar(self.software_frm)
        self.software.set(lcat['last_used_software'])
        software_choice = ctk.CTkOptionMenu(self.software_frm, values=['TopoDroid','PocketTopo'], variable=self.software, anchor='center')
        software_choice.pack(padx=5, pady=5)

        #   OPEN FILE-DECLINATION FRAME
        self.content = ctk.CTkFrame(self.gui)
        self.content.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.open_file_img = ctk.CTkImage(Image.open(resource_path('img/open_file.png')), size=(15,15))
        self.open_file = ctk.CTkButton(self.content, width=180, text=f'{lcat["open_file"][self.lc]}', 
                                    command=lambda: self.open_file_event(self.software.get()), 
                                    compound='left', image=self.open_file_img)
        self.open_file.grid(row=0, column=0, padx=5, pady=10, columnspan=2)
        self.opened_file = ctk.CTkLabel(self.content, text='', width=200, height=25, 
                                        fg_color='white', corner_radius=5)
        self.opened_file.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        self.opened_file.configure(state='disabled')
        self.opened_file.grid_remove()
        self.survey_sign_lbl = ctk.CTkLabel(self.content, text=f'{lcat["survey_sign_lbl"][self.lc]}')
        self.survey_sign_lbl.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.survey_sign = ctk.CTkEntry(self.content, width=50, height=25)
        self.survey_sign.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.calc_md_img = ctk.CTkImage(Image.open(resource_path('img/compass.png')), size=(15,15))
        self.calc_magn_decl_btn = ctk.CTkButton(self.content, width=200, text=f'{lcat["calc_magn_decl_btn"][self.lc]}', 
                                        command=self.calc_magn_decl, compound='left', image=self.calc_md_img)
        self.calc_magn_decl_btn.grid(row=3, column=0, padx=5, pady=10, columnspan=2)

        #   GENERATE FRAME
        self.content2 = ctk.CTkFrame(self.gui)
        self.content2.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.parse_img = ctk.CTkImage(Image.open(resource_path('img/generate.png')), size=(15,15))
        self.parse_file = ctk.CTkButton(self.content2, text=f'{lcat["parse_file"][self.lc]}', 
                                        command=lambda: self.parse_event(self.software.get()),
                                        compound='left', image=self.parse_img)
        self.parse_file.pack(padx=5, pady=5)
        self.parse_file.configure(state='disabled')
        self.success_run = ctk.CTkLabel(self.content2, text='', width=180, height=25, 
                                        fg_color='white', corner_radius=5)
        self.success_run.pack(padx=5, pady=10)
        self.success_run.configure(state='disabled')
        self.success_run.pack_forget()
        self.open_gen_file = ctk.CTkButton(self.content2, text=f'{lcat["open_gen_file"][self.lc]}', 
                                        command=lambda: os.system('"%s"' % write_file_path),
                                        compound='left', image=self.open_file_img)
        self.open_gen_file.pack(padx=5, pady=5)
        self.open_gen_file.pack_forget()

        #   RUN
        self.gui.mainloop()
    
    def open_readme(self):
        # find the readme file against dynamic app location
        file_path = os.path.join(application_path, f'{lcat["readme_file_path"][self.lc]}') 
        
        readme = ctk.CTkToplevel()
        readme.title('Readme')
        readme.grab_set()
        readme_text = ctk.CTkTextbox(readme, width=750, height=500)
        readme_text.pack()
        try:
            with open(file_path,'r', encoding='utf-8') as readme_file:
                text = readme_file.read()
            readme_text.insert('0.0',text)
        except IOError as error:
            readme_text.insert('0.0',f'{lcat["readme_text"][self.lc]}\n{error}')
        readme_text.configure(state='disabled')
    
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

    def open_file_event(self, software):
        global file_path, name_for_file
        pt_filetype = (("Text file","*.txt*"), ("All files","*"))
        td_filetype = (("CSV file","*.csv"), ("All files","*"))
        if software == 'TopoDroid' or software == 'topodroidx':
            file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', 
                                                    title=f'{lcat["file_path_csv"][self.lc]}', filetypes = td_filetype)
        elif software == 'PocketTopo':
            file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', 
                                                    title=f'{lcat["file_path_txt"][self.lc]}', filetypes = pt_filetype)
        
        if (not file_path.endswith('.csv') and (software == 'TopoDroid' or software == 'topodroidx')) or (not file_path.endswith('.txt') and software == 'PocketTopo'):
            if not file_path == '':
                messagebox.showerror('Error',f'{lcat["file_path_error"][self.lc]}')
            file_path = None
        if file_path:
            file_base_name = os.path.basename(file_path)
            name_for_file = os.path.splitext(file_base_name)[0]
            self.opened_file.grid()
            self.opened_file.configure(text=file_base_name)
            self.gui.update()
            self.parse_file.configure(state='normal')
            self.calc_magn_decl_btn.configure(state='normal')

    def calc_magn_decl(self):
        MagneticDeclination_window(self)

    def parse_event(self, software):
        global success 
        success = False
        if self.create_write_file():
            if software == 'PocketTopo':
                success = self.parse_pockettopo()
            elif software == 'TopoDroid':
                success = self.parse_topodroid()
            self.success_run.pack() 
            if success:
                winsound.MessageBeep()
                self.success_run.configure(text=f'{lcat["success_run_true"][self.lc]}')
                self.open_gen_file.pack(padx=5, pady=5)
            else:
                self.success_run.configure(text=f'{lcat["success_run_false"][self.lc]}')
            self.gui.update()
            self.gui.geometry("250x425")
        
        # Save last used software
        lcat['last_used_software'] = software
        file_path = os.path.join(application_path, 'config_settings.json')
        with open(file_path, 'w') as fileWriter:
            json.dump(lcat, fileWriter, indent=4)
        
    def create_write_file(self):
        global write_file_path
        self.sign = self.survey_sign.get()
        if self.sign == '':
            messagebox.showwarning('Warning',f'{lcat["sign_warning"][self.lc]}')
        write_file_path = ctk.filedialog.asksaveasfilename(initialdir='SurveyScraper', title=f'{lcat["write_file_path"][self.lc]}', 
                                                        defaultextension=".csv", initialfile=f'{name_for_file}{lcat["sufix"][self.lc]}')
        if write_file_path == '':
            return False
        try:
            with open(write_file_path, 'w') as file:
                file.write(f'{lcat["file.write"][self.lc]}\n')
                return True
        except IOError:
            messagebox.showerror('Error',f'{lcat["IOError"][self.lc]}')
            return False
    
    def parse_pockettopo(self):
        with open(file_path,'r') as file:
            for _ in range(6):
                next(file)   
            shots = [] #a temporary shot list
            for row in file:
                row_data = re.sub(r'\[.\]','',row)
                row_data = re.sub(r'<','',row_data)
                shot = row_data.split() #a list of shot data
                if len(shot) == 5: #filter for main shots
                    shots.append(shot)
                    if len(shots) == 2:
                        if shots[1][0] != shots[0][0] and shots[1][1] != shots[0][1]: #if the new shot name is different than the previous shot, save, else add to the list
                            if self.sign == '':
                                main_shot = f'{shots[0][0]},{shots[0][1]},{float(shots[0][2]):.3f},{float(shots[0][3]):.2f},{float(shots[0][4]):.2f}\n'
                            else:
                                main_shot = f'{self.sign}-{shots[0][0]},{self.sign}-{shots[0][1]},{float(shots[0][2]):.3f},{float(shots[0][3]):.2f},{float(shots[0][4]):.2f}\n'
                            with open(write_file_path, 'a') as file:
                                file.write(main_shot)
                            shots.pop(0)
                    if len(shots) == 3:
                            mean_len = (float(shots[0][2])+float(shots[1][2])+float(shots[2][2]))/3
                            mean_dir = (float(shots[0][3])+float(shots[1][3])+float(shots[2][3]))/3 + self.md_val
                            mean_inc = (float(shots[0][4])+float(shots[1][4])+float(shots[2][4]))/3
                            if self.sign == '':
                                main_shot = f'{shots[0][0]},{shots[0][1]},{mean_len:.3f},{mean_dir:.2f},{mean_inc:.2f}\n'
                            else:
                                main_shot = f'{self.sign}-{shots[0][0]},{self.sign}-{shots[0][1]},{mean_len:.3f},{mean_dir:.2f},{mean_inc:.2f}\n'
                            with open(write_file_path, 'a') as file:
                                file.write(main_shot)
                            shots.clear()
        success = True
        return success

    def parse_topodroid(self):
        with open(file_path,'r') as file:
            for _ in range(4):
                next(file)   
            for row in file:
                shot = row.split(',')         
                if shot[1] != '-': #filter for main shots
                    shot_from = shot[0][0:shot[0].find('@')]
                    shot_to = shot[1][0:shot[1].find('@')]
                    if self.sign == '':
                        main_shot = f'{shot_from},{shot_to},{shot[2]},{float(shot[3])+self.md_val},{shot[4]}\n'
                    else:
                        main_shot = f'{self.sign}-{shot_from},{self.sign}-{shot_to},{shot[2]},{float(shot[3])+self.md_val},{shot[4]}\n'
                    with open(write_file_path, 'a') as file:
                        file.write(main_shot)
        success = True
        return success

class MagneticDeclination_window():
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.gui_md = ctk.CTkToplevel()
        self.gui_md.title(f'{lcat["gui_md.title"][self.main_gui.lc]}')
        self.gui_md.grab_set()
        self.gui_md.resizable(False,False)
        self.md_val = 0

        def get_location(location):
            global latitude, longitude
            if location != '':
                self.get_coord_btn.configure(text=f'{lcat["get_coord_btn"][self.main_gui.lc]}')
                self.lat_input.delete(0,ctk.END)
                self.lon_input.delete(0,ctk.END)
                lat_lon_app = Retrieve_lat_lon(location)
                latitude, longitude = lat_lon_app.retrieve_lat_lon()
                self.lat_input.insert(0,f'{latitude:.4f}')
                self.lon_input.insert(0,f'{longitude:.4f}')
                self.map.set_address(location, marker=True)
                self.map.set_zoom(13)
            else:
                messagebox.showerror('Error',f'{lcat["location_error"][self.main_gui.lc]}')
            self.get_coord_btn.configure(text=f'{lcat["get_coord_btn_default"][self.main_gui.lc]}')

        # LOCATION FRAME
        self.location_frame = ctk.CTkFrame(self.gui_md)
        self.location_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=5)
        self.location_frm_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["location_frm_label"][self.main_gui.lc]}:', font=('Roboto', 14))
        self.location_frm_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.location_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["location_label"][self.main_gui.lc]}: ', font=('Roboto', 12))
        self.location_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.location_input = ctk.CTkEntry(self.location_frame, width=120, height=20, font=('Roboto', 12))
        self.location_input.grid(row=1, column=1, padx=10, pady=5)
        self.get_coord_btn = ctk.CTkButton(self.location_frame, width=150, text=f'{lcat["get_coord_btn_label"][self.main_gui.lc]}',
                                        command=lambda: get_location(self.location_input.get()))
        self.get_coord_btn.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        Hovertip(self.location_input,f'{lcat["hovertip"][self.main_gui.lc]}', hover_delay=500)
        self.lat_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["lat_label"][self.main_gui.lc]}: ', font=('Roboto', 12))
        self.lat_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.lat_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lat_input.grid(row=3, column=1,  pady=5)
        self.lat_N = ctk.CTkLabel(self.location_frame, text="N", font=('Roboto', 12))
        self.lat_N.grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.lon_label = ctk.CTkLabel(self.location_frame, text=f'{lcat["lon_label"][self.main_gui.lc]}: ', font=('Roboto', 12))
        self.lon_label.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.lon_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lon_input.grid(row=4, column=1,  pady=5)
        self.lon_E = ctk.CTkLabel(self.location_frame, text="E", font=('Roboto', 12))
        self.lon_E.grid(row=4, column=2, padx=5, pady=5, sticky='w')
        self.map = tkintermapview.TkinterMapView(self.location_frame, width=100, height=300, corner_radius=15)
        self.map.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.map.set_position(float(lcat["map.set_position_x"][self.main_gui.lc]),float(lcat["map.set_position_y"][self.main_gui.lc]))
        self.map.set_zoom(float(lcat["map.set_zoom"][self.main_gui.lc]))

        # MODEL FRAME
        self.model_frame = ctk.CTkFrame(self.gui_md)
        self.model_frame.grid(row=0, column=1, padx=10, pady=5, sticky='news')
        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:", font=('Roboto', 14))
        self.model_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
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
        self.model_wmm.grid(row=1, column=1, padx=60, pady=5, sticky='w')
        self.model_wmm.select()
        self.model_igrf = ctk.CTkRadioButton(self.model_frame, text='IGRF (1590-2024)', value='IGRF', variable=self.model, command=refresh_year)
        self.model_igrf.grid(row=2, column=1, padx=60, pady=5, sticky='w')

        # DATE FRAME
        self.date_frame = ctk.CTkFrame(self.gui_md)
        self.date_frame.grid(row=1, column=1, padx=10, pady=5, sticky='news')
        self.date_frame.columnconfigure((0,1), weight=1)
        self.date_label = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_label"][self.main_gui.lc]}: ', font=('Roboto', 14))
        self.date_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
        self.date_day = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_day"][self.main_gui.lc]}:')
        self.date_day.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        selected_day = ctk.StringVar(value=current_day)
        self.day_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,32)], variable=selected_day)
        self.day_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.date_month = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_month"][self.main_gui.lc]}:')
        self.date_month.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        selected_month = ctk.StringVar(value=current_month)
        self.month_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,13)], variable=selected_month)
        self.month_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.date_year = ctk.CTkLabel(self.date_frame, text=f'{lcat["date_year"][self.main_gui.lc]}:')
        self.date_year.grid(row=3, column=0, padx=10, pady=5, sticky='e')
        selected_year = ctk.StringVar(value=current_year)
        year_range = [str(y) for y in range(2019,int(current_year)+2)]
        self.year_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=sorted(year_range, reverse=True), variable=selected_year)
        self.year_combo.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        def get_md(model, year, month, day):
            try:
                datetime.datetime(int(year),int(month),int(day))
            except ValueError:
                messagebox.showerror('Error',f'{lcat["datetime.ValueError"][self.main_gui.lc]}')
            if self.lat_input.get() == '' or self.lon_input.get() == '':
                messagebox.showerror('Error',f'{lcat["lat_lon_input_error"][self.main_gui.lc]}')
            else:
                magn_decl_app = Retrieve_magn_decl(float(self.lat_input.get()), float(self.lon_input.get()), model, year, month, day)
                md_val = float(f'{magn_decl_app.retrieve_magn_decl():.3f}')
                self.md_value.configure(text=md_val)
                self.main_gui.md_val = md_val   #the characteristic of the main gui window (default value of 0) is now changed
                self.include_md_btn.configure(state='normal')
        
        def apply_md():
             self.gui_md.destroy()

        # CALCULATION FRAME
        self.decl_frame = ctk.CTkFrame(self.gui_md)
        self.decl_frame.grid(row=2, column=1, padx=10, pady=5, sticky='news')
        self.decl_frame.columnconfigure(0, weight=1)
        self.calc_md_btn = ctk.CTkButton(self.decl_frame, width=100, text=f'{lcat["calc_md_btn"][self.main_gui.lc]}',
                                        command=lambda: get_md(self.model.get(),self.year_combo.get(),self.month_combo.get(),self.day_combo.get()))
        self.calc_md_btn.grid(row=0, column=0, columnspan=3, padx=5, pady=10)
        self.md_value_lbl = ctk.CTkLabel(self.decl_frame, text=f'{lcat["md_value_lbl"][self.main_gui.lc]}:')
        self.md_value_lbl.grid(row=1, column=0, padx=5, pady=5)
        self.md_value = ctk.CTkLabel(self.decl_frame, text='', width=80, height=25, fg_color='white', corner_radius=5)
        self.md_value.grid(row=1, column=1, padx=5, pady=5)
        self.md_value.configure(state='disabled')
        self.md_value_deg = ctk.CTkLabel(self.decl_frame, text='°')
        self.md_value_deg.grid(row=1, column=2, padx=5, pady=5)

        # EXECUTE BUTTON
        self.include_md_btn = ctk.CTkButton(self.gui_md, width=150, text=f'{lcat["include_md_btn"][self.main_gui.lc]}', command=apply_md)
        self.include_md_btn.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.include_md_btn.configure(state='disabled')

if __name__ == '__main__':
    # Run config right at the start
    lang = config()
    SurveyScraper(lang)