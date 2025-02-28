from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from users.views import *


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected notifications as read"

admin.site.register(Notification, NotificationAdmin) 