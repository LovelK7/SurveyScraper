import re
import os
import sys
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

class SurveyScraper():
    def __init__(self):
        self.gui = ctk.CTk()
        self.gui.title('SurveyScraper')
        self.gui.columnconfigure(0, weight=6)
        self.gui.columnconfigure(1, weight=1)
        self.md_val = 0

        def resource_path(relative_path):
            """ Get absolute path to resource, works for dev and for PyInstaller """
            try:
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_path = sys._MEIPASS
            except Exception:
                #base_path = os.path.abspath(".")
                base_path = os.path.dirname(__file__)
            return os.path.join(base_path, relative_path)

        def open_readme():
            if getattr(sys,'frozen',False): #check if the app runs as a script or as a frozen exe file
                application_path = os.path.dirname(sys.executable)
            elif __file__:
                application_path = os.path.dirname(__file__)
            file_path = os.path.join(application_path, 'surveyscraper_README.txt') #to find the readme file against dynamic app location

            readme = ctk.CTkToplevel()
            readme.title('Readme')
            readme.grab_set()
            readme_text = ctk.CTkTextbox(readme, width=700, height=500)
            readme_text.pack()
            try:
                with open(file_path,'r', encoding='utf-8') as readme_file:
                    text = readme_file.read()
                readme_text.insert('0.0',text)
            except IOError as error:
                readme_text.insert('0.0',f'Pogreška prilikom učitanja readme datoteke!\n{error}')
            readme_text.configure(state='disabled')

        self.gui_title = ctk.CTkLabel(self.gui, text='SurveyScraper', font=('Roboto', 20))
        self.gui_title.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.readme = ctk.CTkButton(self.gui, text='?', width=20, font=('Roboto', 12), command=open_readme)
        self.readme.grid(row=0, column=1, padx=10, pady=10)

        self.software_frm = ctk.CTkFrame(self.gui)
        self.software_frm.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.software_lbl = ctk.CTkLabel(self.software_frm, text='Odaberi program: ', font=('Roboto', 14))
        self.software_lbl.pack(padx=5, pady=5)
        software = ctk.StringVar(self.software_frm)
        td_radiobtn = ctk.CTkRadioButton(self.software_frm, variable=software, text='TopoDroid', value='topodroid')
        td_radiobtn.pack(padx=5, pady=5)
        td_radiobtn.select()
        pt_radiobtn = ctk.CTkRadioButton(self.software_frm, variable=software, text='PocketTopo', value='pockettopo')
        pt_radiobtn.pack(padx=5, pady=5)

        self.content = ctk.CTkFrame(self.gui)
        self.content.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        def open_file_event(software):
            global file_path, name_for_file
            pt_filetype = (("Text file","*.txt*"), ("All files","*"))
            td_filetype = (("CSV file","*.csv"), ("All files","*"))
            if software == 'topodroid' or software == 'topodroidx':
                file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', 
                                                           title='Otvori csv datoteku', filetypes = td_filetype)
            elif software == 'pockettopo':
                file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', 
                                                           title='Otvori txt datoteku', filetypes = pt_filetype)
            
            if (not file_path.endswith('.csv') and (software == 'topodroid' or software == 'topodroidx')) or (not file_path.endswith('.txt') and software == 'pockettopo'):
                if not file_path == '':
                    messagebox.showerror('Pogreška','Nije otvorena pravilna datoteka!')
                file_path = None
            if file_path:
                file_base_name = os.path.basename(file_path)
                name_for_file = os.path.splitext(file_base_name)[0]
                self.opened_file.grid()
                self.opened_file.configure(text=file_base_name)
                self.gui.update()
                self.parse_file.configure(state='normal')
                self.calc_magn_decl_btn.configure(state='normal')
        
        self.open_file_img = ctk.CTkImage(Image.open(resource_path('img/open_file.png')), size=(15,15))
        self.open_file = ctk.CTkButton(self.content, width=180, text='Otvori datoteku s vlakovima', 
                                       command=lambda: open_file_event(software.get()), 
                                       compound='left', image=self.open_file_img)
        self.open_file.grid(row=0, column=0, padx=5, pady=10, columnspan=2)

        self.opened_file = ctk.CTkLabel(self.content, text='', width=200, height=25, 
                                        fg_color='white', corner_radius=5)
        self.opened_file.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        self.opened_file.configure(state='disabled')
        self.opened_file.grid_remove()
        
        self.survey_sign_lbl = ctk.CTkLabel(self.content, text='Predznak točaka: ')
        self.survey_sign_lbl.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.survey_sign = ctk.CTkEntry(self.content, width=50, height=25)
        self.survey_sign.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        def calc_magn_decl():
            MagneticDeclination_window(self)

        self.calc_md_img = ctk.CTkImage(Image.open(resource_path('img/compass.png')), size=(15,15))
        self.calc_magn_decl_btn = ctk.CTkButton(self.content, width=150, text='Uračunaj magnetsku deklinaciju', 
                                        command=calc_magn_decl, compound='left', image=self.calc_md_img)
        self.calc_magn_decl_btn.grid(row=3, column=0, padx=5, pady=10, columnspan=2)

        self.content2 = ctk.CTkFrame(self.gui)
        self.content2.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
        
        self.parse_file = ctk.CTkButton(self.content2, text='Generiraj CSV', 
                                        command=lambda: self.parse_event(software.get()))
        self.parse_file.pack(padx=5, pady=5)
        self.parse_file.configure(state='disabled')

        self.success_run = ctk.CTkLabel(self.content2, text='', width=180, height=25, 
                                        fg_color='white', corner_radius=5)
        self.success_run.pack(padx=5, pady=10)
        self.success_run.configure(state='disabled')
        self.success_run.pack_forget()

        self.gui.mainloop()

    def parse_event(self, software):
        global success 
        success = False
        if self.create_write_file():
            if software == 'pockettopo':
                success = self.parse_pockettopo()
            elif software == 'topodroid':
                success = self.parse_topodroid()
            self.success_run.pack() 
            if success:
                winsound.MessageBeep()
                self.success_run.configure(text='Uspješna konverzija!')
            else:
                self.success_run.configure(text='Pogreška!')
            self.gui.update()
        
    def create_write_file(self):
        global write_file_path
        self.sign = self.survey_sign.get()
        if self.sign == '':
            messagebox.showwarning('Oprez','Bez predznaka Excel će prepoznati točke kao brojeve i maknuti nule!')
        write_file_path = ctk.filedialog.asksaveasfilename(initialdir='SurveyScraper', title='Pohrani csv datoteku', 
                                                        defaultextension=".csv", initialfile=f'{name_for_file}_glavni_vlakovi')
        if write_file_path == '':
            return False
        try:
            with open(write_file_path, 'w') as file:
                file.write(f"od,do,udaljenost,azimut,nagib\n")
                return True
        except IOError:
            messagebox.showerror('Pogreška - otvorena datoteka','Nije moguće kreirati csv datoteku! Molim zatvori datoteku!')
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
        self.gui_md.title('Magnetska deklinacija')
        self.gui_md.grab_set()
        self.gui_md.resizable(False,False)
        self.md_val = 0

        def get_location(location):
            global latitude, longitude
            if location != '':
                self.get_coord_btn.configure(text='Povlačim...')
                self.lat_input.delete(0,ctk.END)
                self.lon_input.delete(0,ctk.END)
                lat_lon_app = Retrieve_lat_lon(location)
                latitude, longitude = lat_lon_app.retrieve_lat_lon()
                self.lat_input.insert(0,f'{latitude:.4f}')
                self.lon_input.insert(0,f'{longitude:.4f}')
                self.map.set_address(location, marker=True)
                self.map.set_zoom(13)
            else:
                messagebox.showerror('Pogreška','Prazan unos!')
            self.get_coord_btn.configure(text='Povuci koordinate')

        # LOCATION FRAME
        self.location_frame = ctk.CTkFrame(self.gui_md)
        self.location_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=5)
        self.location_frm_label = ctk.CTkLabel(self.location_frame, text="Lokacija:", font=('Roboto', 14))
        self.location_frm_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.location_label = ctk.CTkLabel(self.location_frame, text="Upiši lokaciju: ", font=('Roboto', 12))
        self.location_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.location_input = ctk.CTkEntry(self.location_frame, width=120, height=20, font=('Roboto', 12))
        self.location_input.grid(row=1, column=1, padx=10, pady=5)
        self.get_coord_btn = ctk.CTkButton(self.location_frame, width=150, text='Dohvati koordinate',
                                        command=lambda: get_location(self.location_input.get()))
        self.get_coord_btn.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
        Hovertip(self.location_input,'Možeš upisati i adresu (ulica i mjesto odvojeni zarezom)', hover_delay=500)
        self.lat_label = ctk.CTkLabel(self.location_frame, text="Geografska širina: ", font=('Roboto', 12))
        self.lat_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.lat_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lat_input.grid(row=3, column=1,  pady=5)
        self.lat_N = ctk.CTkLabel(self.location_frame, text="N", font=('Roboto', 12))
        self.lat_N.grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.lon_label = ctk.CTkLabel(self.location_frame, text="Geografska dužina: ", font=('Roboto', 12))
        self.lon_label.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.lon_input = ctk.CTkEntry(self.location_frame, width=100, height=20, font=('Roboto', 12))
        self.lon_input.grid(row=4, column=1,  pady=5)
        self.lon_E = ctk.CTkLabel(self.location_frame, text="E", font=('Roboto', 12))
        self.lon_E.grid(row=4, column=2, padx=5, pady=5, sticky='w')

        self.map = tkintermapview.TkinterMapView(self.location_frame, width=100, height=300, corner_radius=15)
        self.map.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.map.set_position(44.2672, 15.8422) #approximately a geographical midpoint of Croatia
        self.map.set_zoom(6)

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
        self.date_label = ctk.CTkLabel(self.date_frame, text="Datum:", font=('Roboto', 14))
        self.date_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='ew')
        self.date_day = ctk.CTkLabel(self.date_frame, text="Dan:")
        self.date_day.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        selected_day = ctk.StringVar(value=current_day)
        self.day_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,32)], variable=selected_day)
        self.day_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.date_month = ctk.CTkLabel(self.date_frame, text="Mjesec:")
        self.date_month.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        selected_month = ctk.StringVar(value=current_month)
        self.month_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=[str(i) for i in range(1,13)], variable=selected_month)
        self.month_combo.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.date_year = ctk.CTkLabel(self.date_frame, text="Godina:")
        self.date_year.grid(row=3, column=0, padx=10, pady=5, sticky='e')
        selected_year = ctk.StringVar(value=current_year)
        year_range = [str(y) for y in range(2019,int(current_year)+2)]
        self.year_combo = ctk.CTkComboBox(self.date_frame, width=60, height=20, values=sorted(year_range, reverse=True), variable=selected_year)
        self.year_combo.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        def get_md(model, year, month, day):
            try:
                datetime.datetime(int(year),int(month),int(day))
            except ValueError:
                messagebox.showerror('Pogreška','Datum je neispravan! Ponovi!')
            if self.lat_input.get() == '' or self.lon_input.get() == '':
                messagebox.showerror('Pogreška','Lokacija nije definirana!')
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
        self.calc_md_btn = ctk.CTkButton(self.decl_frame, width=100, text='Izračunaj',
                                        command=lambda: get_md(self.model.get(),self.year_combo.get(),self.month_combo.get(),self.day_combo.get()))
        self.calc_md_btn.grid(row=0, column=0, columnspan=3, padx=5, pady=10)
        self.md_value_lbl = ctk.CTkLabel(self.decl_frame, text='Magn. deklinacija:')
        self.md_value_lbl.grid(row=1, column=0, padx=5, pady=5)
        self.md_value = ctk.CTkLabel(self.decl_frame, text='', width=80, height=25, fg_color='white', corner_radius=5)
        self.md_value.grid(row=1, column=1, padx=5, pady=5)
        self.md_value.configure(state='disabled')
        self.md_value_deg = ctk.CTkLabel(self.decl_frame, text='°')
        self.md_value_deg.grid(row=1, column=2, padx=5, pady=5)

        # EXECUTE BUTTON
        self.include_md_btn = ctk.CTkButton(self.gui_md, width=150, text='Uračunaj', command=apply_md)
        self.include_md_btn.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.include_md_btn.configure(state='disabled')

if __name__ == '__main__':
    SurveyScraper()