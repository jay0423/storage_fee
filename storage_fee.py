import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta



class MakeDataFrame:

    def __init__(self):
        # 初期値
        self.DAYS = 4000 # 生成日数
        self.FROM_YEAR = 2010 #初期の年
        self.FROM_MONTH = 3 #初期の月
        self.EFFECTIVE_RATE = 0.3 # 有効率：取得する日数の割合
    
    def main(self):
        # 日付のリスト生成()
        date_list = [datetime(self.FROM_YEAR, self.FROM_MONTH, 1) + timedelta(days=i) for i in range(self.DAYS)]
        db = pd.DataFrame({"date": date_list})

        # 入庫と出荷を追加
        db["warehousing"] = [random.randint(0,20) for i in range(len(db))]
        db["shipping"] = [random.randint(0,20) for i in range(len(db))]

        # ランダムに日にちを絞り，並び替える
        effective_list = random.sample([i for i in range(len(db))], int(self.EFFECTIVE_RATE * len(db))) 
        db = db.iloc[effective_list, :]

        return db



class Stocks:

    first_year = 0
    
    def __init__(self, db):
        self.FIRST_STOCKS = 1000 # 在庫数の初期値
        self.db = db

    def get_year_month_range(self):
        # 年月の範囲を修得する
        db_sort = self.db.sort_values("date")
        first_year = db_sort.iloc[0].date.year
        first_month = db_sort.iloc[0].date.month
        last_year = db_sort.iloc[-1].date.year
        last_month = db_sort.iloc[-1].date.month
        return first_year, first_month, last_year, last_month
    
    def make_year_month_list(self):
        # 範囲のリストを生成する．
        self.first_year, first_month, last_year, last_month = self.get_year_month_range()
        year_list = list(range(self.first_year, last_year + 1))
        month_list = list(range(1, 13)) * len(year_list)
        month_list = month_list[first_month-1: -(12-last_month)]
        year_list_all = []

        if len(year_list) >= 2:
            year_list_all += [year_list[0]] * (12 - first_month + 1)
            for i in range(len(year_list) - 2):
                year_list_all += [year_list[i+1]] * 12
            year_list_all += [year_list[-1]] * last_month
        elif len(year_list) == 1:
            year_list_all += [year_list[0]] * len(month_list)

        return month_list, year_list_all

    def make_stocks(self, year, month, stocks):
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        db1 = self.db[self.db["date"] >= datetime(year, month, 1)]
        db2 = db1[db1["date"] < datetime(next_year, next_month, 1)]
        #print(db2)
        
        # 前月末残
        db1 = self.db[self.db["date"] >= datetime(year, month, 1)]
        db1 = db1[db1["date"] <= datetime(year, month, 10)]
        last_stocks = db1["warehousing"].sum() - db1["shipping"].sum() + stocks
        #当月10日残
        db1 = self.db[self.db["date"] >= datetime(year, month, 11)]
        db1 = db1[db1["date"] <= datetime(year, month, 20)]
        ten_stocks = db1["warehousing"].sum() - db1["shipping"].sum() + last_stocks
        #当月20日残
        db1 = self.db[self.db["date"] >= datetime(year, month, 21)]
        db1 = db1[db1["date"] < datetime(next_year, next_month, 1)]
        twenty_stocks = db1["warehousing"].sum() - db1["shipping"].sum() + ten_stocks
        #当月入庫
        stocks_on_the_day = db2.warehousing.sum()
        
        return last_stocks, ten_stocks, twenty_stocks, stocks_on_the_day

    def get_seki(self, storage_fee_db):
        # 積数
        print("積数の合計：", storage_fee_db["sekisu"].sum())

    def main(self):
        # main
        month_list, year_list_all = self.make_year_month_list()
        year = self.first_year
        last_stocks_list = []
        ten_stocks_list = []
        twenty_stocks_list = []
        stocks_on_the_day_list = []
        twenty_stocks_m = self.FIRST_STOCKS
        for month in month_list:
            last_stocks_m, ten_stocks_m, twenty_stocks_m, stocks_on_the_day_m = self.make_stocks(year, month, twenty_stocks_m)
            last_stocks_list.append(last_stocks_m)
            ten_stocks_list.append(ten_stocks_m)
            twenty_stocks_list.append(twenty_stocks_m)
            stocks_on_the_day_list.append(stocks_on_the_day_m)

            if month == 12:
                year += 1

        storage_fee_dict = {
            "year": year_list_all,
            "month": month_list,
            "last_stocks": last_stocks_list,
            "ten_stocks": ten_stocks_list,
            "twenty_stocks": twenty_stocks_list,
            "stocks_on_the_day": stocks_on_the_day_list
        }
        storage_fee_db = pd.DataFrame(storage_fee_dict)

        storage_fee_db["sekisu"] = storage_fee_db["last_stocks"] + storage_fee_db["ten_stocks"] + storage_fee_db["twenty_stocks"] + storage_fee_db["stocks_on_the_day"]
        print("積数の合計：", storage_fee_db["sekisu"].sum())
    
        return storage_fee_db



class Stocks2(Stocks):
    
    def make_year_month_list2(self):
        month_list, year_list_all = self.make_year_month_list()
        year_month_list = []
        for year, month in zip(year_list_all, month_list):
            year_month_list.append(str(year) + "-" + str(month))
        return year_month_list

    # 識別器
    def identification(self, date):
        # stock_type：0=last_stocks, 1=ten_stocks, 2=twenty_stocks
        if date.day >= 1 and date.day <= 10:
            stock_type = 0
        elif date.day >= 11 and date.day <= 20:
            stock_type = 1
        else:
            stock_type = 2
        # year_month
        year_month = str(date.year) + "-" + str(date.month)
        return stock_type, year_month

    def get_dicts(self):
        year_month_list = self.make_year_month_list2()

        last_stocks_dict = dict.fromkeys(year_month_list, 0)
        ten_stocks_dict = dict.fromkeys(year_month_list, 0)
        twenty_stocks_dict = dict.fromkeys(year_month_list, 0)
        stocks_on_the_day_dict = dict.fromkeys(year_month_list, 0)
        for a, b in self.db.iterrows():
            date = b.date.date()
            warehousing = b.warehousing
            shipping = b.shipping
            # 識別器
            stock_type, year_month = self.identification(date)
            # 加算
            stocks_on_the_day_dict[year_month] += warehousing
            if stock_type == 0:
                last_stocks_dict[year_month] += warehousing - shipping
            elif stock_type == 1:
                ten_stocks_dict[year_month] += warehousing - shipping
            elif stock_type == 2:
                twenty_stocks_dict[year_month] += warehousing - shipping

        return last_stocks_dict, ten_stocks_dict, twenty_stocks_dict, stocks_on_the_day_dict
        
    def increace_decreace_table(self):
        # 増減表の作成
        last_stocks_dict, ten_stocks_dict, twenty_stocks_dict, stocks_on_the_day_dict = self.get_dicts()
        keys = list(last_stocks_dict.keys())
        last_stocks_list = list(last_stocks_dict.values())
        ten_stocks_list = list(ten_stocks_dict.values())
        twenty_stocks_list = list(twenty_stocks_dict.values())
        stocks_on_the_day_list = list(stocks_on_the_day_dict.values())

        storage_fee_dict = {
            "year-month": keys,
            "last_stocks": last_stocks_list,
            "ten_stocks": ten_stocks_list,
            "twenty_stocks": twenty_stocks_list,
            "stocks_on_the_day": stocks_on_the_day_list
        }
        storage_fee_db = pd.DataFrame(storage_fee_dict)

        return storage_fee_db

    def main(self):
        last_stocks_dict, ten_stocks_dict, twenty_stocks_dict, stocks_on_the_day_dict = self.get_dicts()
        keys = list(last_stocks_dict.keys())
        last_stocks_list = list(last_stocks_dict.values())
        ten_stocks_list = list(ten_stocks_dict.values())
        twenty_stocks_list = list(twenty_stocks_dict.values())
        stocks_on_the_day_list = list(stocks_on_the_day_dict.values())

        stocks = self.FIRST_STOCKS
        for year_month in keys:
            last_stocks_dict[year_month] += stocks
            stocks = last_stocks_dict[year_month]
            ten_stocks_dict[year_month] += stocks
            stocks = ten_stocks_dict[year_month]
            twenty_stocks_dict[year_month] += stocks
            stocks = twenty_stocks_dict[year_month]

        last_stocks_list = list(last_stocks_dict.values())
        ten_stocks_list = list(ten_stocks_dict.values())
        twenty_stocks_list = list(twenty_stocks_dict.values())
        stocks_on_the_day_list = list(stocks_on_the_day_dict.values())

        storage_fee_dict = {
            "year-month": keys,
            "last_stocks": last_stocks_list,
            "ten_stocks": ten_stocks_list,
            "twenty_stocks": twenty_stocks_list,
            "stocks_on_the_day": stocks_on_the_day_list
        }
        storage_fee_db = pd.DataFrame(storage_fee_dict)

        # 積数
        storage_fee_db["sekisu"] = storage_fee_db["last_stocks"] + storage_fee_db["ten_stocks"] + storage_fee_db["twenty_stocks"] + storage_fee_db["stocks_on_the_day"]
        print("積数の合計：", storage_fee_db["sekisu"].sum())
        return storage_fee_db