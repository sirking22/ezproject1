/**
 * Xiaomi Watch S App - Quick Voice Assistant
 * Минималистичное приложение для быстрого голосового доступа к LLM
 */

class XiaomiWatchApp {
    constructor() {
        this.currentState = 'ready';
        this.isRecording = false;
        this.lastQuery = null;
        this.serverUrl = 'http://192.168.1.100:8000'; // IP твоего компьютера

        // Настройки
        this.config = {
            autoRecordOnWake: true,
            recordTimeout: 10000, // 10 секунд
            retryAttempts: 2,
            wakeWords: ['ассистент', 'помощь', 'вопрос', 'задача', 'мысль']
        };

        this.initialize();
    }

    async initialize() {
        console.log('🚀 Инициализация Xiaomi Watch App...');

        // Настройка экранов
        this.setupScreens();

        // Настройка жестов
        this.setupGestures();

        // Настройка активации
        this.setupWakeDetection();

        // Показ главного экрана
        this.showMainScreen();

        console.log('✅ Xiaomi Watch App готов к работе');
    }

    setupScreens() {
        // Главный экран - готов к записи
        this.screens = {
            main: {
                title: '🎤 Готов',
                message: 'Подними руку\nи говори',
                button1: '●',
                button2: 'Меню',
                color: 'green'
            },
            recording: {
                title: '🔴 Запись',
                message: 'Говорите...',
                button1: '●',
                button2: 'Стоп',
                color: 'red',
                animation: 'wave'
            },
            processing: {
                title: '🔄 Обработка',
                message: 'Анализирую...',
                button1: '●',
                button2: 'Отмена',
                color: 'blue'
            },
            response: {
                title: '✅ Готово',
                message: '',
                button1: 'Повтор',
                button2: 'Новое',
                color: 'green'
            },
            error: {
                title: '❌ Ошибка',
                message: '',
                button1: 'Повтор',
                button2: 'Отмена',
                color: 'red'
            }
        };
    }

    setupGestures() {
        // Жесты для активации записи
        this.gestures = {
            'shake': () => this.activateRecording(),
            'double_tap': () => this.activateRecording(),
            'long_press': () => this.showQuickMenu(),
            'swipe_up': () => this.repeatLastQuery()
        };

        // Настройка обработчиков жестов
        this.setupGestureHandlers();
    }

    setupGestureHandlers() {
        // Обработчики жестов для Xiaomi Watch S
        if (typeof device !== 'undefined') {
            // Встряхивание
            device.addEventListener('shake', () => {
                console.log('👆 Жест: встряхивание');
                this.activateRecording();
            });

            // Двойное касание экрана
            device.addEventListener('doubletap', () => {
                console.log('👆 Жест: двойное касание');
                this.activateRecording();
            });

            // Долгое нажатие
            device.addEventListener('longpress', () => {
                console.log('👆 Жест: долгое нажатие');
                this.showQuickMenu();
            });

            // Свайп вверх
            device.addEventListener('swipeup', () => {
                console.log('👆 Жест: свайп вверх');
                this.repeatLastQuery();
            });
        }
    }

    setupWakeDetection() {
        // Активация при пробуждении экрана
        if (this.config.autoRecordOnWake) {
            if (typeof device !== 'undefined') {
                device.addEventListener('screenwake', () => {
                    console.log('📱 Экран пробудился');
                    this.onScreenWake();
                });

                device.addEventListener('screensleep', () => {
                    console.log('😴 Экран уснул');
                    this.onScreenSleep();
                });
            }
        }
    }

    onScreenWake() {
        this.currentState = 'ready';
        this.showMainScreen();

        // Автоматически готов к записи через 1 секунду
        setTimeout(() => {
            if (this.currentState === 'ready' && !this.isRecording) {
                console.log('⏱️ Автоматически готов к записи');
                this.showReadyIndicator();
            }
        }, 1000);
    }

    onScreenSleep() {
        this.stopRecording();
        this.currentState = 'sleep';
    }

    showMainScreen() {
        const screen = this.screens.main;
        this.renderScreen(screen);
    }

    showReadyIndicator() {
        // Показываем зеленый индикатор готовности
        this.updateScreen({
            title: '🎤 Готов',
            message: 'Говорите...',
            color: 'green',
            indicator: 'pulse'
        });
    }

    activateRecording() {
        if (this.isRecording) {
            this.stopRecording();
            return;
        }

        console.log('🎤 Активация записи...');
        this.startRecording();
    }

    async startRecording() {
        if (this.isRecording) return;

        this.isRecording = true;
        this.currentState = 'recording';

        console.log('🎤 Начало записи голоса...');

        // Показываем экран записи
        this.showRecordingScreen();

        try {
            // Запись голоса
            const audioData = await this.recordVoice();

            if (audioData) {
                // Преобразование в текст
                const text = await this.speechToText(audioData);

                if (text && text.trim()) {
                    console.log('📝 Распознано:', text);
                    await this.processQuery(text);
                } else {
                    console.log('❌ Не удалось распознать речь');
                    this.showError('Не удалось распознать речь');
                }
            }

        } catch (error) {
            console.error('❌ Ошибка записи:', error);
            this.showError('Ошибка записи');
        } finally {
            this.stopRecording();
        }
    }

    async recordVoice() {
        return new Promise((resolve) => {
            // Симуляция записи голоса для Xiaomi Watch S
            console.log('🎙️ Запись голоса...');

            // Таймаут записи
            const timeout = setTimeout(() => {
                console.log('⏱️ Таймаут записи');
                resolve(null);
            }, this.config.recordTimeout);

            // Симуляция успешной записи через 3-5 секунд
            const recordTime = Math.random() * 2000 + 3000; // 3-5 секунд
            setTimeout(() => {
                clearTimeout(timeout);
                console.log('✅ Запись завершена');
                resolve('mock_audio_data');
            }, recordTime);
        });
    }

    async speechToText(audioData) {
        // Симуляция распознавания речи
        console.log('🔄 Преобразование речи в текст...');

        const mockTexts = [
            'добавь задачу медитация',
            'запиши мысль о проекте',
            'покажи прогресс',
            'создай привычку чтение',
            'как мое здоровье',
            'что мне делать сегодня',
            'найди информацию о Python',
            'синхронизируй данные'
        ];

        // Имитация времени обработки
        await new Promise(resolve => setTimeout(resolve, 1000));

        return mockTexts[Math.floor(Math.random() * mockTexts.length)];
    }

    async processQuery(text) {
        console.log('🧠 Обработка запроса:', text);

        this.lastQuery = text;
        this.currentState = 'processing';

        // Показываем экран обработки
        this.showProcessingScreen();

        try {
            // Отправляем в LLM
            const response = await this.sendToLLM(text);

            if (response) {
                console.log('🤖 Ответ LLM:', response);
                this.showResponse(response);
            } else {
                this.showError('Нет ответа от LLM');
            }

        } catch (error) {
            console.error('❌ Ошибка обработки:', error);
            this.showError('Ошибка обработки запроса');
        }
    }

    async sendToLLM(query) {
        try {
            console.log('📡 Отправка в LLM...');

            const response = await fetch(`${this.serverUrl}/watch/voice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    context: 'watch_voice',
                    timestamp: Date.now()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            return result.response;

        } catch (error) {
            console.error('❌ Ошибка отправки в LLM:', error);

            // Fallback: локальная обработка простых команд
            return this.processLocally(query);
        }
    }

    processLocally(query) {
        // Локальная обработка простых команд без сервера
        const commands = {
            'добавь задачу': 'Задача добавлена локально',
            'запиши мысль': 'Мысль сохранена локально',
            'покажи прогресс': 'Прогресс: данные недоступны',
            'синхронизируй': 'Синхронизация: сервер недоступен'
        };

        for (const [key, response] of Object.entries(commands)) {
            if (query.toLowerCase().includes(key)) {
                return response;
            }
        }

        return 'Команда обработана локально. Сервер недоступен.';
    }

    showRecordingScreen() {
        const screen = this.screens.recording;
        this.renderScreen(screen);
    }

    showProcessingScreen() {
        const screen = this.screens.processing;
        this.renderScreen(screen);
    }

    showResponse(response) {
        this.currentState = 'response';

        // Краткий ответ для экрана часов
        const shortResponse = this.getShortResponse(response);

        const screen = {
            ...this.screens.response,
            message: shortResponse
        };

        this.renderScreen(screen);

        // Полный ответ отправляем в Telegram
        this.sendToTelegram(response);
    }

    getShortResponse(response) {
        // Сокращаем ответ для экрана часов
        if (response.includes('добавлена')) return 'Задача добавлена';
        if (response.includes('сохранена')) return 'Мысль сохранена';
        if (response.includes('создана')) return 'Привычка создана';
        if (response.includes('прогресс')) return 'Прогресс готов';
        if (response.includes('синхронизация')) return 'Синхронизировано';

        return response.substring(0, 20) + '...';
    }

    async sendToTelegram(message) {
        try {
            await fetch(`${this.serverUrl}/telegram/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `🎤 Голосовой запрос: ${this.lastQuery}\n\n${message}`,
                    source: 'watch_voice'
                })
            });

            console.log('📱 Отправлено в Telegram');
        } catch (error) {
            console.error('❌ Ошибка отправки в Telegram:', error);
        }
    }

    showError(message) {
        this.currentState = 'error';

        const screen = {
            ...this.screens.error,
            message: message
        };

        this.renderScreen(screen);
    }

    stopRecording() {
        this.isRecording = false;
        console.log('🛑 Запись остановлена');

        if (this.currentState === 'recording') {
            this.currentState = 'ready';
            this.showMainScreen();
        }
    }

    repeatLastQuery() {
        if (this.lastQuery) {
            console.log('🔄 Повтор последнего запроса:', this.lastQuery);
            this.processQuery(this.lastQuery);
        } else {
            this.showError('Нет последнего запроса');
        }
    }

    showQuickMenu() {
        console.log('⚡ Быстрое меню:');
        console.log('  🎤 - Новая запись');
        console.log('  🔄 - Повторить');
        console.log('  📊 - Прогресс');
        console.log('  ⚙️ - Настройки');

        // Показываем меню на экране
        this.renderScreen({
            title: '⚡ Меню',
            message: '🎤 Новая запись\n🔄 Повторить\n📊 Прогресс\n⚙️ Настройки',
            button1: 'Выбор',
            button2: 'Отмена',
            color: 'blue'
        });
    }

    renderScreen(screen) {
        // Отрисовка экрана на Xiaomi Watch S
        console.log(`📱 ЭКРАН: ${screen.title}`);
        console.log(`   Сообщение: ${screen.message}`);
        console.log(`   Кнопки: [${screen.button1}] [${screen.button2}]`);
        console.log(`   Цвет: ${screen.color}`);

        // Здесь будет реальная отрисовка на экране часов
        this.updateDisplay(screen);
    }

    updateDisplay(screen) {
        // Обновление дисплея часов
        if (typeof device !== 'undefined' && device.display) {
            device.display.update({
                title: screen.title,
                message: screen.message,
                button1: screen.button1,
                button2: screen.button2,
                color: screen.color,
                animation: screen.animation
            });
        }
    }

    updateScreen(updates) {
        // Обновление текущего экрана
        const currentScreen = this.screens[this.currentState];
        const updatedScreen = { ...currentScreen, ...updates };
        this.renderScreen(updatedScreen);
    }
}

// Инициализация приложения
const watchApp = new XiaomiWatchApp();

// Обработчики кнопок
function onButton1Press() {
    console.log('🔘 Кнопка 1 нажата');

    switch (watchApp.currentState) {
        case 'ready':
            watchApp.activateRecording();
            break;
        case 'recording':
            watchApp.stopRecording();
            break;
        case 'processing':
            watchApp.stopRecording();
            break;
        case 'response':
            watchApp.repeatLastQuery();
            break;
        case 'error':
            watchApp.repeatLastQuery();
            break;
    }
}

function onButton2Press() {
    console.log('🔘 Кнопка 2 нажата');

    switch (watchApp.currentState) {
        case 'ready':
            watchApp.showQuickMenu();
            break;
        case 'recording':
            watchApp.stopRecording();
            break;
        case 'processing':
            watchApp.stopRecording();
            break;
        case 'response':
            watchApp.activateRecording();
            break;
        case 'error':
            watchApp.showMainScreen();
            break;
    }
}

// Экспорт для использования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { XiaomiWatchApp };
} 