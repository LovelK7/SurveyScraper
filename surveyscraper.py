import re
import os
import winsound
import customtkinter as ctk
from tkinter import messagebox

class SurveyScraper():
    def __init__(self):
        self.gui = ctk.CTk()
        self.gui.title('SScraper')
        self.gui.resizable(False,False)
        self.gui.columnconfigure(0, weight=6)
        self.gui.columnconfigure(1, weight=1)

        def open_readme():
            file_path = 'SurveyScraper/surveyscraper_README.txt'
            readme = ctk.CTkToplevel()
            readme.title('Readme')
            readme.grab_set()
            readme_text = ctk.CTkTextbox(readme,width=650,height=500)
            readme_text.pack()
            try:
                with open(file_path,'r', encoding='utf-8') as readme_file:
                    text = readme_file.read()
                readme_text.insert('0.0',text)
            except IOError as error:
                readme_text.insert('0.0',f'Pogreška prilikom učitanja readme datoteke\n{error}')
            readme_text.configure(state='disabled')

        self.gui_title = ctk.CTkLabel(self.gui, text='SurveyScraper', font=('Roboto', 20))
        self.gui_title.grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.readme = ctk.CTkButton(self.gui, text='?', width=20, font=('Roboto', 12), command=open_readme)
        self.readme.grid(row=0, column=1, padx=10, pady=10)

        self.software_frm = ctk.CTkFrame(self.gui)
        self.software_frm.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.software_lbl = ctk.CTkLabel(self.software_frm, text='Odaberi program: ')
        self.software_lbl.pack(padx=5, pady=5)
        software = ctk.StringVar(self.software_frm)
        td_radiobtn = ctk.CTkRadioButton(self.software_frm, variable=software, text='TopoDroid', value='topodroid')
        td_radiobtn.pack(padx=5, pady=5)
        td_radiobtn.select()
        pt_radiobtn = ctk.CTkRadioButton(self.software_frm, variable=software, text='PocketTopo', value='pockettopo')
        pt_radiobtn.pack(padx=5, pady=5)

        self.content = ctk.CTkFrame(self.gui)
        self.content.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        def open_file_event(software):
            global file_path, name_for_file
            file_path = ctk.filedialog.askopenfilename(initialdir='SurveyScraper', title='Otvori txt datoteku', 
                                                        filetypes = (("Text files","*.txt*"),("CSV file","*.csv"),("all files","*.*")))
            if file_path.endswith('.txt') and software == 'topodroid':
                messagebox.showerror('Pogreška','Za obradu TopoDroid podataka potrebna je csv datoteka!')
                file_path = None
            elif file_path.endswith('.csv') and software == 'pockettopo':
                messagebox.showerror('Pogreška','Za obradu PocketTopo podataka potrebna je txt datoteka!')
                file_path = None
            if file_path:
                file_base_name = os.path.basename(file_path)
                name_for_file = os.path.splitext(file_base_name)[0]
                self.opened_file.configure(text=file_base_name)
                self.parse_file.configure(state='normal')
            
        self.open_file = ctk.CTkButton(self.content, width=180, text='Otvori datoteku s vlakovima', 
                                       command=lambda: open_file_event(software.get()))
        self.open_file.grid(row=0, column=0, padx=5, pady=10, columnspan=2)

        self.opened_file = ctk.CTkLabel(self.content, text='', width=200, height=25)
        self.opened_file.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        self.opened_file.configure(state='disabled')
        
        self.survey_sign_lbl = ctk.CTkLabel(self.content, text='Predznak točaka: ')
        self.survey_sign_lbl.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.survey_sign = ctk.CTkEntry(self.content, width=50, height=25)
        self.survey_sign.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        self.parse_file = ctk.CTkButton(self.content, width=150, text='Generiraj CSV', 
                                        command=lambda: self.parse_event(software.get()))
        self.parse_file.grid(row=3, column=0, padx=5, pady=10, columnspan=2)
        self.parse_file.configure(state='disabled')

        self.gui.mainloop()

    def parse_event(self, software):   
        if self.create_write_file():
            if software == 'pockettopo':
                self.parse_pockettopo()
            elif software == 'topodroid':
                self.parse_topodroid()           
        
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
            shots = []
            for row in file:
                row_data = re.sub(r'\[.\]','',row)
                row_data = re.sub(r'<','',row_data)
                shot = row_data.split()
                if len(shot) == 5: #filter for main shots
                    shots.append(shot)
                if len(shots) == 3:
                    mean_len = (float(shots[0][2])+float(shots[1][2])+float(shots[2][2]))/3
                    mean_dir = (float(shots[0][3])+float(shots[1][3])+float(shots[2][3]))/3
                    mean_inc = (float(shots[0][4])+float(shots[1][4])+float(shots[2][4]))/3
                    if self.sign == '':
                        main_shot = f'{shots[0][0]},{shots[0][1]},{mean_len:.3f},{mean_dir:.2f},{mean_inc:.2f}\n'
                    else:
                        main_shot = f'{self.sign}-{shots[0][0]},{self.sign}-{shots[0][1]},{mean_len:.3f},{mean_dir:.2f},{mean_inc:.2f}\n'
                    with open(write_file_path, 'a') as file:
                        file.write(main_shot)
                    shots.clear()
        winsound.MessageBeep()

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
                        main_shot = f'{shot_from},{shot_to},{shot[2]},{shot[3]},{shot[4]}\n'
                    else:
                        main_shot = f'{self.sign}-{shot_from},{self.sign}-{shot_to},{shot[2]},{shot[3]},{shot[4]}\n'
                    with open(write_file_path, 'a') as file:
                        file.write(main_shot)
        winsound.MessageBeep()

if __name__ == '__main__':
    SurveyScraper()