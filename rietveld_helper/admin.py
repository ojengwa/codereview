"""Admin interface customizations."""
from django.contrib import admin

from codereview import models

# Patch in some simple lambda's, Django uses them.
models.Issue.__unicode__ = lambda self: self.subject
models.PatchSet.__unicode__ = lambda self: self.message or ''


class PatchSetInlineAdmin(admin.TabularInline):

    """Patchset inline admin helper."""

    model = models.PatchSet


class PatchSetAdmin(admin.ModelAdmin):

    """Patchset admin helper."""

    list_filter = ('issue', 'issue__owner')
    list_display = ('issue', 'message')
    search_fields = ('issue__subject', 'message')


class IssueAdmin(admin.ModelAdmin):

    """Issue admin helper."""

    list_filter = ('closed', 'owner')
    list_display = ('id', 'subject', 'owner', 'modified', 'n_comments')
    list_display_links = ('id', 'subject')
    inlines = [PatchSetInlineAdmin]

admin.site.register(models.Issue, IssueAdmin)
admin.site.register(models.PatchSet, PatchSetAdmin)


class CodereviewAccountAdmin(admin.ModelAdmin):

    """Admin class for codereview.models.Account model."""

    list_display = ('nickname', 'email', 'user')
    fields = ('nickname', 'email', 'lower_email',
              'user', 'lower_nickname', 'gae_key')

admin.site.register(models.Account, CodereviewAccountAdmin)
