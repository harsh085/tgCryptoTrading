import datetime
from config import TRADE_DCA_PATH, TRADE_HISTORY_PATH
import pandas as pd
import apiReq as api


    
# '''
def handle_msg(list_s):
    # return "aasd"
    l = list_s.replace("@", " ").split()
    log = "handle_msg(): msg received.\n"
    # print(xl.active)
    l[0]=l[0].lower()
    if l[0]=="buy" and len(l)==5:
        return (trade_command(l,log))
    if l[0]=="sell" and len(l)==5:
        return (trade_command(l,log))
    elif l[0]=="tradeinfo" and len(l)==2:
        return tradeinfo_command(l)
    elif l[0] == "tradehistory" and len(l) == 2:
        return tradehistory_command(l)
    else:
        return "Wrong message try again."

def trade_command(l,log):
    log = log + "trade_command(): "
    try:
        date = datetime.date.today()
        # l = list_s.replace("@", " ").split(" ")
        exchange = l[1].lower()
        if exchange not in ["bh","bk","by","ku","ga"]:
            return log + "wrong CEx - bh, bk, by, ku, ga \n"
        coin = l[2].upper()
        lot_size = float(l[3])
        price = float(l[4])
        log = log + f"coin:{coin}, CEx:{exchange}\n"
        log = log + trade_dca(exchange, coin, lot_size, price,l[0])
        # log = log + log_trade_history(date,exchange,coin,lot_size,price,l[0])
        # print("a")
        return log
    except Exception as e:
        return log + str(e)+"\n"

def dca_price_buy(old_price,old_size, new_price,new_size):
    updated_size = old_size.item()+new_size
    updated_price = ((old_size.item()*old_price.item() )+( new_size*new_price))/updated_size
    return [updated_price,updated_size]

def dca_price_sell(old_price,old_size, new_price,new_size):
    updated_size = old_size.item()-new_size
    # if updated_size==0:
    updated_price = (old_size.item()*old_price.item())-(new_size*new_price)
    return [updated_price,updated_size]

def log_trade_history(date, exchange, coin, lot_size, price,t):
    log = "log_trade_history: "
    try:
        df_history_trade = pd.read_csv(TRADE_HISTORY_PATH)
        df = pd.concat([df_history_trade, pd.DataFrame({'date':[date],'exchange':[exchange],'coin':[coin],'lot_size':[lot_size],'at_price':[price],'buyorsell':[t]})])
        # print(df)
        df.to_csv(TRADE_HISTORY_PATH,index=False)
        # print("a")
        return log+"success\n"
    except Exception as e:
        return log + str(e)+"\n"

def trade_dca(ex, coin, lot_size, price, buyorsell):
    log = "trade_dca: "
    try:
        df = pd.read_csv(TRADE_DCA_PATH)

        if (df.loc[df['coin']==coin]).empty :
            if buyorsell=="sell":
                return log+"trade not found. can't sell\n"
            df1 = (df.loc[df['coin']=='sample']).copy()
            df1.loc[df1['coin']=='sample',['coin',ex + '_size',ex + "_price"]] = [coin,lot_size,price]
            # print(df1)
            df = pd.concat([df,df1])
        else:
            old_size = (df.loc[df['coin'] == coin]).iloc[0][ex + '_size']
            old_price = (df.loc[df['coin'] == coin]).iloc[0][ex + "_price"]
            if buyorsell == "buy":
                df.loc[df['coin'] == coin, [ex + '_price', ex + "_size"]] = dca_price_buy(old_price, old_size, price,lot_size)
            else:
                temp = dca_price_sell(old_price, old_size, price,lot_size)
                if temp[1]==0:
                    df.loc[df['coin'] == coin, [ex + '_price', ex + "_size",'profit']] = [0,0,0-temp[0]]
                else:
                    df.loc[df['coin'] == coin, [ex + '_price', ex + "_size"]] = [temp[0]/temp[1],temp[1]]
        # print(df)
        df.to_csv(TRADE_DCA_PATH, index=False)
        # print("a")
        return log+"success\n"
    except Exception as e:
        return log + str(e) + "\n"

def tradeinfo_command(cmd):
    coin = cmd[1].upper()
    try:
        df = pd.read_csv(TRADE_DCA_PATH)
        if (df.loc[df['coin']==coin]).empty :
            return f"No Trades for {coin}"
        else:
            s = ''
            df1 = df.loc[df['coin']==coin]
            for col in df1:
                if df1[col].iloc[0]!=0:
                    s = s+ f"{col} : {df1[col].iloc[0]}\n"
            return s
    except Exception as e:
        return str(e) + "\n"


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
# '''