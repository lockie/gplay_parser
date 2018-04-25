#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import (Flask, request, abort, jsonify, make_response,
                   send_from_directory, g)
from http import HTTPStatus
import MySQLdb
from typing import Dict
from urllib.parse import urlparse, parse_qs

from .parser import do_parse


app = Flask(__name__)


def get_db() -> 'MySQLdb.Connection':
    '''Opens a new database connection if there is none yet for the
    current application context.'''
    if not hasattr(g, 'db'):
        g.db = MySQLdb.connect(host='db', db='default',
                               use_unicode=True, charset='utf8')
    return g.db


@app.teardown_appcontext
def close_db(_) -> None:
    '''Closes the database again at the end of the request.'''
    if hasattr(g, 'db'):
        g.db.close()


def error(message: str, status_code: int = HTTPStatus.BAD_REQUEST) -> None:
    abort(
        make_response((
            jsonify(message=message),
            status_code,
            {})))


def load(id_: str, hl: str) -> Dict[str, str]:
    '''Load previously queried permissions from database'''
    perms = []
    with get_db().cursor() as cursor:
        cursor.execute('SELECT id FROM Apps '
                       'WHERE identifier = %s AND language = %s',
                       (id_, hl))
        app_id = cursor.fetchone()
        if app_id is not None:
            cursor.execute('SET SESSION group_concat_max_len = 65536')
            cursor.execute('SELECT PG.title, PG.icon, GROUP_CONCAT(P.title) '
                           'FROM PermissionGroups AS PG, Permissions AS P '
                           'JOIN AppPermissions ON '
                           'P.id=AppPermissions.permission_id '
                           'WHERE P.group_id=PG.id AND '
                           'AppPermissions.app_id = %s '
                           'GROUP BY PG.title', app_id)
            raw_perms = cursor.fetchall()
            for perm in raw_perms:
                perms.append({
                    'title': perm[0],
                    'icon': perm[1],
                    'items': perm[2].split(',')
                })
    return perms


def save(id_: str, hl: str, perms: Dict[str, str]) -> None:
    '''Save permissions to database'''
    with get_db().cursor() as cursor:
        cursor.execute('INSERT IGNORE INTO Apps(identifier, language) '
                       'VALUES (%s, %s)', (id_, hl))
        cursor.execute('SELECT id FROM Apps '
                       'WHERE identifier = %s AND language = %s',
                       (id_, hl))
        app_id = cursor.fetchone()[0]
        for perm in perms:
            cursor.execute('INSERT INTO PermissionGroups(title,icon) '
                           'VALUES (%s, %s) '
                           'ON DUPLICATE KEY UPDATE icon = %s',
                           (perm['title'], perm['icon'], perm['icon']))
            cursor.execute('SELECT id FROM PermissionGroups WHERE title = %s',
                           (perm['title'],))
            group_id = cursor.fetchone()[0]
            for item in perm['items']:
                cursor.execute('INSERT INTO Permissions(title, group_id) '
                               'VALUES (%s, %s)',
                               (item, group_id))
                cursor.execute('SELECT LAST_INSERT_ID()')
                permission_id = cursor.fetchone()[0]
                cursor.execute('INSERT INTO '
                               'AppPermissions(app_id, permission_id) '
                               'VALUES (%s, %s)',
                               (app_id, permission_id))
        cursor.execute('COMMIT')


@app.route('/parse', methods=('POST',))
def parse():
    try:
        url = urlparse(request.json)
    except ValueError:
        error('Ill-formed query')
    if url.netloc != 'play.google.com':
        error('This does not look like Google Play app URL')
    params = parse_qs(url.query)
    if 'id' not in params:
        error('Missing app ID')
    id_ = next(iter(params.get('id'))).strip()
    hl = next(iter(params.get('hl') or ['en'])).strip()
    perms = load(id_, hl)
    if not perms:
        try:
            perms = do_parse(id_, hl)
            save(id_, hl, perms)
        except ValueError as e:
            error(str(e))
    return jsonify(perms)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)


@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)
