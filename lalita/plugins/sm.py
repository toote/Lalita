# -*- coding: utf-8 -*-
# Copyright 2012 Sebastian Alvarez <sebastianmalvarez@gmail.com>
# License: GPL v3
# For further info, see LICENSE file

"""
Standup Meeting Plugin.

Simple Lalita plugin to manage standup meetings in the channel

"""

import random
import smtplib
import datetime

from email.mime.text import MIMEText

from twisted.internet import reactor

from lalita import Plugin


class SM(Plugin):

    """
    SM class.

    The main heart of everything

    """

    def init(self, config):
        """Init the plugin."""

        self.register(self.events.COMMAND, self.process_sm, ['sm'])
        self.email = config['email']
        self.password = config['password']
        self.to = config['to']
        if 'remember_time' in config:
            self.remember_time = config['remember_time']
        else:
            # 30 minutes by default
            self.remember_time = 60 * 30
        self.config()

    def config(self):
        """Configure the plugin for the instance, used to re-start also."""

        self.users = tuple()
        self.order = list()
        self.sm = dict()
        self.started = False
        self.cancel = False
        self.started_by = None
        self.started_on = None
        self.rememberer = None

    def process_sm(self, user, channel, command, *what):
        """Understand what comes from the channel."""

        f = 'option_' + what[0]
        if f in dir(self):
            getattr(self, f)(user, channel, command, what[1:])
        else:
            self.say(channel, u"%s What the heck is '%s'?" % (user, what[0]))

    def option_add(self, user, channel, command, what):
        """Add command."""

        if self.started:
            self.users = tuple(list(self.users) + list(what))
            self.order = self.order + list(what)
            random.shuffle(self.order)
            for auser in what:
                self.sm[auser] = dict()
            self.say(channel, u"Added %s to the meeting" % (', '.join(what)))

    def option_start(self, user, channel, command, what):
        """Start command."""

        if not what:
            say = u"%s You need to tell me who \
is going to be at the SM" % (user)
            self.say(channel, say)
        else:
            self.users = what
            self.order = list(what)
            random.shuffle(self.order)
            for auser in self.users:
                self.sm[auser] = dict()
            say = u"Starting standup meeting with %s. \
%s is leading it" % (', '.join(self.users), user)
            self.say(channel, say)
            self.started = True
            self.started_by = user
            self.started_on = datetime.datetime.now()
            self.rememberer = reactor.callLater(self.remember_time, self.check_status, channel)

    def check_status(self, channel):
        """Callable to remember everyone to do the SM."""

        if self.started:
            who = self.check_who_didnt_finish()
            self.say(channel, u"%s Remember to do the SM!" % (', '.join(who)))
            self.rememberer = reactor.callLater(self.remember_time, self.check_status, channel)

    def option_1(self, user, channel, command, what):
        """What I did command."""

        if user in self.sm:
            self.sm[user][1] = " ".join(what)
            if self.check_if_finished():
                self.option_end(self.started_by, channel, command, what)
        else:
            self.say(channel, u"%s you are not invited to this sm" % (user))

    def option_2(self, user, channel, command, what):
        """What I will do command."""

        if user in self.sm:
            self.sm[user][2] = " ".join(what)
            if self.check_if_finished():
                self.option_end(self.started_by, channel, command, what)
        else:
            self.say(channel, u"%s you are not invited to this sm" % (user))

    def option_3(self, user, channel, command, what):
        """What I need command."""

        if user in self.sm:
            self.sm[user][3] = " ".join(what)
            if self.check_if_finished():
                self.option_end(self.started_by, channel, command, what)
        else:
            self.say(channel, u"%s you are not invited to this sm" % (user))

    def option_cancel(self, user, channel, command, what):
        """Cancel command."""

        if self.cancel and user == self.started_by:
            self.say(channel, u"%s Ok, done" % (user))
            self.config()
        else:
            say = u"%s Say cancel again!! say cancel again!! \
I dare you!! I double dare you motherf***" % (user)
            self.say(channel, say)
            self.cancel = True

    def option_check(self, user, channel, command, what):
        """Check SM status command."""

        if self.started:
            didnt_finish = ', '.join(self.check_who_didnt_finish())
            say = u"Users who didnt finish yet: %s" % (didnt_finish)
            self.say(channel, say)

    def option_list(self, user, channel, command, what):
        """List user command."""

        if self.started:
            say = u"Users addded to the sm: %s. Meeting leaded by %s" % (', '.join(self.users), self.started_by)
            self.say(channel, say)

    def check_if_finished(self):
        """Check if the sm is finished.

        returns Boolean

        """

        for user, options in self.sm.iteritems():
            if 1 not in options or 2 not in options or 3 not in options:
                return False
        return True

    def check_who_didnt_finish(self):
        """Check who needs to finish the SM.

        Check who needs to finish the SM
        and returns a list of users who didnt finish.

        """

        not_finished = []
        for user, options in self.sm.iteritems():
            if 1 not in options or 2 not in options or 3 not in options:
                not_finished.append(user)
        return not_finished

    def option_end(self, user, channel, command, what):
        """End the SM command."""

        if self.started and user == self.started_by:
            self.say(channel, u"Ending the meeting....")

            self.say(channel, u"Sending emails....")
            msg_text = u""
            for user in self.users:
                msg_text += u"\n\n#%s\n\n" % (user)
                if 1 in self.sm[user]:
                    msg_text += u"1. " + (self.sm[user][1]) + "\n"
                if 2 in self.sm[user]:
                    msg_text += u"2. " + (self.sm[user][2]) + "\n"
                if 3 in self.sm[user]:
                    msg_text += u"3. " + (self.sm[user][3]) + "\n"
            msg = MIMEText(msg_text.encode('utf-8'))
            formated_date = self.started_on.strftime("%d-%m-%Y")
            msg['Subject'] = u"[SM] %s" % (formated_date)
            msg['From'] = self.email
            msg['To'] = self.to
            s = smtplib.SMTP('smtp.sendgrid.net', 25)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(self.email, self.password)
            s.sendmail(self.email, [self.to], msg.as_string())
            s.quit()

            self.say(channel, u"Resetting....")
            msg_text = None
            self.config()

            self.say(channel, u"Done. One is glad to be of service")
        else:
            say = u"%s You must start before you end (#twss)" % (user)
            self.say(channel, say)
