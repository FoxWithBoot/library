from datetime import date

from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm

from lib_manager.models import BookManager


def validate_reader_book_count(value):
    # reader = value.reader
    print(value)
    print(value, "RRRR")
    if BookManager.objects.filter(reader=value.reader, return_date=None).exists():
        print(value.reader, "SSSSSSSss")
        raise ValidationError("Читатель уже взял эту книгу и пока не вернул.")


class BooksInlineForm(BaseInlineFormSet):
    # class Meta:
    #     model = CustomUser.books.through
    #     fields = ['book', 'issue_date', 'return_date']

    def clean(self):
        super().clean()
        for form in self.forms:
            cleaned_data = form.cleaned_data
            if cleaned_data:
                if not cleaned_data['return_date']:
                    reader = cleaned_data['reader']
                    if BookManager.objects.filter(reader=reader, return_date=None).exists():
                        if cleaned_data['DELETE']:
                            form.add_error(None, ValidationError("Нельзя удалить запись пока читатель не вернет книгу.",
                                                                 code='invalid_delete'))
                            raise ValidationError('', code='invalid_delete')
                        else:
                            form.add_error('book', ValidationError("Читатель уже взял эту книгу и пока не вернул.",
                                                                   code='invalid_book1'))
                            raise ValidationError('', code='invalid_book1')
                    if cleaned_data['book'].count == 0:
                        # raise ValidationError({'book': "Все экземпляры сейчас на руках."})
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


