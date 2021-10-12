from django.contrib import admin
from .models import Book, Material, BookInstance, MaterialInstance, Genre, Author

admin.site.register(Book)
admin.site.register(Material)
admin.site.register(Genre)
admin.site.register(Author)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('label', 'book', 'status')
    list_filter = ('status',)

    fieldsets = (
        (None, {
            'fields': ('book','label', 'imprint')
        }),
        ('Availability', {
            'fields': ('status',)
        }),
    )

@admin.register(MaterialInstance)
class MaterialInstanceAdmin(admin.ModelAdmin):
    list_display = ('label', 'material', 'status')
    list_filter = ('status',)

    fieldsets = (
        (None, {
            'fields': ('material', 'label')
        }),
        ('Availability', {
            'fields': ('status',)
        }),
    )
