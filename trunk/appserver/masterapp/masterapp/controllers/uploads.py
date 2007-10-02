import logging

from masterapp.lib.base import *

log = logging.getLogger(__name__)

class UploadsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('upload', 'uploads')


    def index(self, format='html'):
        """GET /uploads: All items in the collection."""
        # url_for('uploads')
        return "List all"

    def create(self):
        """POST /uploads: Create a new item."""
        # url_for('uploads')
        pass

    def new(self, format='html'):
        """GET /uploads/new: Form to create a new item."""
        # url_for('new_upload')
        pass

    def update(self, id):
        """PUT /uploads/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('upload', id=ID),
        #           method='put')
        # url_for('upload', id=ID)
        pass

    def delete(self, id):
        """DELETE /uploads/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('upload', id=ID),
        #           method='delete')
        # url_for('upload', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /uploads/id: Show a specific item."""
        # url_for('upload', id=ID)
        return id

    def edit(self, id, format='html'):
        """GET /uploads/id;edit: Form to edit an existing item."""
        # url_for('edit_upload', id=ID)
        pass
