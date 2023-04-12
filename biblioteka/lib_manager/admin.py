import io
from datetime import date

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.forms import HiddenInput
from django.http import StreamingHttpResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _

from lib_manager.models import CustomUser, Type, Heading, PublishPlace, Book, BookManager

from lib_manager.forms import BooksInlineForm

from lib_manager.filters import BookArrivalFilter, HeadingEmptyFilter, FineFilter

from lib_manager.file_manager import create_doc


class BooksInline(admin.TabularInline):
    model = CustomUser.books.through
    readonly_fields = ('issue_date', 'deadline_days')
    classes = ('collapse',)
    formset = BooksInlineForm
    list_filter = ('deadline_days', )

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    BookManager.deadline_days.short_description = 'Осталось дней'


class CustomUserAdmin(UserAdmin):
    readonly_fields = [
        'date_joined', 'last_login'
    ]
    list_filter = ('is_staff', 'is_superuser', 'groups', FineFilter, )
    list_display = ('username', 'fio', 'is_staff', 'is_superuser', 'fine')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal info'), {
            'fields': ('email', 'first_name', 'last_name', 'surname', 'passport')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups'
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    inlines = [BooksInline, ]
    CustomUser.fio.short_description = 'ФИО'
    CustomUser.fio.short_description = 'Штраф'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['groups'].disabled = True
            form.base_fields['is_superuser'].disabled = True
            if obj != request.user:
                for i in form.base_fields:
                    form.base_fields[i].disabled = True
                form.base_fields['passport'].widget = HiddenInput()

        qs = BookManager.objects.filter(reader=obj, return_date=None)
        books = ''
        for i in qs:
            if i.deadline_days() < 0:
                books += f'{i.book.name} {i.book.author}; '
        if len(books) > 0:
            self.message_user(request,
                              f'Этот пользователь взял в библиотеке следующие книги: {books}и не вернул их в срок.',
                              messages.ERROR)
        return form

    def delete_model(self, request, obj):
        if BookManager.objects.filter(reader=obj, return_date=None).exists():
            messages.error(request, f"Пользователь {obj} не сдал все книги, поэтому не может быть удален.")
        else:
            BookManager.objects.filter(reader=obj).delete()
            super().delete_model(request, obj)


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'old_izdat', 'price', 'count')
    list_filter = ('heading', 'publication_place', 'type', BookArrivalFilter)
    search_fields = ('name__startswith', 'author__icontains')
    readonly_fields = ['receipt_date']
    change_list_template = "admin/lib_manager/book/model_change_list.html"
    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'heading', 'type')
        }),
        ('Публикация', {
            'fields': ('publication_year', 'publication_place', 'pages')
        }),
        ('Техническое', {
            'fields': ('price', 'count', 'receipt_date')
        }),
    )

    def old_izdat(self, obj):
        if date.today().year-obj.publication_year > 20:
            return 'старое издание'
        return ''

    def get_urls(self):
        urls = super(BookAdmin, self).get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.create_file), name='create_file'),
        ]
        return custom_urls + urls

    def create_file(self, request):
        select_count = 'SELECT book.id, publication_place_id, COUNT(*) as count ' \
                       'FROM lib_manager_book as book ' \
                       'GROUP BY publication_place_id'
        # s = PublishPlace.objects.raw(select_count)
        # print('select_count')
        # for i in s:
        #     print(i.publication_place_id, i.title, i.count)
        # print('-'*60)

        select_vostreb = "SELECT id, bm.book_id, COUNT(*) AS count " \
                         "FROM lib_manager_BookManager as bm " \
                         "WHERE current_date - bm.issue_date < 1 " \
                         "GROUP BY bm.book_id"
        # s = BookManager.objects.raw(select_vostreb)
        # print('select_vostreb')
        # for i in s:
        #     print(i.book_id, i.count)
        # print('-' * 60)

        s = PublishPlace.objects.raw(select_count)
        select_books = 'SELECT stat.publication_place_id, stat.count, book.id, book.name ' \
                       'FROM lib_manager_book AS book ' \
                       'LEFT JOIN (%s) AS stat ' \
                       'ON book.publication_place_id=stat.publication_place_id ' \
                       'ORDER BY stat.publication_place_id' % select_count
        # s = PublishPlace.objects.raw(select_books)
        # print('select_books')
        # for i in s:
        #     print(i.publication_place_id, i.count, i.name)
        # print('-' * 60)

        select_books_with_vost = 'SELECT book.publication_place_id, book.count, book.id, book.name, vost.count as v_c ' \
                                 'FROM (%s) AS book ' \
                                 'LEFT JOIN (%s) AS vost ON vost.book_id=book.id' % (select_books, select_vostreb)
        # s = PublishPlace.objects.raw(select_books_with_vost)
        # print('select_books_with_vost')
        # for i in s:
        #     print(i.publication_place_id, i.count, i.name, i.v_c)
        # print('-' * 60)

        select_book_place = 'SELECT pp.id, pp.title, stat.count, stat.name, stat.v_c ' \
                            'FROM lib_manager_PublishPlace AS pp ' \
                            'LEFT JOIN (%s) AS stat ' \
                            'ON stat.publication_place_id=pp.id' % select_books_with_vost
        s = PublishPlace.objects.raw(select_book_place)
        # print('select_book_place')
        for i in s:
            print(i.title, i.count, i.name, i.v_c)
        print('-' * 60)

        document = create_doc(s)
        buffer = io.BytesIO()
        document.save(buffer)  # сохранить свой поток памяти
        buffer.seek(0)  # перемотать поток

        response = StreamingHttpResponse(
            streaming_content=buffer,  # использовать содержимое потока
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=Отчёт.docx'
        response["Content-Encoding"] = 'UTF-8'
        return response

    old_izdat.short_description = 'Издание'


class HeadingAdmin(admin.ModelAdmin):
    list_filter = (HeadingEmptyFilter, )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Type)
admin.site.register(Heading, HeadingAdmin)
admin.site.register(PublishPlace)
admin.site.register(Book, BookAdmin)
#admin.site.register(BookManager)
