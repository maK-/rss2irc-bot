#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import socket, string, feedparser, os
from threading import Timer

#feed_list is a list of all of the rss feeds.
feed_list = ["http://api.twitter.com/1/statuses/user_timeline.rss?screen_name=CiaranmaK"]
feed_data = []
feed_hasbeen = []
configured = False


#menu && bot configuration.
def head():
	header = "____________________________________\n"+" ____  ____ ____    ____   ___ _____\n"+"|  _ \/ ___/ ___|  | __ ) / _ \_   _|\n"+"| |_) \___ \___ \  |  _ \| | | || |\n"+"|  _ < ___) |__) | | |_) | |_| || |\n"+"|_| \_\____/____/  |____/ \___/ |_|\n"+"____________________________________\n"+"_________By_Ciaran_McNally__________\n"
	print header

head()
while(not configured):
	setting = str(raw_input('Do you want to use default redbrick settings? (y/n) : '))
	#Run redbrick config.	
	if setting=='Y' or setting=='y' or setting=='yes' or setting=='YES':
		configured = True
		net = 'irc.redbrick.dcu.ie'
		port = 6667
		nick = str(raw_input('Bots nick? (8 characters or under): '))
		channel = str(raw_input('Channel? (#name): '))
		if channel[0] != '#':
			channel = '#'+channel
		ident = str(raw_input('Bot ident/owner? (your nick): '))
	
	#Run other config.
	elif setting=='N' or setting=='n' or setting=='no' or setting=='NO':
		configured = True
		net = str(raw_input('Irc network?: '))
		port = int(raw_input('Irc port? (default=6667): '))
		nick = str(raw_input('Bots nick? (8 characters or under): '))
		channel = str(raw_input('Channel? (#name): '))
		if channel[0] != '#':
			channel = '#'+channel
		ident = str(raw_input('Bot ident/owner? (your nick): '))
	else:
		configured = False


readbuffer = ''
#connect the bot.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((net,port))
s.send('USER '+ident+' '+net+' bla : '+ident+'\r\n')
s.send('NICK '+nick+'\r\n')
s.send('JOIN '+channel+'\r\n')
print s.recv(4096)

#send a message to a channel
def msg(channel, msg):
	s.send('PRIVMSG '+str(channel)+' :'+str(msg)+'\r\n')

#append all the latest feeds
def feed_refresh():
	first_time = False
	if len(feed_data) == 0:
		first_time = True
 	for feed in feed_list:
  		f = feedparser.parse(feed)
  		for entry in f.entries:
			m = entry.title.encode('utf-8')+ " | "+"16"+entry.link.encode('utf-8')
			if m in feed_data:
				pass
			else:
				feed_data.append(m)
				if(first_time == False):
					msg(channel, m)
				
#display n latest feeds from feedlist
def last_feed(n):
	try:
		if n > 4:
			n = 4
	except TypeError:
		return 0
	for feed in feed_list:
		f = feedparser.parse(feed)
		for x in range(0,n):
			m = f.entries[x].title.encode('utf-8')+" | "+"16"+f.entries[x].link.encode('utf-8')
			msg(channel, m)
		
def show_feeds():
    for feed in feed_list:
        msg(channel,feed)

#check for feed update every 15 mins.
def update():
    try:
        x = Timer(900.0, update)
        x.daemon=True
        x.start()
        feed_refresh()
    except (KeyboardInterrupt, SystemExit):
        x.cancel()


#Fill feeds.
feed_refresh()
update()

#read channel data
while(True):
    readbuffer=readbuffer+s.recv(4096)
    temp=string.split(readbuffer, "\n")
    readbuffer=temp.pop()
    for line in temp:
        line=string.rstrip(line)
        line=string.split(line)

#--Channel commands--
	if(line[0]=='PING'):
		s.send('PONG '+line[1]+'\r\n')

	if(len(line)==4)and(line[2]==channel)and(line[3]==':!help'):
		msg(channel,'1,7☠ -RSS-Commands- ☠ ')
		msg(channel, '5!feed [add|remove|list]16 - add/remove/list items in feed list.')
		msg(channel, '5!feed 16- for new entries.')
		msg(channel,'5!feed last [int]16 - for [int] last entries for each feed.')

	if(len(line)==4)and(line[2]==channel)and(line[3]==':!feed'):
		feed_refresh()
	
	if(len(line)==6)and(line[2]==channel)and(line[3]==':!feed')and(line[4]=='last'):
		last_feed(int(line[5]))

	if(len(line)==6)and(line[2]==channel)and(line[3]==':!feed')and(line[4]=='add'):
		if 'http://' in line[5] or 'https://' in line[5]:
                    msg(channel, '3Feed Added!')
                    feed_list.append(line[5])
                    feed_data = []
                    feed_refresh()
                else:
			msg(channel, '5Feed Rejected!')
	
    if(len(line)==5)and(line[2]==channel)and(line[3]==':!feed')and(line[4]=='remove'):
		feed_list.pop()
		msg(channel, '5Removed!')

    if(len(line)==5)and(line[2]==channel)and(line[3]==':!feed')and(line[4]=='list'):
        show_feeds()


