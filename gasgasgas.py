from requests import get

HEADERS = {
    'content-type': 'application/json; charset=utf-8',
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
}

class gasoline:
    def __init__(self):
        self.lpg = 'https://www.bp.com/bp-tr-pump-prices/api/PumpPrices?strCity=%C4%B0STANBUL%20(AVRUPA)'
        self.gasoline = 'https://api.opet.com.tr/api/fuelprices/prices?ProvinceCode=934&IncludeAllProducts=true'        

    def get_prices(self):
        return get(self.gasoline, headers = HEADERS).json()

    def get_lpg(self):
        return get(self.lpg, headers = HEADERS).json()

    def return_prices(self):
        "Returns the prices with the order --> gasoline, diesel, lpg"
        gas = self.get_prices()
        lpg = self.get_lpg()

        gasoline = gas[0]['prices'][0]['amount']
        diesel = gas[0]['prices'][2]['amount']
        lpg_price = lpg[0]['LpgPrice']

        return [gasoline, diesel, float(lpg_price)]
