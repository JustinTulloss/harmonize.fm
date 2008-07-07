import logging
import cjson
import random
from masterapp.lib.base import *
from masterapp.lib.decorators import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_any_friend
)
from sqlalchemy import sql, or_, and_
from masterapp import model
from masterapp.config.schema import dbfields
from masterapp.model import (
    Song,
    Album, 
    Artist, 
    Owner,
    SongOwner,
    RemovedOwner,
    File, 
    Session, 
    User, 
    Playlist, 
    PlaylistSong,
    Spotlight
)
from pylons import config
from facebook import FacebookError
from facebook.wsgi import facebook
from operator import itemgetter
from functools import partial
from masterapp.lib.snippets import build_json, get_user
from ecs import *
import xml.dom.minidom


def get_asin(id,type):
    album = None

    if type == 'album':
        album = Session.query(Album).get(id)
    else:
        qry = Session.query(SongOwner).filter(SongOwner.uid == session['userid']).filter(SongOwner.songid == id)
        if qry.count() != 0:
            # user already has this song
            return "0"
        try:
            album = Session.query(Song).get(id).album
        except:
            return "0"
    if album:
        if album.mp3_asin:
            return album.mp3_asin
        elif album.asin:
            return album.asin
        else:
            return "0"
    else:
        return "0"
