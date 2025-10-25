from django.contrib import admin
from .models import Dog

class DogAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'breed', 'owner')   # show owner in list view
    search_fields = ('name', 'breed')
    list_filter = ('age', 'breed', 'owner')
    list_display_links = ('name',)
    fields = ('owner', 'name', 'age', 'breed')         # allow setting owner when adding/editing

admin.site.register(Dog, DogAdmin)
