# -*- encoding: utf-8 -*-

from . import views
from django.urls import path
from django.urls import re_path

urlpatterns = [
    path('', views.MeetsPopular.as_view(), name='index'),
    path('account/my', views.MyAccount.as_view(), name='my_account'),
    path('user/<str:username>', views.Friendship.as_view(), name='user'),
    path('friends', views.Friends.as_view(), name='friends'),
    path('conversations', views.Conversations.as_view(), name='conversations'),
    path('conversation/<int:pk>', views.Conversation.as_view(), name='conversation'),
    path('user/<str:username>/message', views.TalkToFriend.as_view(), name='messageusr'),
    path('meet/<str:key>/message', views.TalkToMeetOrganizer.as_view(), name='messagemeet'),
    path('meet/new', views.MeetNew.as_view(), name='meetnew'),
    path('meet/hints', views.MeetHints.as_view(), name='meethints'),
    path('meet/<str:key>', views.MeetView.as_view(), name='meet'),
    path('meet/<str:key>/edit', views.MeetEdit.as_view(), name='meetedt'),
    path('meet/<str:key>/edit/links', views.MeetLinksEdit.as_view(), name='meetlinks'),
    path('meetlink/<int:pk>', views.MeetLinkEdit.as_view(), name='meetlink'),
    path('meet/<str:key>/stars', views.MeetStars.as_view(), name='meetstars'),
    path('meetstar/<int:pk>', views.MeetStarEdit.as_view(), name='meetstar'),
    path('meets/nearby', views.MeetsNearby.as_view(), name='meets_nearby'),
    re_path(r'^meets/nearby/(?P<lats>-?\d+(?:\.\d+)?);(?P<longs>-?\d+(?:\.\d+)?)$', views.MeetsNearby.as_view(), name='meets_nearby_precise'),
    path('meets/popular', views.MeetsPopular.as_view(), name='meets_popular'),
    path('ld/index.html', views.LDDump.as_view(), name="lddump"),
    path('ld/dump', views.LDDumpDownload.as_view(), name="lddumpdownload"),
    path('ld/dump.<str:fmt>', views.LDDumpDownload.as_view(), name="lddumpdownload"),
    path('ld/<str:model>/<int:pk>.<str:fmt>', views.LDModelBuild.as_view(), name="ldmodelbuild"),
]

