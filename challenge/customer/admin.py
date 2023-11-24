from django.contrib import admin
from customer import models


class CustomerUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('dni',)


admin.site.register(models.CustomerUser, CustomerUserAdmin)
admin.site.register(models.Customer, CustomerAdmin)
