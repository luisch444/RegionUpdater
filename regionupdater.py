from mcdreforged.api.all import *
import os, os.path
from shutil import copy
import configparser
from threading import Thread
import schedule
import time

PLUGIN_METADATA = {
    'id': 'regionupdater',
    'version': '1.0.0',
    'name': 'RegionUpdater',
    'description': 'This plugin copy any other world into the server(regions) every day but you can except regions',
    'author': 'luisch444',
    'link': 'https://github.com',
    'dependencies': {}
}

config = configparser.ConfigParser()

restime = "04:00"

def writeconfig(file):
  with open(file, 'w') as configfile:
    config.write(configfile)

def copyworld():
    loadconfig()
    serv.say(kickmsg)
    time.sleep(10)
    serv.logger.info('closing server...')
    serv.stop()
    time.sleep(20)
    serv.logger.info("starting copy")
    #overworld
    ov = copiedserverpath+"/region/"
    ov2 = serverpath+"/region/"
    for region in os.listdir(ov):
        if not region in saveregionsov:
            os.remove(ov2+region)
            copy(ov+region, ov2)
    serv.logger.info("overworld finished")

    #end
    en = copiedserverpath+"/DIM1/region/"
    en2 = serverpath+"/DIM1/region/"
    for region in os.listdir(en):
        if not region in saveregionsen:
            os.remove(en2+region)
            copy(en+region, en2)
    serv.logger.info("end finished")

    #nether
    nt = copiedserverpath+"/DIM-1/region/"
    nt2 = serverpath+"/DIM-1/region/"
    for region in os.listdir(nt):
        if not region in saveregionsnt:
            os.remove(nt2+region)
            copy(nt+region, nt2)
    serv.logger.info("nether finished")
    serv.start()
    return

schedule.every().day.at(restime).do(copyworld)

@new_thread
def timer():
    while True:
        schedule.run_pending()
        time.sleep(60)

def loadconfig():
    config.read('CopyWorld.ini')
    global restime
    if not config["config"]['copyhour']=="":
        restime = config['config']['copyhour']
    if config['config']['serverpath']=="":
        return False
    global serverpath
    serverpath = config['config']['serverpath']
    if config['config']['copiedserverpath']=="":
        return False
    global copiedserverpath
    copiedserverpath = config['config']['copiedserverpath']

    global saveregionsov
    saveregionsov = config['plugin']['saveregionsov'].split("/")
    global saveregionsen
    saveregionsen = config['plugin']['saveregionsen'].split("/")
    global saveregionsnt
    saveregionsnt = config['plugin']['saveregionsnt'].split("/")

    global kickmsg
    kickmsg = config['config']['kickmsg']

    print(copiedserverpath+"/region/")



def saveregion(region, dimmension):
    loadconfig()
    if dimmension=='ov' or dimmension=='overworld':
        config["plugin"]["saveregionsov"]+= "/"+region
    elif dimmension=='en' or dimmension=='end':
        config["plugin"]["saveregionsen"]+= "/"+region
    elif dimmension=='nt' or dimmension=='nether':
        config["plugin"]["saveregionsnt"]+= "/"+region
    writeconfig('CopyWorld.ini')
    return

def removeregion(region, dimmension):
    loadconfig()
    if dimmension=='ov' or dimmension=='overworld':
        ls = config['plugin']["saveregionsov"].split("/")
        ls.remove(region)
        config['plugin']["saveregionsov"] = ""
        for i in ls:
            config['plugin']["saveregionsov"]+= i
    elif dimmension=='en' or dimmension=='end':
        ls = config['plugin']["saveregionsen"].split("/")
        ls.remove(region)
        config['plugin']["saveregionsen"] = ""
        for i in ls:
            config['plugin']["saveregionsen"]+= i
    elif dimmension=='nt' or dimmension=='nether':
        ls = config['plugin']["saveregionsnt"].split("/")
        ls.remove(region)
        config['plugin']["saveregionsnt"] = ""
        for i in ls:
            config['plugin']["saveregionsnt"]+= i
    writeconfig('CopyWorld.ini')
    return


def listregions(source: CommandSource):
    loadconfig()
    msg = ""
    ls = config['plugin']["saveregionsov"].split("/")
    msg+="Overworld: "+str(ls)+"\n"
    lsnt = config['plugin']["saveregionsnt"].split("/")
    msg+="Nether: "+str(lsnt)+"\n"
    lsen = config['plugin']["saveregionsen"].split("/")
    msg+="End: "+str(lsen)+"\n"
    source.reply(msg)
    return

def commandhelp(source: CommandSource):
    msg = "regionupdater, this plugin of mcdr copy every day a server world to other.\nUse:\n!!region save region-name dimmension --- this will stop for copy that mc region, to check your regions you can use https://dinnerbone.com/minecraft/tools/coordinates/ \n!!region delete region-name dimmension --- this will start again to copy in that region\n"
    source.reply(msg)
    return

def commandcopy(source: CommandSource):
    msg = "copy now the server"
    source.reply(msg)
    return

def on_load(server, old):
    global serv
    serv = server

    server.register_command(Literal('!!region').runs(commandhelp)
    .then(Literal("save").then(Text("region").then(Text("dimmension")
    .runs(lambda src, ctx: saveregion(ctx["region"], ctx["dimmension"]))
    )
        )
            )
    .then(Literal("remove").then(Text("region").then(Text("dimmension")
    .runs(lambda src, ctx: removeregion(ctx["region"], ctx["dimmension"]))
    )
        )
            )
    .then(Literal("list").runs(listregions))
    )

    server.register_command(Literal('!!copynow').runs(copyworld))

    timer()
    server.logger.info('Timer initialiced!')