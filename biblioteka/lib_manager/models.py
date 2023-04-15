from datetime import date, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    names_validator = RegexValidator(regex="^[A-ZА-Я][a-zа-я]*$", message="Должно начинаться с заглавной буквы.")

    first_name = models.CharField(_("Имя"), max_length=32, validators=[names_validator],
                                  help_text="Обязательное поле. Имя с заглавной буквы.")
    last_name = models.CharField(_("Фамилия"), max_length=32, validators=[names_validator],
                                 help_text="Обязательное поле. Фамилия с заглавной буквы.")
    surname = models.CharField(_("Отчество"), max_length=32, blank=True, validators=[names_validator])
    passport = models.CharField(_("Паспорт"), max_length=32, unique=True,
                                error_messages={
                                  "unique": _("Пользователь с такими паспортными данными уже зарегистрирован."),
                                },
                                validators=[RegexValidator(regex="^([I,V,X,L,M]+-[А-Я]{2})|(\d{4}) \d{6}$",
                                                           message="Не соответствует маске документа.")],
                                help_text="Обязательное поле. Серия и номер паспорта или свидетельства о рождении.")
    email = models.EmailField(_("email address"),
                              unique=True,
                              error_messages={
                                  "unique": _("Пользователь с такой почтой уже зарегистрирован."),
                              },)

    books = models.ManyToManyField('Book', through='BookManager', blank=True)

    EMAIL_FIELD = None
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "surname", "passport"]

    def fio(self):
        if self.surname:
            return "%s %s.%s." % (self.last_name, str(self.first_name)[0], str(self.surname)[0])
        else:
            return "%s %s." % (self.last_name, str(self.first_name)[0])

    def fine(self):
        qs = BookManager.objects.filter(reader=self, return_date=None)
        fine = 0
        for i in qs:
            if i.deadline_days() < 0 and i.book.type.title == 'редкий фонд':
                fine += i.book.price*0.003
        return fine


class PHT(models.Model):
    title = models.CharField(_("Название"), max_length=32, default='')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class PublishPlace(PHT):
    pass

    class Meta:
        verbose_name = _("Место издания")
        verbose_name_plural = _("Места издания")

    def __str__(self):
        place = {
            "М": "Москва",
            "Л": "Ленинград",
            "Мн": "Минск",
            "К": "Киев",
            "СПб": "Санкт-Петербург"
        }
        if self.title in place:
            return "%s - %s" % (self.title, place.get(str(self.title)))
        else:
            return self.title


class Heading(PHT):
    pass

    class Meta:
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"


class Type(PHT):
    pass
    days = models.PositiveIntegerField(_("Насколько выдается"), default=30)

    class Meta:
        verbose_name = "Тип книги"
        verbose_name_plural = "Типы книг"


class Book(models.Model):
    METHOD_TYPE = [
        (1, 'читальный зал'),
        (2, 'на руки')
    ]

    name = models.CharField(_("Название"), max_length=32)
    author = models.CharField(_("Автор(-ы)"), max_length=32)
    heading = models.ForeignKey('Heading', on_delete=models.DO_NOTHING, verbose_name='Рубрика')
    publication_year = models.PositiveIntegerField(_("Год издания"))
    publication_place = models.ForeignKey('PublishPlace', on_delete=models.DO_NOTHING, verbose_name='Место издания')
    pages = models.PositiveIntegerField(_("Количество страниц"))
    price = models.FloatField(_("Стоимость"))
    type = models.ForeignKey('Type', on_delete=models.DO_NOTHING, verbose_name='Тип')
    method = models.PositiveIntegerField(_("Способ выдачи"), choices=METHOD_TYPE, default=1)
    count = models.PositiveIntegerField(_("Количество экземпляров"), default=1)
    receipt_date = models.DateField(_("Дата поступления"), default=date.today)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-receipt_date']

    def __str__(self):
        return self.name


class BookManager(models.Model):
    reader = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, verbose_name=_("Читатель"))
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING, verbose_name=_("Книга"))
    issue_date = models.DateField(default=date.today, verbose_name=_("Дата выдачи"))
    return_date = models.DateField(blank=True, null=True, verbose_name=_("Дата возврата"))

    class Meta:
        verbose_name = _("Book Manager")
        verbose_name_plural = _("Book Manager")

    def __str__(self):
        return "%s: %s - %s" % (self.book.author, self.book.name, self.reader.fio())

    @classmethod
    def book_count_manage(cls, sender, instance, created, *args, **kwargs):
        print(sender, instance, created)
        book = instance.book
        if created:
            book.count -= 1
        elif instance.return_date:
            book.count += 1
        book.save()

    def deadline_days(self):
        return (self.issue_date+timedelta(days=self.book.type.days)-date.today()).days


post_save.connect(BookManager.book_count_manage, sender=BookManager)
