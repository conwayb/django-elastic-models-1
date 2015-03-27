from optparse import make_option
from datetime import datetime, timedelta
import re

from django.core.management.base import BaseCommand

from elastic_models.receivers import get_search_models

class IndexCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--since', action="store", default='', dest='since',
            help='Index data updated after this time.  yyyy-mm-dd[-hh:mm] or [#d][#h][#m][#s]'),
        make_option('--limit', action="store", default='', dest='limit',
            help='Index at most this many of each model.'),
    )
    args = '<app[.model] app[.model] ...>'
    help = 'Creates and populates the search index.  If it already exists, it is deleted first.'

    duration_re = re.compile(
        r"^(?:(?P<days>\d+)D)?"
        r"(?:(?P<hours>\d+)H)?"
        r"(?:(?P<minutes>\d+)M)?"
        r"(?:(?P<seconds>\d+)S)?$",
        flags=re.IGNORECASE)

    def parse_date_time(self, input):
        try:
            return datetime.strptime(input, "%Y-%m-%d-%H:%M")
        except ValueError:
            pass

        try:
            return datetime.strptime(input, "%Y-%m-%d")
        except ValueError:
            pass

        match = self.duration_re.match(input)
        if match:
            kwargs = dict((k, int(v)) for (k, v) in match.groupdict().items() if v is not None)
            return datetime.now() - timedelta(**kwargs)

        raise ValueError("%s could not be interpereted as a datetime" % options['since'])

    def get_models(self, args):
        models = get_search_models()
        if args:
            models = [m for m in models if
                        m._meta.app_label in args or
                        '%s.%s' % (m._meta.app_label, m._meta.model_name) in args]

        return models
