import logging
from tag_compare import (
    compare_to_release,
    match_file_to_release,
    match_file_to_track
)
log = logging.getLogger(__name__)

class BrainzTagger(BaseAction):
    def __init__(self, *args):
        # Hook up to the database
        pconfig['pylons.g'] = Mock()
        pconfig['pylons.g'].sa_engine = engine_from_config(config,
            prefix = 'sqlalchemy.default.'
        )
        from masterapp import model
        self.model = model
