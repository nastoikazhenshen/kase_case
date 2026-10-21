# Запуск офлайн-демо

## Предварительные условия

- Python 3.12 (проверено 3.12.14, Windows);
- отдельный локальный evidence ZIP, полученный из доверенного внутреннего канала;
- публичный клон проекта и `mvp/requirements.lock.txt`.

Чистый клон намеренно не содержит `mvp/data/raw/`, `mvp/data/processed/` и готовые отчёты. Пока пакет доказательств не восстановлен, запуск сборки должен завершиться ошибкой отсутствующего файла или проверкой целостности. Не создавайте пустые данные и не отключайте проверку хешей.

```powershell
py -3.12 -m venv mvp/.venv
mvp/.venv/Scripts/python.exe -m pip install -r mvp/requirements.lock.txt
mvp/.venv/Scripts/python.exe mvp/scripts/restore_evidence.py "путь/к/bondscope-evidence.zip"
mvp/.venv/Scripts/python.exe -m mvp.src.build_snapshot
mvp/.venv/Scripts/python.exe mvp/scripts/export_report.py
mvp/.venv/Scripts/python.exe -m streamlit run mvp/src/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

`restore_evidence.py` проверяет все пути, типы файлов, размеры и SHA-256 до первой записи. Он отклоняет symlink/path traversal/Windows aliases, посторонние каталоги и отличающиеся существующие файлы. Одинаковые файлы допускают повторное восстановление. Обрабатывается только формат `BS3-local-evidence-1`, а не исходные ZIP из стартового комплекта. Код проекта и настройки из пакета не извлекаются.

В этой локальной поставке ZIP находится в `mvp/local_pack/bondscope-evidence.zip`. Перед передачей проверьте SHA-256 по `mvp/implementation/local_pack_manifest.json`. Публичный Git не раздаёт его; права на копирование материалов KASE остаются внешним ограничением.

## Что проверять в демо

1. Сборщик проверяет пути и SHA-256, затем формирует локальный snapshot.
2. Интерфейс показывает пять выпусков и ограничения качества, а не обещает рыночную полноту.
3. Ценовые и исторические правила блокируются при непроверенной вкладке цены, режиме, финальности или недостатке истории.
4. Экспорт создаёт локальные `report.json`, `mvp_results.csv` и `report.html` в `mvp/outputs/`. CSV содержит типы строк `EVALUATION`, `EVENT`, `VALUATION`, `SOURCE`; для таблицы правил фильтруйте `record_type=EVALUATION`. Все типы имеют один `report_id`.

Для локальной рабочей книги после экспорта нужен авторский Node runtime с `@oai/artifact-tool`:

```powershell
node mvp/scripts/build_workbook.mjs
```

Результат `mvp/outputs/mvp_results.xlsx` локален и не входит в публичный Git. Этот шаг не устанавливает пакеты и не публикует файл.

Не запускайте acquisition как часть демонстрации. Свежие API-ревизии отделены от архивных строк, а автоматическое обновление не снимает ограничения по mode/price view/history.

## Проверки и явное обновление

```powershell
mvp/.venv/Scripts/python.exe -m unittest discover -s mvp/tests -v
mvp/.venv/Scripts/python.exe -m unittest discover -s mvp/data/raw/archive/verification/tests -v
mvp/.venv/Scripts/python.exe mvp/scripts/reconcile_sources.py
mvp/.venv/Scripts/python.exe -m ruff check mvp/src mvp/tests mvp/scripts --select F
```

Без локального пакета real-source тесты явно пропускаются; это не подтверждает реальную интеграцию. Для браузерной проверки отдельно установите Chromium командой `python -m playwright install chromium`, запустите приложение на 127.0.0.1:8501 и выполните `python mvp/scripts/browser_smoke.py`. Проверка блокирует все внешние браузерные запросы. Состояния missing/corrupt/empty также проверяются через Streamlit AppTest в изолированных тестах.

Пример отдельного сбора с новой папкой ревизии (требуется сеть):

```powershell
python -m mvp.src.acquisition --ticker BIGDb5 --cache-dir mvp/data/raw/acquisition/new-review --attempts mvp/data/raw/acquisition/new-review/attempts.jsonl
```

Существующий кэш не заменяется. Новая ревизия требует проверки человеком и манифеста перед включением в снимок; команда сама снимок не обновляет. Сборщик не обходит WAF.
