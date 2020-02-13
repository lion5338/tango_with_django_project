from django.contrib import admin
from rango.models import Category, Page
from rango.models import UserProfile
class Cust_Admin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, Cust_Admin)
admin.site.register(UserProfile)
# Register your models here.