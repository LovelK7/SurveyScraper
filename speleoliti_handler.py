import os
import sys
import time
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class Speleoliti_online():
    """
    This script handles Speleoliti Online (https://speleoliti.speleo.net/online/app_en.html)
    Methods: constructor, open_object, retrieve_cave_data, find_highest_point, update_fixed_station
    """
    def __init__(self, headless, survey_path=None):
        """Initialize Selenium ChromeDriver"""

        self.online = True
        try:
            driver_path = ChromeDriverManager().install()
        except: # Exception as e:
            #messagebox.showerror('Error', f'Error accessing Speleoliti Online !\n\n{e} \n\n Try using SurveyScraper offline!')
            self.online = False
        #driver_path = 'c:/Users/Lovel.IZRK-LK-NB/.wdm/drivers/chromedriver/win64/120.0.6099.225/chromedriver-win32/chromedriver.exe'
        if self.online:
            service = Service(driver_path)
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging']) # surpress DevTools listening
            options.add_argument('--log-level=0')
            options.set_capability("browserVersion", "117")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-logging')
            self.headless = headless
            if headless:
                options.add_argument("--headless=new")
            try:
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                messagebox.showerror('Error', f'Error initializing ChromeDriver: !\n\n{e}')
                self.driver.quit()
            if not headless:
                self.driver.minimize_window()
                self.handle_of_the_window = self.driver.current_window_handle
            self.url = f"https://speleoliti.speleo.net/online/app_en.html"
            # Access survey data file
            survey_data_filename = 'survey_data.json'
            if getattr(sys,'frozen', False): #check if the app runs as a script or as a frozen exe file
                self.survey_data_filepath = os.path.join(os.path.dirname(sys.executable), survey_data_filename)
            elif __file__:
                self.survey_data_filepath = os.path.join(os.path.dirname(__file__), survey_data_filename)
            else:
                self.survey_data_filepath = survey_path    

    def open_empty_object(self):
        """Opens an empty window of Speleoliti Online"""
        self.driver.get(self.url)

    def open_object(self):
        """Opens a cave survey file into Speleoliti Online"""
        try:
            self.driver.get(self.url)
            WebDriverWait(self.driver, 3).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="DefOpt2"]'))).click()
            self.driver.find_element("xpath",'//*[@id="impexRadio_file"]').click() # find file import radiobutton
            file_input = self.driver.find_element("xpath",'//*[@id="UploadFileFld"]') # insert cave survey file path
            file_input.send_keys(self.survey_data_filepath)   # direct input of json file content to an input field    
            self.driver.find_element("xpath",'//*[@id="impex"]/table/tbody/tr/td/div/input').click() # confirm import
            WebDriverWait(self.driver, 3).until(expected_conditions.alert_is_present())
            self.driver.switch_to.alert.accept() # accept alert message
        except Exception as e:
            messagebox.showerror('Error', f'Error while opening object!\n\n{e}')
            return e

    def retrieve_cave_data(self):
        """retrieve survey data from"""
        poly_length = self.driver.find_element("xpath",'//*[@id="table99"]/tbody/tr[4]/td[2]').text.split()[0]
        hor_length = self.driver.find_element("xpath",'//*[@id="table99"]/tbody/tr[5]/td[2]').text.split()[0]
        elevation = self.driver.find_element("xpath",'//*[@id="table99"]/tbody/tr[6]/td[2]').text.split()[0]
        depth = self.driver.find_element("xpath",'//*[@id="table99"]/tbody/tr[7]/td[2]').text.split()[0]
        return poly_length, hor_length, elevation, depth

    def find_highest_point(self):
        """Find highest elevated station so it becomes the fixed station by default"""
        try:
            WebDriverWait(self.driver, 3).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="ico_coords"]'))).click()
            #self.driver.find_element("xpath",'//*[@id="ico_coords"]').click() # switch to coordinate table
            data_tbl = self.driver.find_element("xpath",'//*[@id="table2b"]/tbody')
            station_alts = {}
            for index, row in enumerate(data_tbl.find_elements('xpath','.//tr')):
                if index == 0:
                    continue
                station = row.find_element('xpath',f'//*[@id="table2b"]/tbody/tr[{index+1}]/td[1]').text
                alt = row.find_element('xpath',f'//*[@id="table2b"]/tbody/tr[{index+1}]/td[4]/div').text
                station_alts[station] = float(alt)
            self.driver.find_element("xpath",'//*[@id="ico_main"]').click() # return to main menu
            key_of_max_value = max(station_alts, key=station_alts.get)
            return key_of_max_value
        except Exception as e:
            messagebox.showerror('Error', f'Error finding the highest point!\n\n{e}')
            return e

    def update_fixed_station(self, fixed_station):
        """Update the given fixed station"""
        try:
            self.driver.find_element("xpath",'//*[@id="ico_survey"]').click() # switch to edit survey table
            fixed_station_elm = self.driver.find_element("xpath",'//*[@id="survey_fix"]') # find fixed station element
            self.driver.execute_script('arguments[0].value = ""', fixed_station_elm) # delete current entry
            fixed_station_elm.click()
            fixed_station_elm.send_keys(fixed_station) # insert new entry
            self.driver.find_element("xpath",'//*[@id="ico_main"]').click() # return to main menu
        except Exception as e:
            messagebox.showerror('Error', f'Error updating the fixed station!\n\n{e}')
            return e
    
    def restore_window(self):
        self.driver.switch_to.window(self.handle_of_the_window)
        self.driver.set_window_rect(0, 0)
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()

#***************        ONLY FOR TESTING     ************************
if __name__ == '__main__':

    curr_time = time.time()
    # Set path to a current cave survey data
    survey_data_filename = 'survey_data.json'
    if getattr(sys,'frozen', False): #check if the app runs as a script or as a frozen exe file
        survey_data_filepath = os.path.join(os.path.dirname(sys.executable), survey_data_filename)
    elif __file__:
        survey_data_filepath = os.path.join(os.path.dirname(__file__), survey_data_filename)

    speleoliti_app = Speleoliti_online(headless=False, survey_path=survey_data_filepath)
    if speleoliti_app.online:
        speleoliti_app.open_object()
        fixed_station = speleoliti_app.find_highest_point()
        speleoliti_app.update_fixed_station(fixed_station)
        dimensions = speleoliti_app.retrieve_cave_data()
        #speleoliti_app.restore_window()
        speleoliti_app.close_driver()
        print(dimensions)
        duration = time.time() - curr_time
        print('Duration: ',duration)
    else:
        print('Unable to reach Speleoliti Online due to internet connection!')