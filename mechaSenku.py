# Imports
import os
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
import re
from jikanpy import Jikan
from bs4 import BeautifulSoup
import urllib
import json
import requests
import asyncio
from PIL import Image

# Intents and Bot command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

# Load keys from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
covidkey = os.getenv('COVIDKEY')
tenorkey = os.getenv('TENORKEY')

# limit on the amount of content retrieved using Tenor GIF API
lmt = 5

# Powered by CoinGecko API
cg = CoinGeckoAPI()

#Powered by Jikan Unofficial MAL Anime API
jikan = Jikan()

# global variable
dad_response = False

# Greetings 
greetings = [ 'Hi ', 'Hi there ', 'Hello ', 'Hey ', 'Hey there ', ] 

# 8-ball responses
possible_responses = [ 'That is a resounding no', 'It is not looking likely', 'Too hard to tell', 'It is quite possible', 'Definitely', ] 

# Simple welcome message
@bot.command(pass_context=True, brief='Greeting message')
async def hello(ctx):
    msg = 'Hello {0.mention}. How can Mecha Senku assist you today?'.format(ctx.message.author)
    await ctx.send(msg)

# Dice roll
@bot.command(pass_context=True, brief='Roll a dice')
async def dice(ctx):
    dice = random.randint(1, 6)
    filename = "dice " + str(dice) + ".png"
    dicename = os.path.join('dice', filename)
    await ctx.send('You rolled ' + str(dice), file=discord.File(dicename))

# Coin flip
@bot.command(pass_context=True, brief='Flip a coin')
async def coin(ctx):
    coin = random.randint(1,2)
    filename = numbers_to_side(coin) + ".jpg"
    coinname = os.path.join('coin', filename)
    await ctx.send('You got ' + numbers_to_side(coin), file=discord.File(coinname))

# Eight ball
@bot.command(pass_context=True, aliases=['8ball'], brief='Asks your question to an 8ball')
async def eight_ball(ctx):
    if ('win' in ctx.message.content) and ('lottery' in ctx.message.content):
        await ctx.send('Statistically, the odds of winning are about 1 in 175 million so I would say no.')
    else:
        await ctx.send(random.choice(possible_responses))

# Random Number
@bot.command(pass_context=True, brief='Returns a random number from a selected range')
async def pick(ctx):
    num_range = ctx.message.content.split()
    min_val = int(num_range[1])
    max_val = int(num_range[2])
    await ctx.send(random.randint(min_val, max_val))

# Cryptocurrency price
@bot.command(pass_context=True, brief='Checks the price of cryptocurrency')
async def price(ctx):
    message_list = ctx.message.content.split()
    crypto = message_list[message_list.index('!price') + 1]
    result = str(cg.get_price(ids=crypto, vs_currencies='usd'))
    price =  re.findall(r"\d+\.\d{1,2}", result)
    await ctx.send(crypto +" price is: $" + price[0])

# Function to convert number into coin side 
def numbers_to_side(argument): 
    switcher = { 1: "heads", 2: "tails", } 
    return switcher.get(argument, "nothing") 

# Memes
@bot.command(pass_context=True, brief='Gets you a meme template')
async def memetemplate(ctx):
    link = 'https://api.imgflip.com/get_memes'
    f = urllib.request.Request(link, headers={'User-agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(f)
    data = resp.read().decode()
    loaded_data = json.loads(data)
    memeSize = len(loaded_data['data']['memes']) - 1
    randNum = random.randint(0,memeSize)
    meme_name = loaded_data['data']['memes'][randNum]['name']
    meme_image = loaded_data['data']['memes'][randNum]['url']
    embed = discord.Embed(title=meme_name, value=str(meme_name), inline=False)
    embed.set_image(url=meme_image)
    await ctx.send(embed=embed)

# Dad jokes
@bot.command(pass_context=True, brief='Send you dad jokes')
async def dadjoke(ctx):
    link = 'https://icanhazdadjoke.com/'
    f = urllib.request.Request(link, headers={'User-agent': 'Our Bot(https://github.com/gbessrour/project-stone)',"Accept":"application/json"})
    resp = urllib.request.urlopen(f)
    data = resp.read().decode()
    loaded_data = json.loads(data)
    joke = loaded_data['joke']
    await ctx.send(joke)

# PubSubs on sale or not
@bot.command(pass_context=True, brief='Checks if pubsubs are on sale or not')
async def pubsub(ctx):
    req = urllib.request.Request('http://arepublixchickentendersubsonsale.com')
    resp = urllib.request.urlopen(req)
    respData = str(resp.read())
    if ('<!-- onsale:no -->') in respData:
        answer = "Pub subs are NOT on sale :("
        await ctx.send(file=discord.File(os.path.join('Reacts', 'sad_deku.gif')))
    elif('<!-- onsale:yes -->') in respData:
        answer = "Pub subs ARE on sale my dudes!!!"
        await ctx.send(file=discord.File(os.path.join('Reacts', 'excited_deku.gif')))
    await ctx.send(answer)

# Urban Dictionary
@bot.command(pass_context=True, brief='Gets you Urban Dictionary definitions', description='Gets you Urban Dictionary definitions so you can keep up with kids these days')
async def urban(ctx):
    url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
    userInput = ctx.message.content.split()
    word = userInput[1]
    querystring = {"term":word}
    headers = {
    'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
    'x-rapidapi-key': "5f0790a371mshbde9da487ddc1fdp19ca7cjsn3d32a8881f9b"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.content)
    definition = data['list'][0]['definition']
    await ctx.send(definition)

# Some replies to messages such as dad jokes and jojo references
@bot.event
async def on_message(message):
    global dad_response
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return
    # Dad Jokes
    elif (message.content.startswith('I\'m ')) or (message.content.startswith('I am ') or (message.content.startswith('Im '))):
        if message.content.startswith('I\'m '):
            dadjoke = message.content.replace('I\'m ', '')
        elif message.content.startswith('I am '):
            dadjoke = message.content.replace('I am ', '')
        elif message.content.startswith('Im '):
            dadjoke = message.content.replace('Im ', '')
        msg = random.choice(greetings) + dadjoke + '. I\'m dad!'
        await message.channel.send(msg)

        dad_response = True
        
    # Confusion message
    elif message.content.lower() == 'what' or message.content.lower() == 'wot' or message.content.lower() == 'wat' or message.content.lower() =='nani':
        if message.content.lower() =='nani':
            rando = random.randint(0,1)
            await message.channel.send(file=discord.File(os.path.join('Reacts', 'nani'+str(rando)+'.gif')))
        else:
            await message.channel.send(message.content)

    # Dad joke response
    elif dad_response == True and message.author != bot.user:
        if 'fuck' in message.content.lower() or 'no ' in message.content.lower() or message.content.lower() == 'no':
            await message.channel.send('no u')
        elif 'thank' in message.content.lower():
            await message.channel.send('You\'re welcome, ' + message.author.display_name)
        dad_response = False

    # JoJo Reference?
    # if 'jojo' in message.content.lower() or 'jojo\'s' in message.content.lower() or 'jojos' in message.content.lower() or 'stand' in message.content.lower():
    for words in ['jojo', 'jojo\'s', 'jojos', 'stand']:
        if re.search(r'\b' + words + r'\b', message.content.lower()) and  message.author.id == 386230029169852419:
            await message.channel.send('Was that a motherfucking JoJo\'s reference??')
            await message.channel.send('btw Ghassen, you should watch JoJo\'s')
            
    if ('You thought' in message.content) and ('but' in message.content):
        await message.channel.send(file=discord.File(os.path.join('Reacts', 'dio.gif')))
    

    if message.content.lower() =='lewd':
        rando = random.randint(0,1)
        await message.channel.send(file=discord.File(os.path.join('Reacts', 'lewd'+str(rando)+'.gif')))

    await bot.process_commands(message)

# Returns the current exchange rate of currencies
@bot.command(pass_context=True, brief='Returns the current exchange rate of currencies')
async def currency(ctx):
    currency_list = ctx.message.content.split()
    amount = currency_list[1]
    base = currency_list[2].upper()
    target = currency_list[3].upper()
    list_url = "https://currency13.p.rapidapi.com/list"
    url = "https://currency13.p.rapidapi.com/convert/"+amount+"/"+base+"/"+target

    headers = {
        'x-rapidapi-host': "currency13.p.rapidapi.com",
        'x-rapidapi-key': "6d91c9f439msh87c30494f5265adp18e8a7jsn6496e29a419a"
        }

    response = requests.request("GET", url, headers=headers)
    list_response = requests.request("GET", list_url, headers=headers)
    data = json.loads(response.content)
    data_list = json.loads(list_response.content)

    for i in range(0, len(data_list["currencies"])):
        if base == data_list["currencies"][i]["code"]:
            baseName = data_list["currencies"][i]["name"]
            baseSymbol = data_list["currencies"][i]["symbol"]

        if target == data_list["currencies"][i]["code"]:
            targetName = data_list["currencies"][i]["name"]
            targetSymbol = data_list["currencies"][i]["symbol"]

    result = data['amount']
    price =  str(round(result,2))
    await ctx.send(baseSymbol+""+amount+" "+base+"("+baseName+") is equivalent to "+targetSymbol+price+" "+target+"("+targetName+")")

# Returns the current Covid-19 numbers
@bot.command(pass_context=True)
async def covid(ctx):

    covid_list = ctx.message.content.split()
    country = covid_list[1:]
    countryStr = " ".join(country)
   
    url = "https://covid-19-data.p.rapidapi.com/country"

    querystring = {"format":"json","name":str(countryStr)}

    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': covidkey
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.content)
    
    countries = data[0]["country"]
    confirmed = data[0]["confirmed"]
    recovered = data[0]["recovered"]
    critical = data[0]["critical"]
    deaths = data[0]["deaths"]
    embed = discord.Embed(title=countries, value=str(countries), inline=False)
    embed.add_field(name="Confirmed Cases", value=confirmed, inline=False)
    embed.add_field(name="Recovered", value=recovered, inline=False)
    embed.add_field(name="Critical Cases", value=critical, inline=False)
    embed.add_field(name="Deaths", value=deaths, inline=False)
    await ctx.send(embed=embed)

# Gets you the gif you want
@bot.command(pass_context=True, brief='Gets you the gif you want')
async def gif(ctx):
    
    global tenorkey
    global lmt

    message_list = ctx.message.content.split()
    
    search_term = message_list[1:]
        
    # get the top 8 GIFs for the search term
    r = requests.get("https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, tenorkey, lmt))

    if r.status_code == 200:
    # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)
        gifArraySize = len( top_gifs['results']) - 1
        randNum = random.randint(0,gifArraySize)

        randomGif = top_gifs['results'][randNum]['media'][0]['gif']['url']
        await ctx.send(randomGif)
    else:
        top_gifs = None

# Facts about numbers like the nerd you are
@bot.command(pass_context=True, brief='Gives you fun number facts', description='The number facts this command gives you can be either trivia, date, year, or math. All you need to do is call !numberfacts [factType] [number]')
async def numberfacts(ctx):
    message_list = ctx.message.content.split()
    factType = message_list[1]
    search_number = message_list[2]

    url = "https://numbersapi.p.rapidapi.com/"+search_number+"/"+factType

    querystring = {"fragment":"true","notfound":"floor","json":"true"}

    headers = {
        'x-rapidapi-host': "numbersapi.p.rapidapi.com",
        'x-rapidapi-key': "6d91c9f439msh87c30494f5265adp18e8a7jsn6496e29a419a"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.content)
    if factType == 'year':
        randomFact = "In "+ search_number + ", " + data['text']
    elif factType == 'date':
        randomFact = "In " + search_number + "/"+ str(data['year']) +", " + data['text']
    else:
        randomFact = search_number + " is " + data['text']
    await ctx.send(randomFact)

# Anime search
@bot.command(pass_context=True, brief='Does anime queries for you', description='If you call !anime name [anime_name], it will return all the info about that anime.\nIf you call !anime season [season] [optional # of anime], it will return the specified number of anime from that season.')
async def anime(ctx):
    anime_list = ctx.message.content.split()
    param = anime_list[anime_list.index('!anime') + 1]
    second_param = str(anime_list[2:])

    if(param == 'name'):
        anime = jikan.search(search_type= 'anime', query= second_param)
        data = json.dumps(anime)
        loaded_data = json.loads(data)
        anime_title = loaded_data['results'][0]['title']
        year_released = str(loaded_data['results'][0]['start_date'])
        synopsis = loaded_data['results'][0]['synopsis']            
        url = loaded_data['results'][0]['url']
        image_result = loaded_data['results'][0]['image_url']
        episodes = loaded_data['results'][0]['episodes']
        score = loaded_data['results'][0]['score']
        embed = discord.Embed(title=str(anime_title), value=str(anime_title), inline=False)
        embed.add_field(name="Score", value=score, inline=False)
        embed.add_field(name="Synopsis", value=synopsis, inline=False)
        embed.add_field(name="Number of Episodes", value=episodes, inline=False)
        embed.add_field(name="Year Released", value=year_released[0:4], inline=False)
        embed.set_image(url=image_result)
        embed.add_field(name="URL", value=url, inline=False)
        await ctx.send(embed=embed)
    elif(param == 'season'):
        second_param = anime_list[anime_list.index('!anime') + 2] 
        third_param = anime_list[anime_list.index('!anime') + 3] 
        #Little comment explaining that this try-except handles an IndexOutOfBoundsException
        try:
            fourth_param = anime_list[anime_list.index('!anime') + 4]
        except:
            fourth_param = 5

        result = jikan.season(year= int(third_param), season= second_param)
        data = json.dumps(result)
        loaded_data = json.loads(data)
        
        for i in range(0,int(fourth_param)):
            randNum = random.randint(0,(len(loaded_data["anime"])-1))

            #Skip showing animes that are continuing when asking about a specific season  
            if loaded_data["anime"][randNum]["continuing"]:
                continue 

            anime_title = loaded_data["anime"][randNum]["title"]
            url = loaded_data['anime'][randNum]['url']

            embed = discord.Embed(title=anime_title, value=second_param +" "+ str(third_param), inline=False)
            
            for j in range(0,len(loaded_data["anime"][randNum]["genres"])):
                embed.add_field(name="Genre", value= loaded_data["anime"][randNum]["genres"][j]["name"], inline=True)            
           
            embed.add_field(name="MyAnimeList URL",value=url, inline=False)
            await ctx.send(embed=embed)

# Manga search
@bot.command(pass_context=True, brief='Does manga queries for you')
async def manga(ctx):
    manga_list = ctx.message.content.split()
    param = manga_list[manga_list.index('!manga') + 1] 
    second_param = str(manga_list[2:])

    if(param == 'name'):
        manga = jikan.search(search_type= 'manga', query= second_param)
        
        data = json.dumps(manga)
        loaded_data = json.loads(data)
        manga_title = loaded_data['results'][0]['title']
        year_released = str(loaded_data['results'][0]['start_date'])
        synopsis = loaded_data['results'][0]['synopsis']            
        url = loaded_data['results'][0]['url']
        image_result = loaded_data['results'][0]['image_url']
        score = loaded_data['results'][0]['score']
        volumes = loaded_data['results'][0]['volumes']
        chapters = loaded_data['results'][0]['chapters']
        publishing = loaded_data['results'][0]['publishing']

        embed = discord.Embed(title=str(manga_title), value=str(manga_title), inline=False)
        embed.add_field(name="Score", value=score, inline=True)
        if publishing:
            embed.add_field(name="Status", value="Publishing", inline=True)
        else:
            embed.add_field(name="Number of Volumes", value=volumes, inline=True)
            embed.add_field(name="Number of Chapters", value=chapters, inline=True)
            embed.add_field(name="Status", value="Finished", inline=True)
        embed.add_field(name="Year Released", value=year_released[0:4], inline=True)
        embed.add_field(name="Synopsis", value=synopsis, inline=False)
        embed.set_image(url=image_result)
        embed.add_field(name="URL", value=url, inline=False)
        await ctx.send(embed=embed)

# Prints when the bot is ready
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run(TOKEN)