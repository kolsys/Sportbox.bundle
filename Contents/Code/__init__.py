# -*- coding: utf-8 -*-

# Copyright (c) 2016, KOL
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTLICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from updater import Updater
Common = SharedCodeService.common


def Start():
    HTTP.CacheTime = CACHE_1HOUR


###############################################################################
# Video
###############################################################################

@handler(
    Common.PREFIX,
    L(Common.TITLE),
    None,
    R(Common.ICON)
)
def MainMenu():

    menu = Common.ApiRequest('menu')

    if not menu:
        return MessageContainer(
            L('Error'),
            L('Service not avaliable')
        )

    oc = ObjectContainer(title2=L(Common.TITLE), no_cache=True)

    Updater(Common.PREFIX+'/update', oc)

    oc.add(DirectoryObject(
        key=Callback(Rubric, oid=menu['id']),
        title=u'Все рубрики',
    ))

    oc.add(DirectoryObject(
        key=Callback(Rubric, oid=Common.SB_ANNONCE, is_announce=True),
        title=u'Расписание',
    ))

    for item in menu['menu']:
        oc.add(DirectoryObject(
            key=Callback(Rubric, oid=item['id']),
            title=item['name'],
        ))

    return oc


@route(Common.PREFIX + '/rubric')
def Rubric(oid, offset=None, is_announce=None):

    offset = {'page': 0, 'count': 0} if offset is None else JSON.ObjectFromString(offset)
    params = {'page': offset['page']}
    if is_announce:
        params['status'] = 'announce+live'
        params['sort'] = 'asc'

    rubric = Common.GetRubric(oid, params)

    if not rubric:
        return ContentNotFound()

    oc = ObjectContainer(
        title2=u'%s' % rubric['name'],
        replace_parent=bool(offset['page'])
    )

    if not is_announce and not offset['page'] and oid != Common.SB_ALL:
        oc.add(DirectoryObject(
            key=Callback(Rubric, oid=oid, is_announce=True),
            title=u'Расписание',
            summary=u'%s - расписание трансляций' % rubric['name'],
            thumb=R('schedule.png')
        ))

    for video in rubric['items']:
        if video['id']:
            oc.add(Common.GetVideoObject(video))

    if not len(oc):
        return ContentNotFound()

    if rubric['count']:
        offset['count'] = int(rubric['count'])

    offset['page'] = offset['page']+1

    if offset['count'] > Common.SB_LIMIT*offset['page']:
        oc.add(NextPageObject(
            key=Callback(
                Rubric,
                oid=oid,
                offset=JSON.StringFromObject(offset),
                is_announce=is_announce,
            ),
            title=u'%s' % L('Далее'),
        ))

    return oc if len(oc) else ContentNotFound()


###############################################################################
# Common
###############################################################################

def ContentNotFound():
    return MessageContainer(
        L('Error'),
        L('No entries found')
    )