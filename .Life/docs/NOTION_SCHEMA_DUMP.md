# Notion Database Schema Dump
## yearly_goals (Year Goals)
ID: 223db2b98a1b805f8607ddfdfed692a7
| Property | Type |
|---|---|
| Category | select |
| Notes | rich_text |
| Due Date | date |
| Priority | select |
| Resources Needed | rich_text |
| Key Milestones | rich_text |
| Status | status |
| Progress | number |
| Why It Matters | rich_text |
| Goal | title |

## genius_list (genius_list)
ID: 1121db7adaa2433ab88135998805eaa2
| Property | Type |
|---|---|
| Оценка Маши | rich_text |
| URL | url |
| Оценка Арсения | date |
| Комментарий Арсения | rich_text |
| Комментарий Маши | rich_text |
| Tags | multi_select |
| Name | title |

## journal (Journal)
ID: ed6ee67a8f1f4c85a0039e58ff6ee52b
| Property | Type |
|---|---|
| Tags | multi_select |
| Выводы дня Х/П/МУ | rich_text |
| Оценка | number |
| Чек лист дня | relation |
| Чек лист | rollup |
| Created | created_time |
| Name | title |

## rituals (Ритуалы)
ID: 1fddb2b98a1b80b6a12dc29e84fce46d
| Property | Type |
|---|---|
| % выполнения | rollup |
| Почему работает | rich_text |
| Описание | rich_text |
| Гайды/Регламенты | relation |
| Рефлексия | relation |
| Категория | select |
| Экшены | relation |
| Микрошаг | rich_text |
| Важность | number |
| Сейчас в работ/ на паузе | checkbox |
| Пошаговая инструкция | rich_text |
| Теги | multi_select |
| Источник/Автор | rich_text |
| Треккер привычек | relation |
| Название | title |

## habits (Трекер привычек)
ID: 1fddb2b98a1b8053a54aedf250530798
| Property | Type |
|---|---|
| Выполнено | checkbox |
| Время дня | select |
| Комментарии | rich_text |
| Экшены | relation |
| Ритуалы | relation |
| Дата | date |
| Уровень энергии | number |
| Рефлексия | relation |
| Настроение | select |
| Длительность | number |
| Привычка | title |

## reflection (Рефлексия)
ID: 1fddb2b98a1b80518f9be7a55e84294f
| Property | Type |
|---|---|
| Ритуалы | relation |
| Гайды/Регламенты | relation |
| Дата | date |
| Настроение | select |
| Уровень энергии | number |
| Треккер привычек | relation |
| Что удалось | rich_text |
| Теги | multi_select |
| Сложность | rich_text |
| Урок/Вывод | rich_text |
| Микрошаг | rich_text |
| Событие | title |

## guides (Гайды/Регламенты)
ID: 1fddb2b98a1b806e8c70c1d7dd406dd8
| Property | Type |
|---|---|
| Последнее обновление | date |
| Описание | rich_text |
| Ритуалы | relation |
| Чеклист внутри | checkbox |
| Тип гайда | multi_select |
| Теги | multi_select |
| Рефлексия | relation |
| Авторы/внедрившие | rich_text |
| Сложность | select |
| Формат | multi_select |
| Канал применения | multi_select |
| Дата добавления | date |
| Name | title |

## tasks (Экшены/Задачи)
ID: 1fddb2b98a1b80d7901ecdf0cb22ce42
| Property | Type |
|---|---|
| Статус | status |
| Категория | select |
| Приоритет | select |
| Дедлайн | date |
| Шаблон таблицы материалов | relation |
| Теги | multi_select |
| Дата старта | date |
| Трекер привычек | relation |
| Результат | rich_text |
| Ритуалы | relation |
| Описание | rich_text |
| Задача | title |

## terms (Термины)
ID: 201db2b98a1b800ea076deec76f5f17a
| Property | Type |
|---|---|
| Оценка/ROI | rich_text |
| Тема / Теги | rich_text |
| Статус | rich_text |
| Формулировка карточки RemNote | rich_text |
| Определение | rich_text |
| Формат | select |
| План применения | rich_text |
| Категория | select |
| Дата добавления | date |
| Name | title |

## materials (Материалы)
ID: 1ffdb2b98a1b80b98cffce229152b0d7
| Property | Type |
|---|---|
| Инсайт/Заметка | rich_text |
| Архив | checkbox |
| Категория | select |
| Ссылка/Файл | url |
| Оценка/ROI | rich_text |
| Статус | status |
| Формат | select |
| Связанные люди/Команда | rich_text |
| План применения/Проект | rich_text |
| Рейтинг/Полезность | number |
| Автор/Источник | rich_text |
| Дата внедрения | date |
| Дата добавления | created_time |
| Теги | multi_select |
| Применено в задачах | relation |
| Презентация/Кейс | url |
| Название | title |

## agent_prompts (Промты агентов)
ID: 211db2b98a1b802d8f4cd1048e406707
| Property | Type |
|---|---|
| Статус | select |
| Версия | number |
| Промпт | rich_text |
| Дата создания | date |
| Роль | select |
| Миссия | rich_text |
| Последнее обновление | date |
| Name | title |

## ideas (База идей)
ID: 223db2b98a1b80fe8789c2fefad43f11
| Property | Type |
|---|---|
| Name | title |

## experience_hub (Experience Hub)
ID: 223db2b98a1b8025b609d4ed5b138779
| Property | Type |
|---|---|
| Name | title |

