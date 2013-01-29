# -*- coding: utf-8 -*-
# Copyright 2012 Sebastian Alvarez <sebastianmalvarez@gmail.com>
# License: GPL v3
# For further info, see LICENSE file

import random
import smtplib
import datetime

from email.mime.text import MIMEText

from lalita import Plugin


class SM(Plugin):
	def init(self, config):
		self.register(self.events.COMMAND, self.process_sm, ['sm'])
		self.config()
	
	def config(self):
		self.users = tuple()
		self.order = list()
		self.sm = dict()
		self.started = False
		self.active = None
		self.cancel = False

	def process_sm(self, user, channel, command, *what):
		f = 'option_'+what[0]
		if f in dir(self):
			getattr(self, f)(user, channel, command, what[1:])
		else:
			self.say(channel, u"%s What the heck is '%s'?" % (user, what[0]))
	
	def option_start(self, user, channel, command, what):
		if not what:
			self.say(channel, u"%s You need to tell me who is going to be at the SM" % (user))
		else:
			self.users = what
			self.order = list(what)
			random.shuffle(self.order)
			for user in self.users:
				self.sm[user] = dict()
			self.say(channel, u"Starting standup meeting with %s" % (', '.join(self.users)))
			self.active = self.order.pop()
			self.say(channel, u"%s you are first, because of reasons" % (self.active))
			self.started = True

	def option_1(self, user, channel, command, what):
		if self.started and user == self.active:
			self.sm[user][1] = " ".join(what)
		else:
			self.say(channel, u"%s Don't be a jerk" % (user))

	def option_2(self, user, channel, command, what):
		if self.started and user == self.active:
			self.sm[user][2] = " ".join(what)
		else:
			self.say(channel, u"%s Don't be a jerk" % (user))

	def option_3(self, user, channel, command, what):
		if self.started and user == self.active:
			self.sm[user][3] = " ".join(what)
			if self.order:
				self.active = self.order.pop()
				self.say(channel, u"%s Got it, %s you are next" % (user, self.active))
			else:
				self.option_end(user, channel, command, what)
		else:
			self.say(channel, u"%s Don't be a jerk" % (user))

	def option_cancel(self, user, channel, command, what):
		if self.cancel:
			self.say(channel, u"%s Ok, done" % (user))
			self.config()
		else:
			self.say(channel, u"%s Say cancel again!! say cancel again!! I dare you!! I double dare you motherf***" % (user))
			self.cancel = True

	def option_end(self, user, channel, command, what):
		if self.started:
			self.say(channel, u"Ending the meeting....")

			self.say(channel, u"Sending emails....")
			msg_text = u""
			for user in self.users:
				msg_text += u"\n\n#%s\n\n" % (user)
				msg_text += u"1. %s\n" % (self.sm[user][1])
				msg_text += u"2. %s\n" % (self.sm[user][2])
				msg_text += u"3. %s\n" % (self.sm[user][3])
			msg = MIMEText(msg_text)
			me = "hermes@olapic.com"
			you = "developers@olapic.com"
			msg['Subject'] = u"SM %s" % (datetime.datetime.now().strftime("%d-%m-%Y"))
			msg['From'] = me
			msg['To'] = you
			s = smtplib.SMTP('smtp.gmail.com', 587)
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(me, "6DF1FFFAE081221CD3CA6415E5ABFBCA5DDB067725A99DC8771730D1DFE0673C")
			s.sendmail(me, [you], msg.as_string())
			s.quit()

			self.say(channel, u"Resetting....")
			msg_text = None
			self.config()

			self.say(channel, u"Done. One is glad to be of service")
		else:
			self.say(channel, u"%s You must start before you end (#twss)" % (user))
