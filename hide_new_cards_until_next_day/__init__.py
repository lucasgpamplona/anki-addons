#!/usr/bin/env python

from aqt import mw
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import getText, showInfo
from anki.lang import _
# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from anki import Collection

# import constant
from anki.consts import QUEUE_TYPE_MANUALLY_BURIED
from aqt import gui_hooks
from datetime import datetime
from time import time_ns
import re

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.
MARKER_SEP = '_'
MARKER_TAG_BASE = 'zTagHidden' + MARKER_SEP
REGEX_TAG = re.compile(f'^{MARKER_TAG_BASE}')


def marker_today():
    d = datetime.fromtimestamp(time_ns()//10**9)
    d = datetime(d.year, d.month, d.day, 0)
    return d


def marker_tag() -> str:
    return f'{MARKER_TAG_BASE}{marker_today().strftime("%Y-%m-%d")}'


def is_marker_tag_from_today(tag: str) -> bool:
    if tag != marker_tag():
        return False
    return True


def remove_mark_tags(note, tags: list) -> None:
    for tag in tags:
        if is_marker_tag_from_today(tag):
            continue
        if REGEX_TAG.search(tag):
            note.delTag(tag)
        # TODO: remove after lucas use it
        if re.search(r'^z\.lucas', tag):
            note.delTag(tag)


def custom_bury_cards(*args, **kargs) -> None:
    ids = mw.col.find_notes("is:new -is:suspended added:1")
    mw.col.sched.suspendCards(ids)
    mw.col.tags.bulkAdd(ids, marker_tag())
    mw.reset()


def custom_unbury_cards(*args, **kargs) -> None:
    ids = mw.col.find_cards(f'tag:"{MARKER_TAG_BASE}*"')
    for id in ids:
        card = mw.col.getCard(id)
        note = card.note()
        remove_mark_tags(note, note.tags)
        note.flush()
    mw.reset()


def marker_main(*args, **kargs) -> None:
    custom_bury_cards()
    custom_unbury_cards()


gui_hooks.add_cards_did_add_note.append(marker_main)
# create a new menu item, "Organizar Cartões"
action = QAction("Organizar Cartões", mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, marker_main)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
