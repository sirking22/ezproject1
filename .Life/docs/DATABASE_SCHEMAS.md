# Схемы баз данных

## Существующие базы (расширение)

### 1. Рефлексия → Personal Analytics Hub

**Текущие поля:**
- Дата
- Заметка
- Настроение

**Добавить поля:**
- `flow_state` (Select): #deep-flow, #shallow-flow, #no-flow
- `energy_level` (Number): 1-10
- `focus_score` (Number): 1-10
- `session_duration` (Number): минуты
- `activity_type` (Select): #work, #learning, #creative, #admin
- `insights` (Text): ключевые инсайты
- `improvements` (Text): что улучшить
- `tags` (Multi-select): #flow, #micro-retro, #energy, #focus, #insight

**Связки:**
- Задачи (Relation)
- Материалы (Relation)
- Промпты агентов (Relation)

### 2. Материалы → Learning Content Vault

**Текущие поля:**
- Название
- Описание
- Ссылка

**Добавить поля:**
- `learning_type` (Select): #book, #article, #video, #course, #podcast
- `difficulty` (Select): #beginner, #intermediate, #advanced
- `completion_status` (Select): #not-started, #in-progress, #completed, #abandoned
- `related_goals` (Relation): Yearly Goals
- `skill_tags` (Multi-select): навыки, которые развивает
- `rating` (Number): 1-5
- `key_takeaways` (Text): основные выводы
- `action_items` (Text): что применить
- `review_date` (Date): когда пересмотреть

**Связки:**
- Yearly Goals (Relation)
- Skill Progress Tracker (Relation)
- Задачи (Relation)

### 3. Промпты агентов → AI Prompt Library

**Текущие поля:**
- Название
- Промпт
- Описание

**Добавить поля:**
- `effectiveness_rating` (Number): 1-5
- `innovation_score` (Number): 1-5
- `use_count` (Number): количество использований
- `success_rate` (Number): % успешных результатов
- `agent_type` (Select): #task-agent, #creative-agent, #analytics-agent
- `context` (Text): когда использовать
- `improvements` (Text): как улучшить
- `tags` (Multi-select): #auto, #fail, #insight, #repeat, #effective

**Связки:**
- AI Worklog (Relation)
- Задачи (Relation)
- Experiment Log (Relation)

## Новые базы

### 4. AI Worklog

**Поля:**
- `date` (Date): дата взаимодействия
- `agent_name` (Text): имя агента
- `request` (Text): запрос к агенту
- `response` (Text): ответ агента
- `result` (Text): результат использования
- `insight` (Text): инсайт или вывод
- `time_spent` (Number): время в минутах
- `satisfaction` (Number): удовлетворенность 1-5
- `tags` (Multi-select): #auto, #fail, #insight, #repeat, #effective
- `related_task` (Relation): связанная задача
- `experiment` (Relation): связанный эксперимент

### 5. Skill Progress Tracker

**Поля:**
- `skill_name` (Text): название навыка
- `current_level` (Select): #beginner, #intermediate, #advanced, #expert
- `target_level` (Select): целевой уровень
- `description` (Text): описание навыка
- `checkpoints` (Text): чекпоинты прогресса
- `last_assessment` (Date): последняя оценка
- `next_review` (Date): следующая проверка
- `learning_materials` (Relation): связанные материалы
- `practice_tasks` (Relation): задачи для практики
- `retrospection` (Text): ретроспектива прогресса

### 6. Experiment Log

**Смысл:**
База для фиксации гипотез, экспериментов, тестов, изменений в привычках/воркфлоу/AI. Используется для анализа, повторения, поиска инсайтов и внедрения новых паттернов.

**Поля:**
- `date` (Date): дата эксперимента
- `title` (Text): название эксперимента
- `hypothesis` (Text): гипотеза, которую проверяешь
- `action` (Text): что делал в рамках эксперимента
- `result` (Text): результат (что реально произошло)
- `conclusions` (Text): выводы по итогам
- `repeat_decision` (Select): #repeat, #modify, #abandon
- `success_score` (Number): субъективная оценка успеха 1-5
- `tags` (Multi-select): #success, #failure, #insight, #automation, #habit, #ai, #workflow и др.
- `related_habits` (Text): привычки/навыки, которые тестировались
- `related_tasks` (Text): задачи, которые были частью эксперимента
- `related_prompts` (Text): промпты/AI, которые тестировались
- `formula_success` (Text): формула для оценки успеха (например: success_score * (result == 'успех'))
- `experience_hub_link` (Text): если эксперимент дал инсайт — ссылка/описание для Experience Hub

**Пояснения:**
- Если эксперимент связан с привычкой/задачей/AI — указывай это явно.
- Формулы (например, для success) пиши как текст, чтобы потом реализовать в Notion.
- Если эксперимент дал инсайт — фиксируй его в Experience Hub и делай ссылку/описание здесь.

**Рекомендации:**
- Не бойся фиксировать даже мелкие эксперименты — это источник инсайтов.
- Периодически делай ретроспективу: что реально сработало, что нет.
- Инсайты и best practices — в Experience Hub.

### 7. Personal KPI Dashboard

**Поля:**
- `date` (Date): дата метрики
- `task_speed` (Number): скорость выполнения задач
- `automation_percentage` (Number): % автоматизации
- `new_skills` (Number): новых навыков за период
- `innovative_actions` (Number): инновационных действий
- `flow_time` (Number): время в потоке (часы)
- `energy_avg` (Number): средняя энергия
- `focus_avg` (Number): средний фокус
- `productivity_score` (Number): общий скор продуктивности
- `notes` (Text): заметки по метрикам

### 8. AI/Agent Evolution Log

**Поля:**
- `date` (Date): дата изменения
- `agent_name` (Text): имя агента
- `change_type` (Select): #new-feature, #improvement, #bug-fix, #optimization
- `improvement` (Text): описание улучшения
- `patterns_standardized` (Text): стандартизированные паттерны
- `impact` (Select): #low, #medium, #high
- `testing_results` (Text): результаты тестирования
- `next_steps` (Text): следующие шаги
- `related_prompts` (Relation): связанные промпты

## Experience Hub

### 9. Experience Hub (Хаб опыта и инсайтов)

**Смысл:**
Общее пространство для сбора инсайтов, лучших практик, паттернов, ошибок и "боевого опыта" — как от тебя, так и от агентов/ботов/команд. Точка синергии между проектами, ботами, личным ростом и внешними окнами.

**Поля:**
- `date` (Date): дата инсайта/события
- `source` (Select): #personal, #agent, #team, #external
- `author` (Text): кто добавил (ты, агент, внешний бот)
- `insight` (Text): суть инсайта/паттерна/ошибки
- `context` (Text): контекст (проект, задача, бот, ситуация)
- `impact` (Select): #low, #medium, #high
- `type` (Select): #insight, #pattern, #anti-pattern, #error
- `related_projects` (Text): связанные проекты/базы (если нельзя relation — перечислять)
- `related_agents` (Text): связанные агенты/боты
- `related_tasks` (Text): связанные задачи
- `related_materials` (Text): связанные материалы/гайды
- `tags` (Multi-select): #workflow, #automation, #learning, #fail, #pattern, #ai, #habit, #ritual и др.
- `implementation_note` (Text): как внедрить/применить инсайт
- `status` (Select): #raw, #reviewed, #standardized
- `last_used` (Date): когда последний раз применялось
- `success_count` (Number): сколько раз инсайт/паттерн был успешно применён
- `formula_impact_score` (Text): формула для оценки влияния (например: success_count * impact)

**Пояснения:**
- Если инсайт связан с проектом/агентом/материалом — указывай это явно.
- Формулы (например, для impact_score) пиши как текст, чтобы потом реализовать в Notion.
- Можно использовать для ретроспектив, обучения новых агентов, генерации новых идей.

**Рекомендации:**
- Не бойся фиксировать даже "сырые" инсайты — потом можно их доработать и стандартизировать.
- Используй Experience Hub как точку сборки best practices и ошибок.
- Периодически делай ревью и поднимай лучшие инсайты в стандарты (гайды, регламенты).

## Связки между базами

### Основные связи:
1. **Задачи ↔ Ритуалы ↔ Привычки** - иерархия действий
2. **Материалы ↔ Yearly Goals ↔ Skill Progress** - обучение и развитие
3. **Промпты ↔ AI Worklog ↔ Experiment Log** - AI взаимодействия
4. **Рефлексия ↔ Flow Sessions ↔ Personal KPI** - аналитика и метрики
5. **Best Practices ↔ Все базы** - обмен опытом

### Теги для связки:
- `#auto` - автоматизированные процессы
- `#fail` - неудачные попытки
- `#insight` - инсайты
- `#repeat` - повторяющиеся паттерны
- `#flow` - состояние потока
- `#energy` - уровень энергии
- `#focus` - уровень фокуса
- `#effective` - эффективные решения
- `#success` - успешные эксперименты

## 1. Habit/Skill Tracker (Трекер привычек/навыков)

**Смысл:**
Трекер привычек — это одновременно и трекер навыков, если привычки = действия для прокачки навыков. Используется для отслеживания прогресса, ретроспективы, анализа эффективности ритуалов и привычек.

**Поля:**
- `habit_name` (Text): название привычки/навыка
- `description` (Text): краткое описание, зачем эта привычка/навык
- `current_streak` (Number): текущая серия выполнений
- `total_completions` (Number): всего выполнено раз
- `skill_level` (Text): уровень навыка (можно вручную: beginner/intermediate/advanced/expert)
- `last_review` (Date): дата последней ретроспективы
- `related_rituals` (Text): с какими ритуалами связана (если нельзя сделать relation, перечислять названия)
- `insights` (Text): инсайты, которые появились в процессе
- `experiment_notes` (Text): если привычка — часть эксперимента, фиксировать гипотезу/выводы
- `tags` (Multi-select): #habit, #skill, #focus, #energy, #ritual, #experiment и др.
- `formula_streak_score` (Text): формула для вычисления "эффективности привычки" (например: current_streak * total_completions / days_tracked)
- `related_tasks` (Text): задачи, связанные с привычкой (если нельзя relation, перечислять)

**Пояснения:**
- Если привычка — это навык, не дублируй сущности.
- Если привычка входит в ритуал, указывай это явно.
- Формулы (например, для streak_score) пиши как текст, чтобы потом реализовать в Notion.
- Если есть связь с задачами, фиксируй их названия или ID в текстовом поле.

**Рекомендации:**
- Не плодить привычки ради привычек — только реально важные для роста.
- Периодически делай ретроспективу: что работает, что нет, что стоит изменить.
- Используй инсайты для пополнения Experience Hub.

## 3. Tasks/Actions (Задачи/Экшены)

**Смысл:**
База для управления задачами, экшенами, чек-листами. Используется для планирования, отслеживания прогресса, связки с привычками, ритуалами, материалами и агентами.

**Поля:**
- `task_name` (Text): название задачи/экшена
- `description` (Text): подробное описание
- `status` (Select): #todo, #in-progress, #done, #blocked, #archived
- `priority` (Select): #low, #medium, #high, #critical
- `due_date` (Date): срок выполнения
- `completed_date` (Date): дата завершения
- `related_habits` (Text): привычки, связанные с задачей (если нельзя relation — перечислять)
- `related_rituals` (Text): ритуалы, связанные с задачей
- `related_materials` (Text): материалы, которые помогут выполнить задачу
- `related_agents` (Text): агенты/боты, которые участвуют в выполнении
- `insights` (Text): инсайты, появившиеся в процессе выполнения
- `tags` (Multi-select): #habit, #ritual, #learning, #automation, #ai, #urgent и др.
- `formula_time_to_complete` (Text): формула для расчёта времени выполнения (например: completed_date - due_date)
- `experience_hub_link` (Text): если задача дала инсайт — ссылка/описание для Experience Hub

**Пояснения:**
- Если задача связана с привычкой/ритуалом — указывай это явно.
- Формулы (например, для time_to_complete) пиши как текст, чтобы потом реализовать в Notion.
- Если задача дала инсайт — фиксируй его в Experience Hub и делай ссылку/описание здесь.

**Рекомендации:**
- Не плодить задачи ради структуры — только реально важные.
- Используй теги для фильтрации и поиска.
- Инсайты и best practices — в Experience Hub.

## 5. Materials (Learning Vault)

**Смысл:**
База для хранения и трекинга всех обучающих материалов: книги, статьи, видео, курсы, подкасты, заметки. Используется для планирования обучения, связки с целями, навыками, задачами и ретроспективы.

**Поля:**
- `material_name` (Text): название материала
- `description` (Text): краткое описание/аннотация
- `type` (Select): #book, #article, #video, #course, #podcast, #note
- `difficulty` (Select): #beginner, #intermediate, #advanced
- `completion_status` (Select): #not-started, #in-progress, #completed, #abandoned
- `related_goals` (Text): цели, с которыми связан материал (если нельзя relation — перечислять)
- `skill_tags` (Multi-select): навыки, которые развивает материал
- `rating` (Number): субъективная оценка 1-5
- `key_takeaways` (Text): основные выводы/инсайты
- `action_items` (Text): что применить на практике
- `review_date` (Date): когда пересмотреть/повторить
- `related_tasks` (Text): задачи, для которых материал полезен
- `related_habits` (Text): привычки/навыки, для которых материал полезен
- `formula_learning_score` (Text): формула для оценки полезности (например: rating * #completed_links)
- `experience_hub_link` (Text): если материал дал инсайт — ссылка/описание для Experience Hub
- `tags` (Multi-select): #learning, #goal, #habit, #insight, #review, #important и др.

**Пояснения:**
- Если материал связан с целью/навыком/задачей — указывай это явно.
- Формулы (например, для learning_score) пиши как текст, чтобы потом реализовать в Notion.
- Если материал дал инсайт — фиксируй его в Experience Hub и делай ссылку/описание здесь.

**Рекомендации:**
- Не копи материалы ради галочки — только реально полезные.
- Периодически делай review и удаляй устаревшее.
- Инсайты и best practices — в Experience Hub.

## 6. Agent Prompts / AI Workflow (Промпты агентов / AI Workflow)

**Смысл:**
База для хранения, развития и анализа промптов, инструкций и паттернов работы агентов/ботов. Используется для оптимизации команд, накопления best practices, анализа эффективности и эволюции AI-агентов.

**Поля:**
- `prompt_text` (Text): текст промпта/инструкции
- `agent_name` (Text): имя агента/бота, для которого предназначен промпт
- `description` (Text): краткое описание задачи промпта
- `use_count` (Number): сколько раз использовался промпт
- `last_used` (Date): дата последнего использования
- `effectiveness` (Number): субъективная оценка эффективности 1-5
- `innovation_score` (Number): субъективная оценка новизны 1-5
- `success_rate` (Number): % успешных результатов (если считаешь вручную)
- `context` (Text): когда и для чего использовать промпт
- `improvements` (Text): идеи для улучшения промпта
- `related_tasks` (Text): задачи, для которых промпт был полезен
- `related_experiments` (Text): эксперименты, где промпт тестировался
- `tags` (Multi-select): #auto, #fail, #insight, #repeat, #effective, #pattern, #agent и др.
- `formula_success_rate` (Text): формула для расчёта success_rate (например: use_count_success / use_count)
- `experience_hub_link` (Text): если промпт дал инсайт — ссылка/описание для Experience Hub

**Пояснения:**
- Если промпт связан с задачей/экспериментом — указывай это явно.
- Формулы (например, для success_rate) пиши как текст, чтобы потом реализовать в Notion.
- Если промпт дал инсайт — фиксируй его в Experience Hub и делай ссылку/описание здесь.

**Рекомендации:**
- Не плодить промпты ради количества — только реально рабочие.
- Периодически делай ревью и улучшай промпты.
- Инсайты и best practices — в Experience Hub.

## 7. AI Worklog (Лог взаимодействий с агентами)

**Смысл:**
База для логирования всех взаимодействий с агентами/ботами: запросы, ответы, результат, инсайты, теги. Используется для ретроспективы, анализа эффективности, поиска паттернов и улучшения AI workflow.

**Поля:**
- `date` (Date): дата взаимодействия
- `agent_name` (Text): имя агента/бота
- `prompt_used` (Text): какой промпт/инструкция использовалась
- `request` (Text): твой запрос к агенту
- `response` (Text): ответ агента
- `result` (Text): результат использования (что реально произошло)
- `insight` (Text): инсайт или вывод по итогам взаимодействия
- `time_spent` (Number): время на взаимодействие (мин)
- `satisfaction` (Number): субъективная оценка 1-5
- `tags` (Multi-select): #auto, #fail, #insight, #repeat, #effective, #pattern, #agent и др.
- `related_task` (Text): задача, для которой использовался агент
- `related_experiment` (Text): эксперимент, если взаимодействие было частью эксперимента
- `formula_success` (Text): формула для оценки успешности (например: satisfaction * (result == 'успех'))
- `experience_hub_link` (Text): если взаимодействие дало инсайт — ссылка/описание для Experience Hub

**Пояснения:**
- Если взаимодействие связано с задачей/экспериментом — указывай это явно.
- Формулы (например, для success) пиши как текст, чтобы потом реализовать в Notion.
- Если взаимодействие дало инсайт — фиксируй его в Experience Hub и делай ссылку/описание здесь.

**Рекомендации:**
- Логируй не только успехи, но и фейлы — это источник инсайтов.
- Используй теги для поиска паттернов и ретроспективы.
- Инсайты и best practices — в Experience Hub.

## 10. Glossary (Термины)

**Смысл:**
База для сбора и уточнения терминов, определений, понятий, используемых в системе и проектах.

**Поля:**
- `term` (Text): термин
- `definition` (Text): определение
- `context` (Text): где и как используется
- `related_materials` (Text): материалы, где встречается термин
- `tags` (Multi-select): #ai, #workflow, #habit, #ritual, #project и др.
- `author` (Text): кто добавил термин
- `date_added` (Date): дата добавления

## 11. Guides/Regulations (Гайды/Регламенты)

**Смысл:**
База для хранения гайдов, регламентов, стандартов, best practices.

**Поля:**
- `guide_name` (Text): название гайда/регламента
- `description` (Text): краткое описание
- `content` (Text): полный текст гайда/регламента
- `related_projects` (Text): проекты, к которым относится
- `tags` (Multi-select): #workflow, #habit, #ritual, #ai, #project и др.
- `author` (Text): кто добавил
- `date_added` (Date): дата добавления
- `status` (Select): #draft, #active, #archived

## 12. Personal KPI Dashboard

**Смысл:**
База для трекинга ключевых метрик продуктивности, автоматизации, развития.

**Поля:**
- `date` (Date): дата метрики
- `task_speed` (Number): скорость выполнения задач
- `automation_percentage` (Number): % автоматизации
- `new_skills` (Number): новых навыков за период
- `innovative_actions` (Number): инновационных действий
- `flow_time` (Number): время в потоке (часы)
- `energy_avg` (Number): средняя энергия
- `focus_avg` (Number): средний фокус
- `productivity_score` (Number): общий скор продуктивности
- `notes` (Text): заметки по метрикам
- `formula_productivity_score` (Text): формула для расчёта (например: (task_speed + automation_percentage + flow_time) / 3)

## 13. Agent Evolution Log (Журнал эволюции агентов)

**Смысл:**
База для фиксации изменений, улучшений, багфиксов, новых паттернов в агентах/ботах.

**Поля:**
- `date` (Date): дата изменения
- `agent_name` (Text): имя агента/бота
- `change_type` (Select): #new-feature, #improvement, #bug-fix, #optimization
- `improvement` (Text): описание улучшения
- `patterns_standardized` (Text): стандартизированные паттерны
- `impact` (Select): #low, #medium, #high
- `testing_results` (Text): результаты тестирования
- `next_steps` (Text): следующие шаги
- `related_prompts` (Text): связанные промпты/инструкции
- `author` (Text): кто инициировал изменение 

# Notion DATABASE SCHEMAS (.life)

## yearly_goals (Year Goals)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Category            | select     | "Личное развитие"                   |
| Notes               | rich_text  | "Описание цели и шагов"             |
| Due Date            | date       | "2024-12-31"                        |
| Priority            | select     | "Высокий"                           |
| Resources Needed    | rich_text  | "Книги, курсы, ментор"              |
| Key Milestones      | rich_text  | "1. Пройти курс\n2. Сделать проект" |
| Status              | status     | "В процессе"                        |
| Progress            | number     | 40                                   |
| Why It Matters      | rich_text  | "Почему эта цель важна"             |
| Goal                | title      | "Научиться ML"                      |

## genius_list (genius_list)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Оценка Маши         | rich_text  | "10/10"                             |
| URL                 | url        | "https://example.com"               |
| Оценка Арсения      | date       | "2024-05-01"                        |
| Комментарий Арсения | rich_text  | "Отличная идея!"                    |
| Комментарий Маши    | rich_text  | "Нужно доработать"                  |
| Tags                | multi_select| "#insight, #auto"                   |
| Name                | title      | "Гениальная идея"                   |

## journal (Journal)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Tags                | multi_select| "#flow, #energy"                    |
| Выводы дня Х/П/МУ   | rich_text  | "Сегодня был продуктивный день"     |
| Оценка              | number     | 8                                   |
| Чек лист дня        | relation   | "[relation: habits]"                |
| Чек лист            | rollup     | "[rollup: habits->Выполнено]"       |
| Created             | created_time| "2024-05-01T10:00:00Z"              |
| Name                | title      | "Журнал 1 мая"                      |

## rituals (Ритуалы)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| % выполнения        | rollup     | "[rollup: habits->Выполнено]"       |
| Почему работает     | rich_text  | "Формирует привычку"                |
| Описание            | rich_text  | "Утренняя зарядка"                  |
| Гайды/Регламенты    | relation   | "[relation: guides]"                |
| Рефлексия           | relation   | "[relation: reflection]"            |
| Категория           | select     | "Здоровье"                          |
| Экшены              | relation   | "[relation: tasks]"                 |
| Микрошаг            | rich_text  | "Встать с кровати"                  |
| Важность            | number     | 5                                   |
| Сейчас в работ/ на паузе | checkbox | true                              |
| Пошаговая инструкция| rich_text  | "1. Встать\n2. Зарядка"             |
| Теги                | multi_select| "#morning, #energy"                 |
| Источник/Автор      | rich_text  | "Atomic Habits"                     |
| Треккер привычек    | relation   | "[relation: habits]"                |
| Название            | title      | "Утренняя рутина"                   |

## habits (Трекер привычек)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Выполнено           | checkbox   | true                                |
| Время дня           | select     | "Утро"                              |
| Комментарии         | rich_text  | "Было легко"                        |
| Экшены              | relation   | "[relation: tasks]"                 |
| Ритуалы             | relation   | "[relation: rituals]"               |
| Дата                | date       | "2024-05-01"                        |
| Уровень энергии     | number     | 7                                   |
| Рефлексия           | relation   | "[relation: reflection]"            |
| Настроение          | select     | "Отлично"                           |
| Длительность        | number     | 30                                  |
| Привычка            | title      | "Медитация"                         |

## reflection (Рефлексия)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Ритуалы             | relation   | "[relation: rituals]"               |
| Гайды/Регламенты    | relation   | "[relation: guides]"                |
| Дата                | date       | "2024-05-01"                        |
| Настроение          | select     | "Вдохновлён"                        |
| Уровень энергии     | number     | 6                                   |
| Треккер привычек    | relation   | "[relation: habits]"                |
| Что удалось         | rich_text  | "Выполнил все задачи"               |
| Теги                | multi_select| "#focus, #retro"                    |
| Сложность           | rich_text  | "Было сложно начать"                |
| Урок/Вывод          | rich_text  | "Нужно планировать заранее"         |
| Микрошаг            | rich_text  | "Поставить будильник"               |
| Событие             | title      | "Рефлексия 1 мая"                   |

## guides (Гайды/Регламенты)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Последнее обновление| date       | "2024-04-30"                        |
| Описание            | rich_text  | "Как делать утренние ритуалы"       |
| Ритуалы             | relation   | "[relation: rituals]"               |
| Чеклист внутри      | checkbox   | true                                |
| Тип гайда           | multi_select| "#routine, #howto"                  |
| Теги                | multi_select| "#guide, #energy"                   |
| Рефлексия           | relation   | "[relation: reflection]"            |
| Авторы/внедрившие   | rich_text  | "Иван, Мария"                       |
| Сложность           | select     | "Средняя"                           |
| Формат              | multi_select| "#text, #video"                     |
| Канал применения    | multi_select| "#morning, #work"                   |
| Дата добавления     | date       | "2024-04-01"                        |
| Name                | title      | "Гайд по утру"                      |

## tasks (Экшены/Задачи)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Статус              | status     | "В процессе"                        |
| Категория           | select     | "Личное"                            |
| Приоритет           | select     | "Высокий"                           |
| Дедлайн             | date       | "2024-05-10"                        |
| Шаблон таблицы материалов | relation | "[relation: materials]"           |
| Теги                | multi_select| "#urgent, #auto"                    |
| Дата старта         | date       | "2024-05-01"                        |
| Трекер привычек     | relation   | "[relation: habits]"                |
| Результат           | rich_text  | "Завершено успешно"                 |
| Ритуалы             | relation   | "[relation: rituals]"               |
| Описание            | rich_text  | "Описание задачи"                   |
| Задача              | title      | "Сделать отчёт"                     |

## terms (Термины)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Оценка/ROI          | rich_text  | "Высокий"                           |
| Тема / Теги         | rich_text  | "#ai, #growth"                      |
| Статус              | rich_text  | "В работе"                          |
| Формулировка карточки RemNote | rich_text | "Что такое ROI?"              |
| Определение         | rich_text  | "Return on Investment"              |
| Формат              | select     | "Термин"                            |
| План применения     | rich_text  | "Использовать в проекте"            |
| Категория           | select     | "Финансы"                           |
| Дата добавления     | date       | "2024-05-01"                        |
| Name                | title      | "ROI"                               |

## materials (Материалы)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Инсайт/Заметка      | rich_text  | "Важная мысль"                      |
| Архив               | checkbox   | false                               |
| Категория           | select     | "Книга"                             |
| Ссылка/Файл         | url        | "https://book.com"                  |
| Оценка/ROI          | rich_text  | "8/10"                              |
| Статус              | status     | "Прочитано"                         |
| Формат              | select     | "PDF"                               |
| Связанные люди/Команда | rich_text| "Иван, команда"                     |
| План применения/Проект | rich_text| "Внедрить в задачу X"               |
| Рейтинг/Полезность  | number     | 9                                   |
| Автор/Источник      | rich_text  | "Автор книги"                       |
| Дата внедрения      | date       | "2024-05-01"                        |
| Дата добавления     | created_time| "2024-04-30T12:00:00Z"              |
| Теги                | multi_select| "#book, #learning"                  |
| Применено в задачах | relation   | "[relation: tasks]"                 |
| Презентация/Кейс    | url        | "https://presentation.com"          |
| Название            | title      | "Книга по ML"                       |

## agent_prompts (Промты агентов)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Статус              | select     | "Активен"                           |
| Версия              | number     | 2                                   |
| Промпт              | rich_text  | "Сделай X"                          |
| Дата создания       | date       | "2024-05-01"                        |
| Роль                | select     | "Ассистент"                         |
| Миссия              | rich_text  | "Помогать с задачами"               |
| Последнее обновление| date       | "2024-05-02"                        |
| Name                | title      | "Промпт для задач"                  |

## ideas (База идей)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Name                | title      | "Идея: автоматизация"               |

## experience_hub (Experience Hub)
| Property            | Type       | Example/Test Value/Formula/Relation |
|---------------------|------------|-------------------------------------|
| Name                | title      | "Best Practice: Review Weekly"      |

---

**Для всех relation/rollup/формул — вписан пример строки/описание, чтобы можно было быстро внедрить вручную в Notion. Используй этот файл как эталон для автоматизации, интеграций и оптимизации.** 