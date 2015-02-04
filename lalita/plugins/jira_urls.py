# -*- coding: utf-8 -*-
# Copyright 2015 Sebastian Alvarez <sebastianmalvarez@gmail.com>
# License: GPL v3
# For further info, see LICENSE file

import re

from lalita import Plugin


class JiraUrls(Plugin):

    def init(self, config):
        """Init the plugin."""

        self.register(self.events.PUBLIC_MESSAGE, self.message)

    def message(self, user, channel, message, date=None, time=None):
        """Understand what comes from the channel."""

        urls = self.find_jira_ids(message)

        if(urls):
            for url in urls:
                self.say(channel, '%s, %s' % (user, url))

    def find_jira_ids(self, text):
        ids = []
        jira_urls = []
        regex = re.compile('^(\w+\-\d+)$', re.IGNORECASE)
        for word in text.split(' '):
            if(regex.search(word)):
                ids.append(word)

        for id in ids:
            jira_base_url = u"https://photorank.atlassian.net/browse/"
            jira_urls.append(u"%s%s" % (jira_base_url, id))

        return jira_urls
