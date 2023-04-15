from datetime import date

from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm, forms

from lib_manager.models import BookManager


# def validate_reader_book_count(value):
#     # reader = value.reader
#     print(value)
#     print(value, "RRRR")
#     if BookManager.objects.filter(reader=value.reader, return_date=None).exists():
#         print(value.reader, "SSSSSSSss")
#         raise ValidationError("Читатель уже взял эту книгу и пока не вернул.")


class BooksInlineForm(BaseInlineFormSet):

    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            cleaned_data = form.cleaned_data
            count += 1
            if cleaned_data:
                if not cleaned_data['return_date']:
                    reader = cleaned_data['reader']
                    book = cleaned_data['book']
                    if BookManager.objects.filter(reader=reader, book=book, return_date=None).exists():
                        if cleaned_data['DELETE']:
                            form.add_error(None, ValidationError("Нельзя удалить запись пока читатель не вернет книгу.",
                                                                 code='invalid_delete'))
                            raise ValidationError('', code='invalid_delete')
                        else:
                            if count > BookManager.objects.filter(reader=reader).count():
                                form.add_error('book', ValidationError("Читатель уже взял эту книгу и пока не вернул.",
                                                                       code='invalid_book1'))
                                raise ValidationError('', code='invalid_book1')
                    if cleaned_data['book'].count == 0:
                        if count > BookManager.objects.filter(reader=reader).count():
                            form.add_error('book', ValidationError("Все экземпляры сейчас на руках.", code='invalid_book2'))
                            raise ValidationError('', code='invalid_book2')
                else:
                    if cleaned_data['return_date'] < cleaned_data['id'].issue_date:
                        form.add_error('return_date', ValidationError("Нельзя вернуть книгу раньше, чем взять её.",
                                                                      code='invalid_date1'))
                        raise ValidationError('', code='invalid_date1')
                    if cleaned_data['return_date'] > date.today():
                        form.add_error('return_date', ValidationError("Дата в будущем.", code='invalid_date2'))
                        raise ValidationError('', code='invalid_date2')
