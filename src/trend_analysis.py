from pytrends.request import TrendReq

pytrends = TrendReq(hl='id-ID', tz=360)

def get_trend(keyword):
    pytrends.build_payload([keyword], timeframe='2020-01-01 2025-12-01', geo='ID')
    return pytrends.interest_over_time()
