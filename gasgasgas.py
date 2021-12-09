from requests import get

HEADERS = {
    'content-type': 'application/json; charset=utf-8',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

class Opet:
    def __init__(self):
        self.province_code = 934 # default (istanbul european side)
        self.api_page = 'https://api.opet.com.tr/api/fuelprices/prices?ProvinceCode={}&IncludeAllProducts=true'

    def get_prices(self):
        return get(self.api_page.format(self.province_code), headers=HEADERS).json()

    def prices(self):
        response = self.get_prices()
        gasoline = response[0]['prices'][0]['amount']
        diesel = response[0]['prices'][2]['amount']
        return [gasoline, diesel]
