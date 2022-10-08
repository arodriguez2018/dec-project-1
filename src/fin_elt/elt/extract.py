import os
import pandas as pd
import requests
import logging
import jinja2 as j2 


class Extract:

    @staticmethod
    def treasury_yields(
            interval: str,
            maturity: str,
            api_key: str
    ) -> pd.DataFrame:
        """
        Function to extract historical US Treasury Yields (including current day)

        :param interval: granularity of data (daily, weekly, monthly)
        :param maturity: type of bond (3month, 2year, 5year, 7year, 10year, 30year)
        :param api_key: api key to access Alpha Vantage API
        :return: Pandas Dataframe
        """
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s][%(asctime)s]: %(message)s")

        url = f'https://www.alphavantage.co/query?' \
              f'function=TREASURY_YIELD&' \
              f'interval={interval}&' \
              f'maturity={maturity}&' \
              f'apikey={api_key}'

        if api_key:
            r = requests.get(url)
            if r.status_code == 200:
                try:
                    data = r.json()
                    df = pd.json_normalize(data['data'])
                    # Set index to use in load step
                    df = df.set_index('date')
                    return df
                except KeyError:
                    logging.error(f'Error extracting {interval} {maturity} treasury yields from API')
            else:
                logging.error('Call to API - treasury yields - failed.')

    @staticmethod
    def extract_fx_rate(
        from_symbol:str,
        to_symbol:str,
        api_key:str
        )->pd.DataFrame:
        """
        Extracts daily exchange rates.
        - `from_symbol`: The currency symbol from which the exchange occurs.
        - `to_symbol`: The currency symbol into which the exchange occurs.
        
        """
        base_url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol={to_symbol}&outputsize=full&apikey={api_key}'
        r = requests.get(base_url)
        if r.status_code == 200:
            response_data = r.json()
            df = pd.DataFrame(response_data['Time Series FX (Daily)']).transpose().reset_index()
            df = df.rename(columns={ df.columns[0]: "Date" })
            # df['from'] = f'{from_symbol}' # Won't use in case we do only USD in the FROM column
            df['to'] = f'{to_symbol}'
            return df
    
    @staticmethod
    def extract_several_fx_rates():
        """
        TODO
        :return:
        """
        df_currencies = pd.read_csv("data/main_currencies.csv")
        df_concat = pd.DataFrame()
        for currency_name in df_currencies["currency code"]:
            df_extracted = extract_fx_rates(from_symbol=from_symbol, to_symbol=currency_name, api_key=api_key)
            df_concat = pd.concat([df_concat, df_extracted])
        return df_concat.reset_index().drop(labels=["index"], axis=1)