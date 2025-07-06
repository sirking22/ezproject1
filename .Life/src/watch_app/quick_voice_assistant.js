/**
 * Quick Voice Assistant для Xiaomi Watch S
 * Максимально быстрый доступ к LLM и базе данных через голос
 */

class QuickVoiceAssistant {
    constructor() {
        this.isRecording = false;
        this.isActive = false;
        this.lastQuery = null;
        this.communication = new Communication();

        // Настройки
        this.config = {
            autoRecordOnWake: true,      // Автозапись при пробуждении экрана
            gestureActivation: true,     // Активация жестами
            voiceActivation: true,       // Активация голосом
            quickMode: true,             // Быстрый режим без UI
            responseTimeout: 10000,      // 10 секунд на ответ
            retryAttempts: 2             // Попытки повтора
        };

        // Состояние
        this.state = {
            screenActive: false,
            lastActivity: null,
            queryHistory: [],
            responseCache: {}
        };

        this.initialize();
    }

    async initialize() {
        console.log('🚀 Инициализация Quick Voice Assistant...');

        // Настройка активации
        this.setupWakeDetection();
        this.setupGestureActivation();
        this.setupVoiceActivation();

        // Тест связи
        await this.testConnection();

        console.log('✅ Quick Voice Assistant готов к работе');
    }

    setupWakeDetection() {
        // Активация при пробуждении экрана
        if (this.config.autoRecordOnWake) {
            // Слушаем события пробуждения экрана
            this.onScreenWake = () => {
                console.log('📱 Экран пробудился - готов к записи');
                this.state.screenActive = true;
                this.showReadyIndicator();

                // Автоматически начинаем слушать через 1 секунду
                setTimeout(() => {
                    if (this.state.screenActive && !this.isRecording) {
                        this.startQuickRecording();
                    }
                }, 1000);
            };

            this.onScreenSleep = () => {
                console.log('😴 Экран уснул');
                this.state.screenActive = false;
                this.stopRecording();
            };
        }
    }

    setupGestureActivation() {
        if (this.config.gestureActivation) {
            // Жесты для активации
            this.gestures = {
                'shake': () => this.activateRecording(),
                'double_tap': () => this.activateRecording(),
                'long_press': () => this.showQuickMenu(),
                'swipe_up': () => this.repeatLastQuery()
            };
        }
    }

    setupVoiceActivation() {
        if (this.config.voiceActivation) {
            // Ключевые слова для активации
            this.wakeWords = [
                'ассистент',
                'помощь',
                'вопрос',
                'задача',
                'мысль',
                'идея'
            ];
        }
    }

    async testConnection() {
        try {
            const response = await this.communication.ping();
            console.log('✅ Связь с сервером установлена');
            return true;
        } catch (error) {
            console.error('❌ Ошибка связи с сервером:', error);
            return false;
        }
    }

    activateRecording() {
        console.log('🎤 Активация записи...');

        if (this.isRecording) {
            this.stopRecording();
            return;
        }

        this.startQuickRecording();
    }

    async startQuickRecording() {
        if (this.isRecording) return;

        this.isRecording = true;
        console.log('🎤 Начало записи голоса...');

        // Показываем индикатор записи
        this.showRecordingIndicator();

        try {
            // Запись голоса (3-10 секунд)
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
        // Симуляция записи голоса
        return new Promise((resolve) => {
            setTimeout(() => {
                // Моковые данные для демонстрации
                resolve('mock_audio_data');
            }, 3000);
        });
    }

    async speechToText(audioData) {
        // Симуляция распознавания речи
        const mockTexts = [
            'добавь задачу медитация',
            'как мое здоровье',
            'покажи прогресс',
            'запиши мысль о проекте',
            'что мне делать сегодня',
            'найди информацию о Python',
            'создай привычку чтение'
        ];

        return mockTexts[Math.floor(Math.random() * mockTexts.length)];
    }

    async processQuery(text) {
        console.log('🧠 Обработка запроса:', text);

        // Сохраняем в историю
        this.state.queryHistory.push({
            text: text,
            timestamp: Date.now()
        });

        this.lastQuery = text;

        // Показываем индикатор обработки
        this.showProcessingIndicator();

        try {
            // Отправляем в LLM
            const response = await this.communication.sendToLLM(text);

            if (response) {
                console.log('🤖 Ответ LLM:', response);

                // Показываем ответ
                this.showResponse(response);

                // Кэшируем ответ
                this.state.responseCache[text] = response;

                // Автоматически выполняем действия если нужно
                await this.executeActions(text, response);

            } else {
                this.showError('Нет ответа от LLM');
            }

        } catch (error) {
            console.error('❌ Ошибка обработки:', error);
            this.showError('Ошибка обработки запроса');
        }
    }

    async executeActions(query, response) {
        // Автоматическое выполнение действий на основе запроса

        if (query.includes('добавь задачу') || query.includes('создай задачу')) {
            await this.addTask(query);
        }

        if (query.includes('запиши мысль') || query.includes('сохрани идею')) {
            await this.saveThought(query);
        }

        if (query.includes('создай привычку')) {
            await this.createHabit(query);
        }

        if (query.includes('покажи прогресс') || query.includes('статистика')) {
            await this.showProgress();
        }
    }

    async addTask(query) {
        try {
            const taskText = query.replace(/добавь задачу|создай задачу/i, '').trim();
            await this.communication.sendToNotion('tasks', {
                title: taskText,
                type: 'task',
                source: 'watch_voice'
            });
            console.log('✅ Задача добавлена:', taskText);
        } catch (error) {
            console.error('❌ Ошибка добавления задачи:', error);
        }
    }

    async saveThought(query) {
        try {
            const thoughtText = query.replace(/запиши мысль|сохрани идею/i, '').trim();
            await this.communication.sendToNotion('reflections', {
                content: thoughtText,
                type: 'thought',
                source: 'watch_voice'
            });
            console.log('✅ Мысль сохранена:', thoughtText);
        } catch (error) {
            console.error('❌ Ошибка сохранения мысли:', error);
        }
    }

    async createHabit(query) {
        try {
            const habitText = query.replace(/создай привычку/i, '').trim();
            await this.communication.sendToNotion('habits', {
                title: habitText,
                type: 'habit',
                source: 'watch_voice'
            });
            console.log('✅ Привычка создана:', habitText);
        } catch (error) {
            console.error('❌ Ошибка создания привычки:', error);
        }
    }

    async showProgress() {
        try {
            const progress = await this.communication.getProgress();
            console.log('📊 Прогресс:', progress);
            this.showResponse(`Прогресс: ${progress.summary}`);
        } catch (error) {
            console.error('❌ Ошибка получения прогресса:', error);
        }
    }

    stopRecording() {
        this.isRecording = false;
        console.log('🛑 Запись остановлена');
        this.hideRecordingIndicator();
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
    }

    // UI индикаторы (упрощенные)
    showReadyIndicator() {
        console.log('📱 Готов к записи');
        // Показываем зеленый индикатор на экране
    }

    showRecordingIndicator() {
        console.log('🔴 Запись...');
        // Показываем красный индикатор записи
    }

    showProcessingIndicator() {
        console.log('🔄 Обработка...');
        // Показываем индикатор обработки
    }

    showResponse(response) {
        console.log('🤖 Ответ:', response);
        // Показываем ответ на экране (кратко)
        // Полный ответ отправляем в Telegram
    }

    showError(message) {
        console.log('❌ Ошибка:', message);
        // Показываем ошибку на экране
    }

    hideRecordingIndicator() {
        console.log('📱 Индикатор скрыт');
        // Скрываем индикатор записи
    }
}

class Communication {
    constructor() {
        this.serverUrl = 'http://localhost:8000';
        this.telegramUrl = 'http://localhost:3000';
    }

    async ping() {
        const response = await fetch(`${this.serverUrl}/ping`);
        return response.ok;
    }

    async sendToLLM(query) {
        try {
            const response = await fetch(`${this.serverUrl}/llm/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    context: 'watch_voice',
                    timestamp: Date.now()
                })
            });

            const result = await response.json();
            return result.response;

        } catch (error) {
            console.error('Ошибка отправки в LLM:', error);
            throw error;
        }
    }

    async sendToNotion(database, data) {
        try {
            const response = await fetch(`${this.serverUrl}/notion/${database}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            return await response.json();

        } catch (error) {
            console.error('Ошибка отправки в Notion:', error);
            throw error;
        }
    }

    async getProgress() {
        try {
            const response = await fetch(`${this.serverUrl}/progress`);
            return await response.json();
        } catch (error) {
            console.error('Ошибка получения прогресса:', error);
            throw error;
        }
    }

    async sendToTelegram(message) {
        try {
            const response = await fetch(`${this.telegramUrl}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    source: 'watch_voice'
                })
            });

            return await response.json();

        } catch (error) {
            console.error('Ошибка отправки в Telegram:', error);
            throw error;
        }
    }
}

// Запуск приложения
const assistant = new QuickVoiceAssistant();

// Экспорт для использования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QuickVoiceAssistant };
} 