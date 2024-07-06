import datetime
# import openpyxl
from config import EXCEL_FILE_PATH
import pandas as pd

# xl = openpyxl.load_workbook(EXCEL_FILE_PATH)

# df_dca_trade = pd.read_csv(TRADE_DCA_PATH)
# df_dca_trade = pd.read_csv

xl = pd.ExcelFile(EXCEL_FILE_PATH)


# df = pd.read_excel(xl,"trades")
# print(df)

# '''
def handle_msg(list_s):
    # return "aasd"
    l = list_s.replace("@", " ").split()
    log = "handle_msg(): msg received.\n"
    # xl.active= xl["trade_history"]
    # print(xl.active)
    if l[0]=="trade" and len(l)==5:
        return (trade_command(l,log))
    else:
        return "Wrong message try again.(5)"

def trade_command(l,log):
    log = log + "trade_command(): "
    try:
        date = datetime.date.today()
        # l = list_s.replace("@", " ").split(" ")
        exchange = l[1]
        if exchange not in ["bh","bk","by","ku","ga"]:
            return log + "wrong CEx - bh, bk, by, ku, ga \n"
        coin = l[2].upper()
        lot_size = int(l[3])
        price = int(l[4])
        log = log + f"coin:{coin}, CEx:{exchange}\n"
        log = log + log_trade_history(date,exchange,coin,lot_size,price)
        # log = log + trade_dca(exchange,coin,lot_size,price,log)
        # print("a")
        return log
    except Exception as e:
        return log + str(e)+"\n"

def log_trade_history(date, exchange, coin, lot_size, price):
    log = "log_trade_history: "
    try:
        xl.active = xl["trade_history"]
        df = pd.read_excel(xl, "trade_history")
        df.append(pd.DataFrame({'date':[date],'exchange':[exchange],'coin':[coin],'lot_size':[lot_size],'at_price':[price]}), ignore_index=True)
        writer = pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl')
        df.to_excel(writer,sheet_name='trade_history')
        writer.save()
        writer.close()
        # print("a")
        return log+"success\n"
    except Exception as e:
        return log + str(e)+"\n"

def trade_dca(date, exchange, coin, lot_size, price, log):
    log = "trade_dca: "
    try:
        df = pd.read_excel(xl, "trades")
        writer = pd.ExcelWriter(EXCEL_FILE_PATH, engine='openpyxl')
        df.to_excel(writer, sheet_name='trades')
        writer.save()
        writer.close()
        # print("a")
        return log+"success\n"
    except Exception as e:
        return log + str(e) + "\n"


# '''