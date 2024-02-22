import ast
import json
import requests

class Retrieve_lat_lon():
    def __init__(self, location):
        self.location = location
        self.user_agent = "SurveyScraper/3.0 (https://github.com/LovelK7/SurveyScraper)"

    def retrieve_lat_lon(self):
        """retreive location coordinates through API with requests"""

        url_location = f"https://nominatim.openstreetmap.org/search.php?q={self.location}&format=jsonv2"
        headers = {'User-Agent': self.user_agent}
        response = requests.get(url_location, headers=headers)

        if response.status_code == 200:
            json_result = response.json()
            latitude = float(json_result[0]['lat'])
            longitude = float(json_result[0]['lon'])
            return latitude, longitude
        else:
            print(f'Erorr while accessing nominatim.openstreetmap! \n {response.text}')
            return None, None

class Retrieve_magn_decl():
    def __init__(self, latitude, longitude, model, year, month, day):
        self.latitude = latitude
        self.longitude = longitude
        self.model = model
        self.year = year
        self.month = month
        self.day = day

    def retrieve_magn_decl(self):
        """retreive magnetic declination through API with requests"""
        if self.latitude and self.longitude:
            url_decl = (f"https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?lat1={self.latitude}&lon1={self.longitude}"
                f"&model={self.model}&startYear={self.year}&startMonth={self.month}&startDay={self.day}&key=zNEw7&resultFormat=json")
            response = requests.get(url_decl)
            json_result = response.json()
            magnetic_declination = json_result['result'][0]['declination']
            return magnetic_declination
        else:
            return None

#***************        ONLY FOR TESTING     ************************
if __name__ == '__main__':

    location, model, year, month, day = 'krkuz','IGRF','2022','6','16'
    lat_lon_app = Retrieve_lat_lon(location)
    latitude, longitude = lat_lon_app.retrieve_lat_lon()
    magn_decl_app = Retrieve_magn_decl(latitude, longitude, model, year, month, day)
    print(magn_decl_app.retrieve_magn_decl())