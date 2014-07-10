# -*- coding: utf-8 -*-
# Copyright 2012 Sebastian Alvarez <sebastianmalvarez@gmail.com>
# License: GPL v3
# For further info, see LICENSE file

import re
import unicodedata

from random import choice

from lalita import Plugin

class Bardator(Plugin):

	def init(self, config):
		self.users = dict()
		self.register(self.events.COMMAND, self.bard, ['bard'])
		self.register(self.events.PRIVATE_MESSAGE, self.private_bard)
		self.bards = [
			u"muchachooo hay que tener cuidadín",
			u"VIRGEN!",
			u"que ágil",
			u"que tipo de mierda",
			u"me hacés mierda...",
			u"go home, you are drunk",
		]
		self.specific_bards = {
			u"UG": u"ULTRA GAAAY! http://i2.kym-cdn.com/entries/icons/original/000/008/910/ultra-gay.png",
			u"GXL": u"GAY XL! https://i.cloudup.com/NIgrcHEvG6.png",
			u"G": u"GAAAAAAY http://media.tumblr.com/tumblr_m9g64idfjp1qbnggp.jpg",
			u"UN": u"ULTRA NEEEERD http://cdn.memegenerator.net/instances/400x/23940800.jpg",
			u"AHH": u"AHHHHHHHHHHHHHHHHHHHHHHHHHHHH!!!! http://bit.ly/PJpxN4",
			u"E": u"Entendiiiido http://www.youtube.com/watch?v=3R92ArVZhc4&feature=youtu.be",
			u"D": u"http://www.youtube.com/watch?v=a1Y73sPHKxw",
			u"LC": u"LCDTMAB!!! https://fbcdn-sphotos-h-a.akamaihd.net/hphotos-ak-ash4/306428_10151129068200792_1317690822_n.jpg",
			u"LP": u"LA HAS LIADO PARDA!! http://www.youtube.com/watch?v=ICQrvG6jfOA",
			u"BUE": u"¯\_(ツ)_/¯",
			u"TWS": u"TWSS!!!!",
			u"ECFD": u"http://imgur.com/BjcW8!!!!",
			u"V": u"VIRGEEEEEEN!!! http://www.virginmedia.com/images/40-Year-Old-Virgin-poster-590x350.jpg",
			u"LTA": u"LA TENÉS ADENTRO! http://www.memegenerator.es/imagenes/memes/0/1185384.jpg",
			u"burn": u"BUUURN! http://d22zlbw5ff7yk5.cloudfront.net/images/cm-21462-150526c45f3346.jpeg",
			u"FU": u"OH MY, YOU'RE ALL FUC*ED UP!!! http://i.imgur.com/RW5SZ97.gif"
		}

	def bard(self, user, channel, command, *args):
		if len(args) > 1:
			user = args[0]
			if len(args) == 2:
				# @bard olapic jorgemudry AHH
				command = args[1]
				self.param_bard(channel, user, command)
			else:
				# @bard olapic jorgemudry
				self.random_bard(channel, user)
		else:
			for user in args:
				self.random_bard(channel, user)
	
	def random_bard(self, channel, user):
		bard = choice(self.bards)
		self.say(channel, u"%s %s", user, bard)


	def private_bard(self, user, message):
		regex = re.compile('^\@bard\s(?P<channel>[\w\#]+)\s(?P<user>[a-zA-Z0-9\-\_]+)\s?(?:(?P<command>[\w]+))?$')
		r = regex.search(message.strip())
		if r.groupdict():
			channel = r.groupdict()['channel']
			if not channel.startswith("#"):
				channel = "#"+channel
			channel = unicodedata.normalize('NFKD', channel).encode('ascii','ignore')
			user = r.groupdict()['user']
			command = r.groupdict()['command']
			if command:
				self.param_bard(channel, user, command)
			else:
				self.random_bard(channel, user)
	
	def param_bard(self, channel, user, command):
		if command in self.specific_bards:
			bard = self.specific_bards[command]
			self.say(channel, u"%s %s", user, bard)
