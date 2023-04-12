from datetime import date
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from lib_manager.models import Book, BookManager


class BookArrivalFilter(admin.SimpleListFilter):
    title = _('Поступление')
    parameter_name = 'arrival'

    def lookups(self, request, model_admin):
        return (
            ('new', _('новое поступление')),
            ('old', _('старое поступление')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'new':
            return queryset.filter(receipt_date__year__gt=(date.today().year-3))
        if self.value() == 'old':
            return queryset.filter(receipt_date__year__lt=(date.today().year-3))


class HeadingEmptyFilter(admin.SimpleListFilter):
    title = _('Пустая рубрика')
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return (
            ('emp', _('нет книг')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'emp':
            qs = Book.objects.values_list('heading', flat=True).distinct()
            return queryset.exclude(id__in=qs)


class FineFilter(admin.SimpleListFilter):
    title = _('Штраф')
    parameter_name = 'fine'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('да')),
            ('no', _('нет')),
        )

    def queryset(self, request, queryset):
        qs = queryset
        if self.value() == 'yes':
            for reader in queryset:
                if reader.fine() == 0:
                    qs = qs.exclude(id=reader.id)
            return qs
        else:
            for reader in queryset:
                if reader.fine() > 0:
                    qs = qs.exclude(reader)
            return qs
