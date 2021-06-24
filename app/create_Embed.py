import discord
from datetime import datetime

def create_Position_Embed(pos, bybit_ex):

    title = "Unknown Position"

    if pos['side'] == 'None':
        title = "No Open Postion"
        embed = discord.Embed(title=title, description="", color=discord.Colour.green())
        embed.add_field(name="Timestamp", value=str(datetime.now()), inline=True)
        return embed
    if pos['side'] == 'Buy':
        #title = str(pos['size']) + " " + pos['symbol'] + " Long at " + str(pos['leverage']) + "x"
        title = "{:,}".format(int(pos['size'])) + " " + pos['symbol'] + " Long at " + str(pos['leverage']) + "x"
    if pos['side'] == 'Sell':
        title = "{:,}".format(int(pos['size'])) + " " + pos['symbol'] + " Short at " + str(pos['leverage']) + "x"    

    desc = ""
    embed = discord.Embed(title=title, description=desc, color=discord.Colour.green())

    #winning trade
    if pos['unrealised_pnl'] >= 0:
        embed.set_thumbnail(url="https://s.yimg.com/ny/api/res/1.2/HI0nwiwd8kyYJVK5ekQBww--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTY2Ny43NzY-/https://media.zenfs.com/en/business_insider_articles_888/162af381ac920e354cfb7430466616c4")
        #embed.set_thumbnail(url="https://media4.giphy.com/media/3ohryhNgUwwZyxgktq/giphy.gif")
    #losing trade
    else:
        embed.colour = discord.Colour.red()
        embed.set_thumbnail(url="http://econintersect.com/images/2017/06/51080866losing.trade.JPG")

    market_price = bybit_ex.get_market_price(pos['symbol'])
    unrel_dollar = float(market_price) * float(pos['unrealised_pnl'])
    unrel_coin = "{:,.6f}".format(float(pos['unrealised_pnl'])) + " " + pos['symbol'][0:3]
    daily_rel_dollar = float(market_price) * float(pos['realised_pnl'])

    embed.add_field(name="Market Price", value="{:,.2f}".format(float(market_price)), inline=True)
    embed.add_field(name="Entry Price", value="{:,.2f}".format(float(pos['entry_price'])), inline=True)
    embed.add_field(name="Liquidation Price", value="{:,.2f}".format(float(pos['liq_price'])), inline=True)

    embed.add_field(name="Unrealised PnL", value=unrel_coin, inline=True)
    embed.add_field(name="in Dollar", value="{:,.2f}".format(unrel_dollar) + " USD", inline=True)
    embed.add_field(name="Closing Fee", value="{:,.4f}".format(float(pos['occ_closing_fee'])), inline=True)
    
    embed.add_field(name="Stop Loss", value="{:,.2f}".format(float(pos['stop_loss'])), inline=True)
    embed.add_field(name="Take Profit", value="{:,.2f}".format(float(pos['take_profit'])), inline=True)
    
    embed.add_field(name="Last updated", value=str(pos['updated_at']), inline=False)

    embed.add_field(name="Realised PnL", value="{:,.6f}".format(float(pos['realised_pnl'])), inline=True)
    embed.add_field(name="in Dollar", value="{:,.2f}".format(daily_rel_dollar) + " USD", inline=True)
    return embed

def create_active_order_Embed(order):
    desc = ""
    if order['side'] == 'Buy':
        title = "{:,}".format(int(order['qty'])) + " " + order['symbol'] + " Long " + order['order_type'] + " Order"
        embed = discord.Embed(title=title, description=desc, color=discord.Colour.green())
    if order['side'] == 'Sell':
        title = "{:,}".format(int(order['qty'])) + " " + order['symbol'] + " Short " + order['order_type'] + " Order"
        embed = discord.Embed(title=title, description=desc, color=discord.Colour.red())

    embed.add_field(name="Price", value="{:,.2f}".format(float(order['price'])), inline=True) 
    embed.add_field(name="Quantity", value="{:,}".format(int(order['qty'])), inline=True)
    embed.add_field(name="Last Update", value=str(order['updated_at']), inline=False)
    embed.add_field(name="Order ID", value=str(order['order_id']), inline=False)

    return embed

def create_exec_order_Embed(order):
    desc = ""
    if order['side'] == 'Buy':
        title = "{:,}".format(int(order['exec_qty'])) + " " + order['symbol'] + " " + order['order_type'] + " Buy " + " Order"
        embed = discord.Embed(title=title, description=desc, color=discord.Colour.green())
    if order['side'] == 'Sell':
        title = "{:,}".format(int(order['exec_qty'])) + " " + order['symbol'] +  " " + order['order_type'] + " Sell " + " Order"
        embed = discord.Embed(title=title, description=desc, color=discord.Colour.red())

    embed.add_field(name="Executed Price", value="{:,.2f}".format(float(order['exec_price'])), inline=True) 
    embed.add_field(name="Quantity", value="{:,}".format(int(order['exec_qty'])), inline=True)
    embed.add_field(name="Execution Fee", value="{:,.6f}".format(float(order['exec_fee'])), inline=True)

    embed.add_field(name="Trade Time", value=str(datetime.fromtimestamp(order['trade_time_ms'] / 1000.0)), inline=False)

    embed.add_field(name="Transaction ID", value=str(order['exec_id']), inline=False)

    return embed

def create_fund_record_Embed(pnl, bybit_ex):

    desc = ""
    title = "{:,.6f}".format(float(pnl['amount'])) + " " + str(pnl['coin']) + " realized"
    embed = discord.Embed(title=title, description=desc, color=discord.Colour.green())

    if pnl['amount'] < 0:
        embed.colour = discord.Colour.red()

    new_balance = "{:,.6f}".format(float(pnl['wallet_balance'])) + " " + pnl['coin']
    amount = "{:,.6f}".format(float(pnl['amount'])) + " " + pnl['coin']

    market_price = bybit_ex.get_market_price(pnl['address'])

    usd_amount = "{:,.2f}".format(float(market_price) * float(pnl['amount']))
    new_balance_usd = "{:,.2f}".format(float(pnl['wallet_balance']) * float(market_price)) + " USD"

    embed.add_field(name="Amount", value=amount, inline=True) 
    embed.add_field(name="in USD", value=usd_amount, inline=True)
    embed.add_field(name="Empty", value="USD", inline=True)

    embed.add_field(name="New Balance", value=new_balance, inline=True)
    embed.add_field(name="in USD", value=new_balance_usd, inline=True)
    embed.add_field(name="Execution Time", value=str(pnl['exec_time']), inline=False)

    return embed

def create_pnl_Embed(pnl, bybit_ex):

    desc = ""
    title = "{:,.6f}".format(float(pnl['closed_pnl'])) + " " + str(pnl['symbol'][0:3])
    embed = discord.Embed(title=title, description=desc, color=discord.Colour.green())

    if pnl['closed_pnl'] < 0:
        embed.colour = discord.Colour.red()

    amount = "{:,.6f}".format(float(pnl['closed_pnl'])) + " " + pnl['symbol'][0:3]

    market_price = bybit_ex.get_market_price(pnl['symbol'])
    usd_amount = "{:,.2f}".format(float(market_price) * float(pnl['closed_pnl']))

    embed.add_field(name="Amount", value=amount, inline=True) 
    embed.add_field(name="in USD", value=usd_amount, inline=True)
    embed.add_field(name="Side", value=pnl['side'], inline=True)

    embed.add_field(name="Avg. Entry", value="{:,.2f}".format(float(pnl['avg_entry_price'])), inline=True)
    embed.add_field(name="Avg. Exit", value="{:,.2f}".format(float(pnl['avg_exit_price'])), inline=True)
    embed.add_field(name="Quantity", value="{:,}".format(int(pnl['qty'])), inline=True)
    
    embed.add_field(name="Execution Time", value=str(datetime.fromtimestamp(pnl['created_at'])), inline=False)

    return embed

    
