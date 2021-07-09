import pandas as pd

SP_COUNTRIES = dict([('US', 'data/USStateName.csv'),
                    ('India', 'data/IndiaStateName.csv')])

class SubRegion:
    """
        Finds States/Regions inside Country.
        If Country is not supported / Data is not available of states,
        then asssigns All.
    """
    def __init__(self, country='World'):
        self.country = country

    def find(self, country):
        for sp_country, loc in SP_COUNTRIES.items():
            if country == sp_country:
                return pd.read_csv(loc, sep=',')['State']
        return ['All']

