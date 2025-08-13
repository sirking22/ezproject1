## Автоподгрузка `.env` в PowerShell

Контекст: при прямых вызовах API из PowerShell текущий процесс не видит переменные из файлов `.env`, пока они не импортированы. Для устранения класса ошибок добавлен универсальный загрузчик и инициализация в профиле.

### Что сделано
- Скрипт `tools/Import-DotEnv.ps1` — безопасно загружает пары `KEY=VALUE` в переменные текущего процесса.
- Рекомендованная инициализация в профиле PowerShell:

```powershell
# В профиль пользователя ($PROFILE) добавить блок
try {
	$dotenv = Join-Path $PSScriptRoot '..\\..\\tools\\Import-DotEnv.ps1' | Resolve-Path -ErrorAction SilentlyContinue
	if (-not $dotenv) {
		# fallback: относительный путь от текущей директории
		$dotenv = Join-Path (Get-Location) 'tools\\Import-DotEnv.ps1'
	}
	if (Test-Path $dotenv) {
		. $dotenv
		if (Test-Path .\\.env) { Import-DotEnv -Path .\\.env -Quiet }
	}
} catch {}
```

Открывать новые окна PowerShell в корне проекта: `.env` будет импортирован.

### Проверка
```powershell
iwr https://api.github.com/user -Headers @{Authorization="Bearer $env:GITHUB_TOKEN"; 'User-Agent'='diag'} -UseBasicParsing
```

### Замечания безопасности
- Скрипт импортирует в уровень процесса, НЕ в реестр.
- Значения не логируются, токены не печатаются.
