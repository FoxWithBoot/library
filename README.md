# library
Учебное задание


# Библиотека
## Предметная область
В библиотечном каталоге каждая книга имеет следующие 
атрибуты: название, автор (ы), год издания, место издания (М, СПб, Мн, К, Л), количество 
страниц, стоимость, рубрика (естественные науки, гуманитарные науки, технические 
науки, беллетристика и т.п.), тип книги (учебник, монография, художественная литература, 
редкий фонд и т.п.), способ выдачи (читальный зал, на руки). В каталоге может находиться 
один или несколько экземпляров одной и той же книги. Читатели при записи в бибилиотеку 
предоставляют о себе персональные данные: фамилия, имя, отчество, данные паспорта либо 
свидетельства о рождении (серия, номер), e-mail. При выдаче/возврате книги фиксируется 
дата выдачи/возврата. Читатель может взять любое количество книг, но не более одного 
экземпляра одной и той же книги. Книги из редкого фонда выдаются на строго ограниченный 
срок – 1 неделя. При возврате такой книги позже указанного срока читателю начисляется 
штраф в размере 0,3% от стоимости книги.

## Задание
1. Создать базу данных в соответствии с предметной областью. Определить необходимые 
отношения, ограничения для полей. Установить связи для поддержки ссылочной 
целостности.
2. Создать триггеры:
 - для запрета удаления читателя в случае, если у него на руках имеется хотя бы одна 
книга.
 - для проверки правильности формирования "Серия документа" и "Номер документа"
3. Создать пакет, содержащий следующие функции и процедуры:
А) Функция, возвращающая строку "старое издание" для учебников, выпущенных 20 и 
более лет назад.
Б) Функция, возвращающая для значения поля "Место издания":
"М" – строку "Москва",
"Л" – строку "Ленинград",
"Мн" – строку "Минск",
"К" – строку "Киев",
"СПб" – строку "Санкт-Петербург",
а для всех остальных значений – исходное место издания без изменения.
В) Функция, преобразующая значение ФИО в фамилию с инициалами (например, 
"Тургенев Иван Сергеевич" в "Тургенев И.С.")
Г) Функция возвращающая уведомление о просреченных читателем книгах
4. Спроектировать и создать выходной документ, который содержит 
сгруппированные книги по издательствам с указанием количества книг, изданных этими 
издательствами. Возле каждой книги указать количество востребований.