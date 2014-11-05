# -*- coding: utf-8 -*-
# Copyright 2014 Sebastian Alvarez <sebastianmalvarez@gmail.com>
# License: GPL v3
# For further info, see LICENSE file

from lalita import Plugin

class PaginasAmarillas(Plugin):

    def init(self, config):
        """Init the plugin."""

        self.register(self.events.COMMAND, self.process_pa, ['number', 'pa'])

        self.plomeros = [
                {
                    "name": "Daniel Godoy",
                    "phone": "3515180898"
                }
        ]

        #self.gasistas = [
                #{
                    #"name": "Daniel Godoy",
                    #"phone": "3515180898"
                #}
        #]

    def process_pa(self, user, channel, command, *what):
        """Understand what comes from the channel."""

        job = what[0]
        if not job.endswith('s'):
            job = job + 's'
        if job in dir(self):
            self.option_answer(user, channel, command, job)
        else:
            self.say(channel, u"%s I Don't know any '%s'?" % (user, job))

    def option_answer(self, user, channel, command, job):
        people_list = [("%s (%s)" % (person['name'], person['phone'])) for person in self.__dict__[job]]
        self.say(channel, u"%s this is the people I know: %s" % (user, ', '.join(people_list)))
