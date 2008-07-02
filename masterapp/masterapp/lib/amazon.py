import logging
import cjson
import random
from masterapp.lib.base import *
from masterapp.lib.decorators import *
from masterapp.lib.fbauth import (
    ensure_fb_session, 
    filter_friends,
    filter_sql_friends,
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


def get_asin(id, type):
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
        albumid = album.id
        asin = Session.query(Album).get(albumid).asin
        if asin:
            try:
                items = ItemSearch(album.artist.name, Title=album.title, SearchIndex="MP3Downloads", AWSAccessKeyId='17G635SNK33G1Y7NZ2R2')
                for item in items:
                    if item.ProductGroup == "Digital Music Album" and item.Creator.lower() == album.artist.name.lower():
                        #found += 1
                        #r[item.Title]= item.ASIN
                        return item.ASIN
                        #s += item.Title + ' : ' + item.ASIN + ' by ' + item.Creator + ' : <a href="' + item.DetailPageURL +'" target="_blank">link</a><br />'
                return asin
            except KeyError:
                return asin
    return "0"

