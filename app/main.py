import logging
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

import create_Embed
from bybit_exchange import BybitExchange

#insert discord token
TOKEN = ""

#channel id for different disc channels to post into
#insert channel ids
bybit_positions_channel_id = 0
active_orders_channel_id = 0
realized_pnl_channel_id = 0
exec_orders_channel_id = 0

#setup the logger
logging.basicConfig(filename="./app/logs/info.log", format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

disc_bot = discord.Client()
logger.info(f"Discord Client started")
bybit_ex = BybitExchange(False)

#get a starting time for executed orders
start_time = datetime.today()
#start_time = (start_time - timedelta(days=1)).timestamp()
start_time_ms = start_time.timestamp() * 1000

#all traded asset pairs
symbols = ['BTCUSD', 'ETHUSD']
position_Embed = [0, 0]
active_orders = []
posted_pnl_id = []
posted_exec_orders_id = []

@disc_bot.event
async def on_ready():
    #schedule all the tasks
    print_positions.start()
    print_active_orders.start()
    print_inactive_orders.start()
    print_realized_pnl.start()
    move_time.start()
    logger.info(f"All tasks started")

@tasks.loop(seconds=2.0)
async def print_positions():
    #get the correct channel to post into
    channel = disc_bot.get_channel(bybit_positions_channel_id)
    #create one embed for each symbol
    for i in range(len(symbols)):
        #first iteration, we have to create the embed
        if position_Embed[i] == 0:
            #query api
            logger.info(f"calling get_position")
            pos = bybit_ex.get_position(symbol=symbols[i])
            #check if the api returned something
            if pos == None:
                return
            #create the embed structure, need bybit_ex for market price data
            embed = create_Embed.create_Position_Embed(pos, bybit_ex)
            #post the embed and save the embed to edit it later
            position_Embed[i] = await channel.send(embed=embed)
        #embed is already posted, just edit it
        else:
            #query api
            pos = bybit_ex.get_position(symbol=symbols[i])
            #check if the api returned something
            if pos == None:
                return
            #create the embed structure, need bybit_ex for market price data
            embed = create_Embed.create_Position_Embed(pos, bybit_ex)
            #exchange the embed with the newly created one
            await position_Embed[i].edit(embed=embed)

@tasks.loop(seconds=30.0)
async def print_active_orders():
    #get the correct channel to post into
    channel = disc_bot.get_channel(active_orders_channel_id)
    #create one embed for each symbol
    for i in range(len(symbols)):
        #query bybit api
        orders = bybit_ex.get_active_orders(symbol=symbols[i])
        #check if the api returned something
        if orders == None:
            return
        #iterate through all returned orders
        for order in orders:
            posted_in_disc = False
            #check all orders that are already posted to the channel
            for a in active_orders:
                #if this order id is already postet, we edit it if neccessary
                if a[0] == order.get('order_id'):
                    #order is in posted
                    posted_in_disc = True
                    #if the order is still active, update the embed
                    if order.get('order_status') == 'New' or order.get('order_status') == 'Untriggered' or order.get('order_status') == 'Created':
                        order_embed = create_Embed.create_active_order_Embed(order)
                        await a[1].edit(embed=order_embed)
                    #the order is cancelled or executed, delete the embed
                    else:
                        await a[1].delete()
                        #get the index and remove from the data structure
                        index = active_orders.index(a)
                        active_orders.pop(index)
                    break
            #the order is not already posted
            if posted_in_disc == False:
                #if the order is still active, create the embed
                if order.get('order_status') == 'New' or order.get('order_status') == 'Untriggered':
                    order_embed = create_Embed.create_active_order_Embed(order)
                    #save the message to add it to data structure
                    sent_message = await channel.send(embed=order_embed)
                    active_orders.append([order.get('order_id'), sent_message])

@tasks.loop(seconds=30.0)
async def print_inactive_orders():
    #remove last object if the list gets too big
    if len(posted_exec_orders_id) > 1000:
        posted_exec_orders_id.pop(0)
    #get the correct channel to post into
    channel = disc_bot.get_channel(exec_orders_channel_id)
    #create one embed for each symbol
    for i in range(len(symbols)):
        #query bybit api
        executed_orders = bybit_ex.get_executed_orders(symbol=symbols[i], start_time=str(int(start_time_ms)))
        #check if the api returned something
        if executed_orders == None:
            return
        #iterate through all returned objects
        for exec_order in executed_orders:
            if exec_order.get('order_id') not in posted_exec_orders_id:
                #create embed and post it
                order_embed = create_Embed.create_exec_order_Embed(exec_order)
                await channel.send(embed=order_embed)
                posted_exec_orders_id.append(exec_order.get('order_id'))

@tasks.loop(minutes=1.0)
async def print_realized_pnl():
    #remove last object if the list gets too big
    if len(posted_pnl_id) > 1000:
        posted_pnl_id.pop(0)
    #get the correct channel to post into
    channel = disc_bot.get_channel(realized_pnl_channel_id)
    #create one embed for each symbol
    for i in range(len(symbols)):
        #query bybit api
        fund_records = bybit_ex.get_closed_pnl(symbol=symbols[i], start_time=int(start_time_ms))
        #check if the api returned something
        if fund_records == None:
            return
        #iterate through all returned objects
        for rel_pnl in reversed(fund_records):
            #print(rel_pnl.get('created_at'))
            #need to check for the time becuase the bybit api just returns all pnl records
            if rel_pnl.get('created_at') > (start_time.timestamp() - 3600):
                #check if we have not already posted
                if rel_pnl.get('id') not in posted_pnl_id:
                    #create the embed, post and add it to data strucute
                    pnl_embed = create_Embed.create_pnl_Embed(rel_pnl, bybit_ex)
                    await channel.send(embed=pnl_embed)
                    posted_pnl_id.append(rel_pnl.get('id'))

@tasks.loop(minutes=10.0)
async def move_time():
    #move the time window
    start_time = bybit_ex.get_timestamp()
    start_time_ms = int(float(start_time))
    #let the time overlap a bit
    start_time_ms -= 120_000
    logger.info(f"Moved time to: " + datetime.fromtimestamp(start_time_ms))

disc_bot.run(TOKEN)
