# О проекте:
Описание с временем запуска парсеров предоставлено в соответствующих *_info.txt файлах. <br />
Поддерживаемые команды описаны в [runners.info](runners.info) <br />
Требуемые библиотеки для запуска парсеров в [requirements](requirements.txt) <br />

## Шаблоны:
[Пример тупого парсера HTML](src/trt_muzic.py) <br />
[Пример тупого парсера HTML, с угадайкой дня](src/sozcu_tv.py) <br />
[Использование js interop, для парсинга nuxt](src/trt_cocuk.py) <br />
[Обычный api](src/cartoon_network.py) <br />
[Ссылки по дням](src/beyaz_tv.py)

## Парсеры с точной временной меткой (дата по которой можно определить день):
| Парсер | Источник |
| --- | --- |
| [Cartoon Network](src/cartoon_network.py) | Из API |
| [Dost TV](src/dost_tv.py) | Запрос к серверу включает дату и время | 
| [Haber Global](src/cartoon_network.py) | Из html атрибутов |
| [Star TV](src/star_tv.py) | Из API |
| [TRT ÇOCUK](src/trt_cocuk.py) | Из JSON, получаемого при вызове JS метода |
| [TRT HABER](src/trt_haber.py) | Из URL запроса |
| [TRT MUZIC](src/trt_muzic.py) | Из html атрибута |
| [trt spor yıldız](src/trt_spor_yildizi.py) | Из JSON внутри скрипта |
| [TRT1](src/trt1.py) | Из html атрибута |
| [TV 41](src/tv41.py) | В заголовке текста точная дата |
| [Ekol Tv](src/ekol_tv.py) | Из URL запроса |
#### Остальные парсеры пытаются угать дату и время беря за начало либо текущий день, либо понедельник

## Парсеры с угадыванием времени у текущей телепередачи (просто нет времени начала):
| Парсер | Комментарий |
| --- | --- |
| [TRT belgesel](src/trt_belgesel.py) | Вместо времени надпись: "Gönüllü Veteriner" |
| [cnn türk](src/cnn_turk.py) | Вместо времени надпись: "Şimdi" |

## Парсеры игнорирующие последнюю программу (из за отсутствия даты окончания у последней передачи):
Перечислена только та ситуация, когда расписание частично затрагивает следующий день, и из за чего может быть так, что дата начала передачи в 6:00 а ее конец в 23:59. В ситуации если нет расписания на следующий день (т.е. программы завершаются за один день)автоматически устанавливается дата окончания 23:59.

| Парсер |
| --- |
| [cnn türk](src/cnn_turk.py) |
| [kANAL 3](src/kanal3.py) | 
| [kon tv](src/kon_tv.py) |
| [trt 2](src/trt2.py) |
| [TV 41](src/tv41.py) |
| [beyaz tv](src/beyaz_tv.py) |
| [TRT belgesel](src/trt_belgesel.py) |
| [TRT HABER](src/trt_haber.py) |
