import datetime
from config import TRADE_DCA_PATH, TRADE_Analysis_PATH
import pandas as pd
import numpy as np
import api
import sendFile
from numerize import numerize
# '''
def handle_msg(list_s):
    # return "aasd"
    l = list_s.replace("@", " ").split()
    log = "handle_msg(): msg received.\n"
    # print(xl.active)
    l[0] = l[0].lower()
    if l[0] == "buy" and len(l) > 4:
        return (trade_command(l, log))
    if l[0] == "sell" and len(l) == 5:
        return (trade_command(l, log))
    elif l[0] == "tradeinfo" and len(l) == 2:
        return tradeinfo_command(l)
    elif l[0] == "fetchrealtimedata" and len(l) == 1:
        return fetchrealtimedata()
    # elif l[0] == "alltrades" and len(l) == 1:
    #     return calc_trade_profit()
    elif l[0] == "sendfile" and len(l) == 1:
        return sendFile.fun()
    elif l[0] == "allremarks" and len(l) == 1:
        return all_remarks()
    elif l[0] == "filter" and len(l) == 3 : #filter col_name symbol(=,<,>..) value
        return filter()
    elif l[0] == "setremarks" and len(l) == 3:  #cmd coin remark(sep = '_')
        return set_remarks(l)
    # elif l[0] == "tradehistory" and len(l) == 2:
    #     return tradehistory_command(l)
    elif l[0] == "tradesupby" and len(l) == 3:
        return tradesupby(l)
    else:
        return "Wrong message try again."

# def filter():


def trade_command(l, log):
    log = log + "trade_command(): "
    try:
        date = datetime.date.today()
        # l = list_s.replace("@", " ").split(" ")
        exchange = l[1].lower()
        if exchange not in ["bh", "bk", "by", "ku", "ga"]:
            return log + "wrong CEx - bh, bk, by, ku, ga \n"
        coin = l[2].upper()
        lot_size = float(l[3])
        price = float(l[4])
        try:
            name = l[5]
        except:
            name = " "
        log = log + f"coin:{coin}, CEx:{exchange}\n"
        log = log + trade_dca(exchange, coin, lot_size, price, l[0], name)
        # log = log + log_trade_history(date,exchange,coin,lot_size,price,l[0])
        # print("a")
        return log
    except Exception as e:
        return log + str(e) + "\n"

'''
def log_trade_history(date, exchange, coin, lot_size, price, t):
    log = "log_trade_history: "
    try:
        df_history_trade = pd.read_csv(TRADE_HISTORY_PATH)
        df = pd.concat([df_history_trade, pd.DataFrame(
            {'date': [date], 'exchange': [exchange], 'coin': [coin], 'lot_size': [lot_size], 'at_price': [price],
             'buyorsell': [t]})])
        # print(df)
        df.to_csv(TRADE_HISTORY_PATH, index=False)
        # print("a")
        return log + "success\n"
    except Exception as e:
        return log + str(e) + "\n"
'''
# ===================================== DCA start =============================================
def trade_dca(ex, coin, lot_size, price, buyorsell, name):
    log = "trade_dca: "
    try:
        df = pd.read_csv(TRADE_DCA_PATH)
        df_analysis = pd.read_csv(TRADE_Analysis_PATH)
        # df_analysis =
        if (df.loc[df['coin'] == coin]).empty:
            if buyorsell == "sell":
                return log + "trade not found. can't sell\n"
            df1 = (df.loc[df['coin'] == 'sample']).copy()
            df1.loc[df1['coin'] == 'sample', ['name', 'coin', ex + '_size', ex + "_price"]] = [name.replace("_"," ").replace("-", " "),
                                                                                               coin, lot_size, price]
            # print(df1)
            df = pd.concat([df, df1])

            df2 = (df_analysis.loc[df_analysis['coin'] == 'sample']).copy()
            df2.loc[df2['coin'] == 'sample', ['coin']] = [coin]
            df_analysis = pd.concat([df_analysis, df2])
            df_analysis.to_csv(TRADE_Analysis_PATH, index=False)
        else:
            old_size = (df.loc[df['coin'] == coin]).iloc[0][ex + '_size']
            old_price = (df.loc[df['coin'] == coin]).iloc[0][ex + "_price"]
            old_profit = (df.loc[df['coin'] == coin]).iloc[0]["profit"]
            if buyorsell == "buy":
                df.loc[df['coin'] == coin, [ex + '_price', ex + "_size"]] = dca_price_buy(old_price, old_size, price,
                                                                                          lot_size)
            else:
                temp = dca_price_sell(old_price, old_size, price, lot_size)
                if temp == False:
                    # tradeinfo_command(["c",coin])
                    return log + "Failed - no trades\n" + tradeinfo_command(["tradeinfo", coin])

                elif temp[1] == 0:
                    df.loc[df['coin'] == coin, [ex + '_price', ex + "_size", 'profit']] = [0, 0, old_profit + temp[0]]
                else:
                    df.loc[df['coin'] == coin, [ex + "_size", 'profit']] = [temp[1], old_profit + temp[0]]
                    # df.loc[df['coin'] == coin, [ex + '_price', ex + "_size"]] = [temp[0] / temp[1], temp[1]]
        # print(df)
        df.to_csv(TRADE_DCA_PATH, index=False)
        # print("a")
        return log + "success\n" + tradeinfo_command(["tradeinfo", coin])
    except Exception as e:
        return log + str(e) + "\n"

def dca_price_buy(old_price, old_size, new_price, new_size):
    updated_size = old_size.item() + new_size
    updated_price = ((old_size.item() * old_price.item()) + (new_size * new_price)) / updated_size
    return [updated_price, updated_size]

def dca_price_sell(old_price, old_size, new_price, new_size):
    if old_price == 0 or old_size == 0:
        return False
    updated_size = old_size.item() - new_size
    # if updated_size==0:
    profit = (new_price * new_size) - (old_price.item() * new_size)
    # updated_price = (old_size.item() * old_price.item()) - (new_size * new_price)
    return [profit, updated_size]

# ===================================== DCA start =============================================
def set_remarks(l):   #cmd coin remarks_
    try:
        # l = "setremarks bnb monitoring_hgh".split()
        df = pd.read_csv(TRADE_Analysis_PATH)
        coin_name = l[1].upper()
        if (df["coin"].str.upper() == coin_name).any():
            # Update remarks where the coin matches, ensuring the case matches
            df.loc[df["coin"].str.upper() == coin_name, "remarks"] = l[2].replace("_", " ")
            df.to_csv(TRADE_Analysis_PATH, index=False)
            return ("Success: Remarks updated.")
        else:
            return (f"Coin '{l[1]}' not present.")
        # print(df)
        # return "success"
    except Exception as e:
        return (f"Error: {e}")

def all_remarks():
    try:
        df = pd.read_csv(TRADE_Analysis_PATH)
                # Filter out rows where 'remarks' is NaN or empty
        filtered_df = df.dropna(subset=["remarks"])
        s = "\n".join(filtered_df.apply(lambda row: f"'{row['coin']}' : {row['remarks']}" if not row['coin'] == 'sample' else '',axis=1))
        # print(s)
        return s
    except Exception as e:
        return str(e) + "\n"

def tradeinfo_command(cmd):
    coin = cmd[1].upper()
    try:
        df = pd.read_csv(TRADE_Analysis_PATH)
        if (df.loc[df['coin'] == coin]).empty:
            return f"No Trades for {coin}"
        else:
            s = ''
            df1 = df.loc[df['coin'] == coin]
            for col in df1:
                if df1[col].iloc[0] != 0 and not (pd.isnull(df1[col].iloc[0])):
                    if cmd[0] == "tradeinfo":
                        s = s + f"'{col}' : {df1[col].iloc[0]}\n"
                    else:
                        s = s + f"'{col}' : {df1[col].iloc[0]}\t"
            return s
    except Exception as e:
        return str(e) + "\n"


def calc_trade_profit():            # tgbot cmd = alltrades
    log = "calculate profits of all trades - "
    try:
        df = pd.read_csv(TRADE_DCA_PATH)
        # print(df.head())
        df_analysis = pd.read_csv(TRADE_Analysis_PATH)
        df_analysis['bk_curr_profit'] = np.where(df['bk_price'] != 0.0, (df['curr_price'] - df['bk_price']) * 100 / df['bk_price'],
                                        np.nan)
        df_analysis['bh_curr_profit'] = np.where(df['bh_price'] != 0.0, (df['curr_price'] - df['bh_price']) * 100 / df['bh_price'],
                                        np.nan)
        df_analysis['by_curr_profit'] = np.where(df['by_price'] != 0.0, (df['curr_price'] - df['by_price']) * 100 / df['by_price'],
                                        np.nan)
        df_analysis['ku_curr_profit'] = np.where(df['ku_price'] != 0.0, (df['curr_price'] - df['ku_price']) * 100 / df['ku_price'],
                                        np.nan)
        df_analysis.to_csv(TRADE_Analysis_PATH, index=False)
        # log = log + "\n"
        log = log + "success\n"
        # df_new = np.where(df["bk_curr_profit"]>10.0 or df["bk_curr_profit"]<-10.0 )
        # log = log + "\n" +tradeinfo_command(["else",c])
        return log
    except Exception as e:
        return log + str(e) + "\n"

def tradesupby(l):
    log = ""
    perc = int(l[1])
    ex = l[2]
    if ex not in ["bh", "bk", "by", "ku", "ga"]:
        return log + "wrong CEx - bh, bk, by, ku, ga \n"
    try:
        df = pd.read_csv(TRADE_DCA_PATH)
        df["dollar"] = df[ex+"_size"] * df["curr_price"]
        # log = log + f"Exchange: {ex}\n"
        for index,row in df[(df["dollar"]>5) & (df[ex+"_curr_profit"]>perc)].iterrows():
            rounded_dollar = round(row['dollar'])
            rounded_curr_profit = round(row[ex+'_curr_profit'])
            log = log + f"{row['coin']}__{rounded_curr_profit}%__{rounded_dollar}$__{ex}\n"

    except Exception as e:
        return log + str(e) + "\n"
    return log

def fetchrealtimedata():          #tgbot command = fetchrealtimedata
    log = "Fetching latest price- "
    try:
        df = pd.read_csv(TRADE_DCA_PATH)
        df_analysis = pd.read_csv(TRADE_Analysis_PATH)
        json = api.get_all()
        json_df = pd.json_normalize(json)
        df_analysis[['coin','profit']] = df[['coin','profit']]
        # json_df.to_csv(TRADE_DCA_PATH.replace("csv_files/trades", "coinmarketcap"), index = False)
        # print('1')
        for coin in df['coin']:
            name = df[df['coin'] == coin]['name'].values[0]
            try:
            # if True:
            #     print(coin)
                price = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.price'].values[0]
                infinite_supply = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['infinite_supply'].values[0]

                circulating_supply = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['circulating_supply'].values[0]
                max_supply = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['max_supply'].values[0]

                volume_change_24h = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.volume_change_24h'].values[0]
                percent_change_24h = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.percent_change_24h'].values[0]
                percent_change_7d = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.percent_change_7d'].values[0]
                percent_change_30d = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.percent_change_30d'].values[0]
                market_cap = json_df[(json_df['symbol'] == coin) & (json_df['name'] == name)]['quote.USD.market_cap'].values[0]
            except:
                price = 0
                infinite_supply = False
                circulating_supply = 0
                max_supply = 1
                volume_change_24h = 0
                percent_change_24h = 0
                percent_change_7d = 0
                percent_change_30d = 0
                market_cap = 0
            # print("hell")
            market_cap = numerize.numerize(market_cap)
            df_analysis.loc[df_analysis['coin'] == coin, ['curr_price','inf_supply','curr_supply_perc',\
                                        '24h_vol_change','24h_perc_change','7d_perc_change',\
                                        '30d_perc_change','market_cap']] \
                = [price,infinite_supply,(circulating_supply/max_supply)*100,\
                                                                 volume_change_24h,percent_change_24h,\
                                                                 percent_change_7d,percent_change_30d,market_cap]
            df.loc[df['coin'] == coin,['curr_price']] = [price]
        # print('2')
        for i in ["bh", "bk", "by", "ku", "ga"]:
            df_analysis[i+'_usd'] = df[i+"_size"]*df["curr_price"]
        
        df_analysis.to_csv(TRADE_Analysis_PATH, index=False)
        df.to_csv(TRADE_DCA_PATH, index=False)
        # calc_trade_profit(log)
        return log + "Success" + "\n" + calc_trade_profit()
    except Exception as e:
        return log + str(e) + "\n"

'''
def tradehistory_command(cmd):
    coin = cmd[1].upper()
    try:
        df = pd.read_csv(TRADE_HISTORY_PATH)
        if (df.loc[df['coin'] == coin]).empty:
            return f"No Trades for {coin}"
        else:
            s = ''
            df1 = df.loc[df['coin'] == coin]
            for col in df1:
                if df1[col].iloc[0] != 0:
                    s = s + f"{col} : {df1[col].iloc[0]}\n"
            return s
    except Exception as e:
        return str(e) + "\n"
'''