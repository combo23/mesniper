import asyncio
import anchorpy
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc import commitment, types
from solana.blockhash import Blockhash
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import AccountMeta, TransactionInstruction, Transaction, Message
from solana.system_program import create_account, CreateAccountParams
from spl.token.instructions import InitializeMintParams, MintToParams, create_associated_token_account, get_associated_token_address, initialize_mint, mint_to
import requests
from anchorpy import Program, Wallet, Provider
from base58 import b58decode, b58encode
import aiohttp
import asyncio
import warnings
import logging
from datetime import datetime
import csv
import json
from discord_webhook import *
import cloudscraper
import helheim
import base58
from helheim.exceptions import (
    HelheimException,
    HelheimSolveError,
    HelheimRuntimeError,
    HelheimSaaSError,
    HelheimSaaSBalance,
    HelheimVersion,
    HelheimAuthError,
    HelheimBifrost
)
import cloudscraper
import sys
from colorama import *
from discord_webhook import *
from importfiles import webhookinput, delay, rpc, license_key, autolist, currentversion
import os
init(autoreset=True)
#for this code you will need working tls, i use bifrost and in code there is an implementation for it
helheim.auth('HELHEIM_API_KEY')

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

helheim_path = resource_path('bifrost.dll')
class sniper:
    def __init__(self, publickey,secret, collection_name, buy_price, proxies) -> None:
        self.payer = publickey
        self.secret = secret
        self.collection_name = collection_name
        self.buy_price = buy_price
        self.proxies = proxies


    async def search(self):
        def injection(session, response):
                if helheim.isChallenge(session, response):
                    return helheim.solve(session, response)
                else:
                    return response

        session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome', 
                    'mobile': False, 
                    'platform': 'windows' 
                },
                requestPostHook=injection,

            )
        session.bifrost_clientHello = 'chrome'
        helheim.bifrost(session, helheim_path) #path to tls 
        self.proxy_ditails = self.proxies.split(":")
        self.proxy = self.proxy_ditails
        fullproxy = {
            'http': "http://" + self.proxy[2]+":"+self.proxy[3]+"@"+self.proxy[0]+":"+self.proxy[1],
            'https': "http://" + self.proxy[2]+":"+self.proxy[3]+"@"+self.proxy[0]+":"+self.proxy[1]
        }
        session.proxies = fullproxy
        def log(content):
            print('[{}] [{}] {}'.format(datetime.utcnow(), self.collection_name,content))
        log(Fore.BLUE+f"Searching for {self.collection_name} under {self.buy_price} SOL with {self.payer}")

        self.search_url = 'https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22'+ str(self.collection_name) +'%22%7D%2C%22%24sort%22%3A%7B%22takerAmount%22%3A1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A20%7D'
        while True:
            
            #self.search_url = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22" + str(self.collection_name) + "%22%2C%22takerAmount%22%3A%7B%22%24lte%22%3A" + str(float(self.buy_price)* 1e9) + "%7D%7D%2C%22%24sort%22%3A%7B%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A" + str(100) + "%7D"
            while True:
                try:
                    test = session.get(self.search_url, timeout=6)
                    break
                except:
                    log(Fore.RED+"Timeout error... retrying")
                    await asyncio.sleep(1)

            if test.status_code == 200:
                try:
                    self.response = json.loads(test.text)
                    self.lowestprice = self.response['results'][0]['price']
                    self.nftname = self.response['results'][0]['title']

                    if self.lowestprice <= float(self.buy_price):
                        log(Fore.GREEN+f"Found {self.nftname} for {self.lowestprice} SOL")
                        self.mintaddress = self.response['results'][0]['mintAddress']
                        self.seller = self.response['results'][0]['owner']
                        self.auction_house = self.response['results'][0]['v2']['auctionHouseKey']
                        self.tokenata = self.response['results'][0]['id']
                        self.sellerReferral = self.response['results'][0]['v2']['sellerReferral']
                        self.image = self.response['results'][0]['img']
                        break
                    else:
                        log(f"[Floor {self.lowestprice}]"+Fore.YELLOW+f" No nft found under {self.buy_price} SOL.. sleeping for {str(delay)}")
                        await asyncio.sleep(float(delay))
                except Exception as e:
                    log(Fore.RED+f"Failed to parse JSON")

            else:
                log(Fore.RED+"Ratelimited... sleeping for 5 seconds")
                await asyncio.sleep(5)
        while True:
            try:
                log(Fore.YELLOW+f'Proceeding to buy {self.nftname} for {self.lowestprice} SOL')
                self.mint_url = 'https://api-mainnet.magiceden.io/rpc/getNFTByMintAddress/' + str(self.mintaddress)
                self.mint_response = json.loads(session.get(self.mint_url).text)
                self.tokenaccount = self.mint_response['results']['id']
                break
            except:
                log(Fore.RED+"Failed to proccess this request...")
                await asyncio.sleep(15)
                await sniper.search(self)
        while True:
            test = {
                'authority': 'api-mainnet.magiceden.io',
                'method': 'GET',
                'scheme': 'https',
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                'if-none-match': 'W/"c32-pSwbvhnrD1N8/tkCVMGNdExnGEE"',
                'origin': 'https://magiceden.io',
                'referer': 'https://magiceden.io/',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Opera";v="85"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': "Windows",
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'
            }

            self.url = "https://api-mainnet.magiceden.io/v2/instructions/buy_now?buyer="+str(self.payer)+"&seller="+str(self.seller)+"&auctionHouseAddress="+str(self.auction_house)+"&tokenMint="+str(self.mintaddress)+"&tokenATA="+str(self.tokenata)+"&price="+str(self.lowestprice)+"&sellerReferral="+str(self.sellerReferral)+"&sellerExpiry=-1"

            while True:
                try:
                    xd = session.get(self.url, headers=test, timeout=6)
                    japierdole = json.loads(xd.text)
                    break
                except:
                    log(Fore.RED+"Timeout error... retrying")
            if xd.status_code == 200:
                break
            else:
                log(Fore.RED+f"Failed to proccess this request... [{xd.status_code}]")
                await asyncio.sleep(15)
                await sniper.search(self)
            

        while True:
            try:
                    webhook = DiscordWebhook(
                                url      = webhookinput,rate_limit_retry = True,
                                username = "j1g tools webhook")
                    embed  =  DiscordEmbed(title = ":tada: Pending purchase :tada:",
                                                                
                                color = 'fc0303',url='https://magiceden.io/item-details/'+ self.mintaddress)
                    embed.set_thumbnail(url = self.image)
                    embed.set_footer(text = f'{currentversion} | created by Combo#2137', icon_url = '')
                    embed.set_timestamp()
                    embed.add_embed_field(name = 'User wallet :', value = f'||{self.payer}||', inline = False)
                    embed.add_embed_field(name = 'Collection :',   value = f'```{str(self.collection_name)}```')
                    embed.add_embed_field(name = 'Nft name :', value = f'```{self.nftname}```')
                    embed.add_embed_field(name = 'Price :',   value = f'```{str(self.lowestprice)}```')
                    webhook.add_embed(embed)
                    response  =  webhook.execute()
            except:
                    log(Fore.RED+"Failed to proccess webhook")
            try:
                log(Fore.YELLOW+"Creating transaction...")
                self.client = AsyncClient(rpc)

                payer = Keypair.from_secret_key(b58decode(self.secret))
                t = Message.deserialize(bytes(japierdole['tx']['data']))
                p = Transaction.populate(t, [])
                p.sign(payer)
                i = Transaction.serialize(p)
                txn = await self.client.send_raw_transaction(i)
                await self.client.close()
                log(Fore.GREEN+"Submitted transaction ")
            except Exception as e:
                log(Fore.RED+f"Failed to submit transaction...")
                await self.client.close()
                await asyncio.sleep(5)
                await sniper.search(self)

            while True:
                try:
                    await asyncio.sleep(15)
                    fulltx = txn['result']
                    checkpayload = {
                                        "jsonrpc": "2.0",
                                        "id": 1,
                                        "method": "getTransaction",
                                        "params": [
                                            fulltx,
                                            "json"
                                        ]
                    }
                    test = session.post('https://explorer-api.mainnet-beta.solana.com/', json=checkpayload)
                    if json.loads(test.text)['result']['meta']['err'] == None:
                        log(Fore.GREEN+"Sniped NFT")
                        webhook = DiscordWebhook(
                                    url      = webhookinput,rate_limit_retry = True,
                                    username = "j1g tools webhook")
                        embed  =  DiscordEmbed(title = ":tada: Succesfully sniped :tada:",
                                                                    
                                    color = 'fc0303',url='https://magiceden.io/item-details/'+ self.mintaddress)
                        embed.set_thumbnail(url = self.image)
                        embed.set_footer(text = f'{currentversion} | created by Combo#2137', icon_url = '')
                        embed.set_timestamp()
                        embed.add_embed_field(name = 'User wallet :', value = f'||{self.payer}||', inline = False)
                        embed.add_embed_field(name = 'Collection :',   value = f'```{str(self.collection_name)}```')
                        embed.add_embed_field(name = 'Nft name :', value = f'```{self.nftname}```')
                        embed.add_embed_field(name = 'Price :',   value = f'```{str(self.lowestprice)}```')
                        webhook.add_embed(embed)
                        response  =  webhook.execute()
                        break
                    else:
                        log(Fore.RED+"Transaction Failed...")
                except:
                    log(Fore.RED+"Failed to check transaction")
                    await asyncio.sleep(15)
                    await sniper.search(self)
            if autolist == "True":

                while True:
                    
                    while True:
                        try:
                            self.floorcheck = session.get(self.search_url, timeout=6)
                            
                        except:
                            log(Fore.RED+"Timeout error... retrying")
                            await asyncio.sleep(5)

                        if self.floorcheck.status_code == 200:
                            try:
                                self.ee = json.loads(self.floorcheck.text)
                                self.floor = self.ee['results'][0]['price']
                                self.listurl = f'https://api-mainnet.magiceden.io/v2/instructions/sell?seller={str(self.payer)}&auctionHouseAddress={str(self.auction_house)}&tokenMint={str(self.mintaddress)}&tokenAccount={str(self.tokenaccount)}&price={str(self.floor)}&expiry=-1'
                                break
                            except:
                                log(Fore.RED+"Failed to get floor price")
                    while True:
                        try:
                            test = {
                                'authority': 'api-mainnet.magiceden.io',
                                'method': 'GET',
                                'scheme': 'https',
                                'accept': 'application/json, text/plain, */*',
                                'accept-encoding': 'gzip, deflate, br',
                                'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
                                'if-none-match': 'W/"c32-pSwbvhnrD1N8/tkCVMGNdExnGEE"',
                                'origin': 'https://magiceden.io',
                                'referer': 'https://magiceden.io/',
                                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Opera";v="85"',
                                'sec-ch-ua-mobile': '?0',
                                'sec-ch-ua-platform': "Windows",
                                'sec-fetch-dest': 'empty',
                                'sec-fetch-mode': 'cors',
                                'sec-fetch-site': 'same-site',
                                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.47'
                            }
                            self.chujens = session.get(self.listurl, timeout=6, headers=test)

                            self.listinstructions = json.loads(self.chujens.text)['tx']['data']
                            log(self.listinstructions)
                            break
                        except:
                            log(Fore.RED+"Failed to get list instructions")
                            log(self.chujens.text)
                    while True:
                        try:
                            log(Fore.YELLOW+"Creating list transaction...")
                            self.client = AsyncClient(rpc)

                            
                            payer = Keypair.from_secret_key(b58decode(self.secret))
                            t = Message.deserialize(bytes(self.listinstructions))
                            p = Transaction.populate(t, [])
                            p.sign(payer)
                            i = Transaction.serialize(p)
                            nowytx = await self.client.send_raw_transaction(i)

                            await self.client.close()
                            log(Fore.GREEN+"Submitted list transaction ")
                            break
                        except Exception as e:
                            log(Fore.RED+f"Failed to list submit transaction...")
                            log(e)
                            await self.client.close()
                            await asyncio.sleep(5)
                    while True:
                        try:
                            await asyncio.sleep(15)
                            fulllisttx = nowytx['result']
                            checkpayload = {
                                                "jsonrpc": "2.0",
                                                "id": 1,
                                                "method": "getTransaction",
                                                "params": [
                                                    fulllisttx,
                                                    "json"
                                                ]
                            }
                            test = session.post('https://explorer-api.mainnet-beta.solana.com/', json=checkpayload)
                            if json.loads(test.text)['result']['meta']['err'] == None:
                                log(Fore.GREEN+"Listed nft for floor price")
                                webhook = DiscordWebhook(
                                            url      = webhookinput,rate_limit_retry = True,
                                            username = "j1g tools webhook")
                                embed  =  DiscordEmbed(title = ":tada: Succesfully listed for floor price :tada:",
                                                                            
                                            color = 'fc0303',url='https://magiceden.io/item-details/'+ self.mintaddress)
                                embed.set_thumbnail(url = self.image)
                                embed.set_footer(text = f'j1g mint 0.0.1 | created by Combo#2137', icon_url = '')
                                embed.set_timestamp()
                                embed.add_embed_field(name = 'User wallet :', value = f'||{self.payer}||', inline = False)
                                embed.add_embed_field(name = 'Collection :',   value = f'```{str(self.collection_name)}```')
                                embed.add_embed_field(name = 'Nft name :', value = f'```{self.nftname}```')
                                embed.add_embed_field(name = 'Price :',   value = f'```{str(self.lowestprice)}```')
                                webhook.add_embed(embed)
                                response  =  webhook.execute()
                                log(Fore.GREEN+"Listed nft for floor price")
                                await asyncio.sleep(15)
                                await sniper.search(self)
                                
                            else:
                                log(Fore.RED+"List Transaction Failed...")
                        except:
                            log(Fore.RED+"Failed to check transaction")
                            await asyncio.sleep(15)

            
            await asyncio.sleep(15)
            await sniper.search(self)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
logging.getLogger('asyncio').setLevel(logging.CRITICAL)
