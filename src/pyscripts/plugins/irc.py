#!/usr/bin/env python

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, task, defer

from hyperserv.events import eventHandler, triggerServerEvent

from hypershade.config import config
from hypershade.cubescript import checkforCS

from hypershade.usersession import UserSessionManager
from hypershade.util import formatCaller

class IrcBot(irc.IRCClient):
	def connectionMade(self):
		self.nickname = self.factory.nickname
		irc.IRCClient.connectionMade(self)
		self.joined_channels = []
	def signedOn(self):
		for channel in self.factory.channels:
			self.join(channel)
		self.factory.signedOn(self)
	def connectionLost(self, reason):
		self.factory.signedOut(self)
	def joined(self, channel):
		if channel not in self.joined_channels:
			self.joined_channels.append(channel)
	def left(self, channel):
		if channel in self.joined_channels:
			self.joined_channels.remove(channel)
	def broadcast(self, message):
		for channel in self.joined_channels:
			self.say(channel, message)
	def privmsg(self, user, channel, msg):
		user = user.split('!', 1)[0]
		if channel == self.nickname:
			if checkforCS(("irc",user),msg)==0:
				msg="@"+msg
				checkforCS(("irc",user),msg)
		else:
			if(checkforCS(("irc",user),msg)==0):
				triggerServerEvent("user_communication",[("irc",user),msg])
	def alterCollidedNick(self, nickname):
		return nickname + '_'
	
	def userJoined(self, user, channel):
		UserSessionManager.create(("irc",user))
	def userLeft(self, user, channel):
		UserSessionManager.destroy(("irc",user))
	def userQuit(self, user, quitMessage):
		UserSessionManager.destroy(("irc",user))
	def userKicked(self, kickee, channel, kicker, message):
		UserSessionManager.destroy(("irc",kickee))
	def userRenamed(self, oldname, newname):
		UserSessionManager.rename(("irc",oldname),("irc",newname))

class IrcBotFactory(protocol.ClientFactory):
	protocol = IrcBot
	def __init__(self, nickname, channels):
		self.nickname = nickname
		self.channels = channels
		self.bots = []
		self.reconnect_count = 0
	def doConnect(self):
		reactor.connectTCP(config['ircserver'], 6667, factory)
	def doReconnect(self):
		if self.reconnect_count < 5:
			self.reconnect_count += 1
			self.doConnect()
	def signedOn(self, bot):
		if bot not in self.bots:
			self.bots.append(bot)
	def signedOut(self, bot):
		if bot in self.bots:
			self.bots.remove(bot)
			addTimer(5000, self.doReconnect, ())
	def broadcast(self, message):
		for bot in self.bots:
			bot.broadcast(message)
	def notice(self, nick, message):
		for bot in self.bots:
			bot.notice(nick,message)

# create factory protocol and application
factory = IrcBotFactory(config['ircnick'], [config['ircchannel']])
factory.doConnect()

@eventHandler('echo')
def ircecho(caller,msg):
	if caller[0]=="irc":
		factory.notice(caller[1],msg)

@eventHandler('say')
def sayirc(msg):
	factory.broadcast(msg)

@eventHandler('user_communication')
def usercommunicationirc(caller,msg):
	if caller[0]=="irc":
		return
	factory.broadcast("<"+formatCaller(caller)+"> "+msg)
	
@eventHandler('notice')
def noticeirc(msg):
	factory.broadcast(msg)