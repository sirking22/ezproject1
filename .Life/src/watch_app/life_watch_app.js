/**
 * Life Watch App для Xiaomi Watch S
 * Персональный AI-ассистент для здоровья и продуктивности
 */

class LifeWatchApp {
    constructor() {
        this.sensors = new Sensors();
        this.communication = new Communication();
        this.ui = new UserInterface();
        this.dataManager = new DataManager();
        this.voiceProcessor = new VoiceProcessor();

        // Состояние приложения
        this.currentScreen = 'main';
        this.isMonitoring = false;
        this.lastSync = null;

        // Конфигурация
        this.config = {
            syncInterval: 30000,        // 30 секунд
            heartRateInterval: 300000,  // 5 минут
            activityInterval: 3600000,  // 1 час
            voiceEnabled: true,
            notificationsEnabled: true,
            heartRateThreshold: 100,
            stepsGoal: 10000,
            caloriesGoal: 500
        };
    }

    async initialize() {
        console.log('🚀 Инициализация Life Watch App...');

        try {
            // Инициализация компонентов
            await this.sensors.initialize();
            await this.communication.initialize();
            await this.ui.initialize();
            await this.dataManager.initialize();

            if (this.config.voiceEnabled) {
                await this.voiceProcessor.initialize();
            }

            // Создание главного экрана
            this.createMainScreen();

            // Настройка жестов
            this.setupGestures();

            // Запуск мониторинга
            this.startMonitoring();

            console.log('✅ Life Watch App инициализирован');

        } catch (error) {
            console.error('❌ Ошибка инициализации:', error);
        }
    }

    createMainScreen() {
        // Главный экран с основной информацией
        this.ui.createScreen('main', {
            title: 'Life Watch',
            layout: 'vertical',
            elements: [
                {
                    type: 'header',
                    text: '🏥 Здоровье',
                    style: { fontSize: 18, fontWeight: 'bold', color: '#4CAF50' }
                },
                {
                    type: 'metric',
                    id: 'heart_rate',
                    label: 'Пульс',
                    value: '--',
                    unit: 'уд/мин',
                    icon: '❤️',
                    style: { color: '#FF5722' }
                },
                {
                    type: 'metric',
                    id: 'stress_level',
                    label: 'Стресс',
                    value: '--',
                    unit: '%',
                    icon: '😰',
                    style: { color: '#FF9800' }
                },
                {
                    type: 'divider'
                },
                {
                    type: 'header',
                    text: '📊 Активность',
                    style: { fontSize: 18, fontWeight: 'bold', color: '#2196F3' }
                },
                {
                    type: 'metric',
                    id: 'steps',
                    label: 'Шаги',
                    value: '--',
                    unit: '',
                    icon: '👟',
                    style: { color: '#4CAF50' }
                },
                {
                    type: 'metric',
                    id: 'calories',
                    label: 'Калории',
                    value: '--',
                    unit: 'ккал',
                    icon: '🔥',
                    style: { color: '#FF5722' }
                },
                {
                    type: 'divider'
                },
                {
                    type: 'button',
                    id: 'voice_command',
                    text: '🎤 Голосовая команда',
                    action: () => this.startVoiceCommand(),
                    style: { backgroundColor: '#9C27B0', color: 'white' }
                },
                {
                    type: 'button',
                    id: 'sync_now',
                    text: '🔄 Синхронизация',
                    action: () => this.syncData(),
                    style: { backgroundColor: '#607D8B', color: 'white' }
                }
            ]
        });

        // Экран голосовых команд
        this.ui.createScreen('voice', {
            title: '🎤 Голосовая команда',
            layout: 'center',
            elements: [
                {
                    type: 'text',
                    text: 'Говорите...',
                    style: { fontSize: 20, textAlign: 'center' }
                },
                {
                    type: 'animation',
                    id: 'voice_wave',
                    type: 'wave',
                    style: { height: 60 }
                },
                {
                    type: 'button',
                    id: 'stop_voice',
                    text: 'Остановить',
                    action: () => this.stopVoiceCommand(),
                    style: { backgroundColor: '#F44336', color: 'white' }
                }
            ]
        });

        // Экран уведомлений
        this.ui.createScreen('notifications', {
            title: '🔔 Уведомления',
            layout: 'list',
            elements: []
        });

        // Экран настроек
        this.ui.createScreen('settings', {
            title: '⚙️ Настройки',
            layout: 'list',
            elements: [
                {
                    type: 'toggle',
                    id: 'voice_enabled',
                    label: 'Голосовые команды',
                    value: this.config.voiceEnabled,
                    action: (value) => this.toggleVoice(value)
                },
                {
                    type: 'toggle',
                    id: 'notifications_enabled',
                    label: 'Уведомления',
                    value: this.config.notificationsEnabled,
                    action: (value) => this.toggleNotifications(value)
                },
                {
                    type: 'slider',
                    id: 'heart_rate_threshold',
                    label: 'Порог пульса',
                    value: this.config.heartRateThreshold,
                    min: 60,
                    max: 150,
                    action: (value) => this.updateHeartRateThreshold(value)
                },
                {
                    type: 'slider',
                    id: 'steps_goal',
                    label: 'Цель по шагам',
                    value: this.config.stepsGoal,
                    min: 5000,
                    max: 20000,
                    step: 1000,
                    action: (value) => this.updateStepsGoal(value)
                }
            ]
        });
    }

    setupGestures() {
        // Настройка жестов управления
        this.ui.setupGestures({
            'swipe_up': () => this.showScreen('notifications'),
            'swipe_down': () => this.showScreen('settings'),
            'swipe_left': () => this.showProgress(),
            'swipe_right': () => this.startVoiceCommand(),
            'double_tap': () => this.emergencyHelp(),
            'long_press': () => this.showQuickActions()
        });
    }

    async startMonitoring() {
        if (this.isMonitoring) return;

        this.isMonitoring = true;
        console.log('📊 Запуск мониторинга...');

        // Мониторинг пульса
        setInterval(async () => {
            try {
                const heartRate = await this.sensors.getHeartRate();
                this.updateMetric('heart_rate', heartRate);

                // Проверка порога стресса
                if (heartRate > this.config.heartRateThreshold) {
                    this.showStressAlert(heartRate);
                }

                // Отправка данных на сервер
                await this.communication.sendData('heart_rate', {
                    heartRate: heartRate,
                    timestamp: Date.now(),
                    quality: 'good'
                });

            } catch (error) {
                console.error('Ошибка мониторинга пульса:', error);
            }
        }, this.config.heartRateInterval);

        // Мониторинг активности
        setInterval(async () => {
            try {
                const activity = await this.sensors.getActivityData();
                this.updateMetric('steps', activity.steps);
                this.updateMetric('calories', activity.calories);

                // Проверка целей
                this.checkActivityGoals(activity);

                // Отправка данных на сервер
                await this.communication.sendData('activity', {
                    steps: activity.steps,
                    calories: activity.calories,
                    distance: activity.distance,
                    activeMinutes: activity.activeMinutes,
                    timestamp: Date.now()
                });

            } catch (error) {
                console.error('Ошибка мониторинга активности:', error);
            }
        }, this.config.activityInterval);

        // Синхронизация с сервером
        setInterval(async () => {
            await this.syncData();
        }, this.config.syncInterval);
    }

    async startVoiceCommand() {
        if (!this.config.voiceEnabled) {
            this.showNotification('Голосовые команды отключены');
            return;
        }

        this.showScreen('voice');

        try {
            const command = await this.voiceProcessor.startRecording();
            if (command) {
                await this.processVoiceCommand(command);
            }
        } catch (error) {
            console.error('Ошибка голосовой команды:', error);
            this.showNotification('Ошибка распознавания речи');
        }

        this.showScreen('main');
    }

    async processVoiceCommand(command) {
        console.log('🎤 Обработка команды:', command);

        // Получение текущих биометрических данных
        const biometrics = await this.getCurrentBiometrics();

        // Отправка команды на сервер для обработки LLM
        try {
            const response = await this.communication.sendVoiceCommand(command, biometrics);
            this.showNotification(response);
        } catch (error) {
            console.error('Ошибка обработки команды:', error);
            this.showNotification('Ошибка обработки команды');
        }
    }

    async getCurrentBiometrics() {
        const heartRate = await this.sensors.getHeartRate();
        const activity = await this.sensors.getActivityData();
        const stressLevel = this.calculateStressLevel(heartRate);

        return {
            heartRate: heartRate,
            stressLevel: stressLevel,
            steps: activity.steps,
            calories: activity.calories,
            timestamp: Date.now()
        };
    }

    calculateStressLevel(heartRate) {
        if (heartRate > 100) return 80;
        if (heartRate > 85) return 60;
        if (heartRate > 70) return 30;
        return 10;
    }

    updateMetric(id, value) {
        this.ui.updateElement(id, { value: value });

        // Обновление в локальном хранилище
        this.dataManager.saveMetric(id, value);
    }

    showStressAlert(heartRate) {
        const notification = {
            type: 'alert',
            title: '🚨 Высокий пульс',
            message: `Пульс: ${heartRate} уд/мин. Рекомендуется отдых.`,
            actions: [
                { text: 'Медитация', action: () => this.startMeditation() },
                { text: 'Дыхание', action: () => this.startBreathing() },
                { text: 'Игнорировать', action: () => { } }
            ]
        };

        this.showNotification(notification);
    }

    checkActivityGoals(activity) {
        if (activity.steps >= this.config.stepsGoal) {
            this.showNotification({
                type: 'success',
                title: '🎉 Цель достигнута!',
                message: `Вы прошли ${activity.steps} шагов!`
            });
        }

        if (activity.calories >= this.config.caloriesGoal) {
            this.showNotification({
                type: 'success',
                title: '🔥 Калории сожжены!',
                message: `Вы сожгли ${activity.calories} калорий!`
            });
        }
    }

    async syncData() {
        try {
            const data = this.dataManager.getAllData();
            await this.communication.syncData(data);
            this.lastSync = Date.now();

            this.showNotification('✅ Данные синхронизированы');
        } catch (error) {
            console.error('Ошибка синхронизации:', error);
            this.showNotification('❌ Ошибка синхронизации');
        }
    }

    showScreen(screenName) {
        this.currentScreen = screenName;
        this.ui.showScreen(screenName);
    }

    showNotification(notification) {
        this.ui.showNotification(notification);
    }

    showProgress() {
        // Показ экрана прогресса
        const progress = this.dataManager.getProgress();
        this.ui.showProgressScreen(progress);
    }

    emergencyHelp() {
        // Экстренная помощь
        this.showNotification({
            type: 'emergency',
            title: '🆘 Экстренная помощь',
            message: 'Отправка данных о местоположении...',
            actions: [
                { text: 'Отмена', action: () => { } }
            ]
        });
    }

    showQuickActions() {
        // Быстрые действия
        const actions = [
            { text: 'Добавить задачу', action: () => this.addTask() },
            { text: 'Записать мысли', action: () => this.recordThoughts() },
            { text: 'Показать прогресс', action: () => this.showProgress() },
            { text: 'Настройки', action: () => this.showScreen('settings') }
        ];

        this.ui.showQuickActions(actions);
    }

    toggleVoice(enabled) {
        this.config.voiceEnabled = enabled;
        this.dataManager.saveConfig(this.config);
    }

    toggleNotifications(enabled) {
        this.config.notificationsEnabled = enabled;
        this.dataManager.saveConfig(this.config);
    }

    updateHeartRateThreshold(value) {
        this.config.heartRateThreshold = value;
        this.dataManager.saveConfig(this.config);
    }

    updateStepsGoal(value) {
        this.config.stepsGoal = value;
        this.dataManager.saveConfig(this.config);
    }

    startMeditation() {
        this.showNotification('🧘 Запуск медитации...');
        // Логика медитации
    }

    startBreathing() {
        this.showNotification('🫁 Упражнения для дыхания...');
        // Логика дыхательных упражнений
    }

    addTask() {
        this.startVoiceCommand();
    }

    recordThoughts() {
        this.startVoiceCommand();
    }
}

// Компоненты приложения

class Sensors {
    async initialize() {
        console.log('🔧 Инициализация сенсоров...');
    }

    async getHeartRate() {
        // Получение пульса с сенсора
        return Math.floor(Math.random() * 40) + 60; // Моковые данные
    }

    async getActivityData() {
        // Получение данных активности
        return {
            steps: Math.floor(Math.random() * 5000) + 5000,
            calories: Math.floor(Math.random() * 300) + 200,
            distance: Math.random() * 5 + 2,
            activeMinutes: Math.floor(Math.random() * 60) + 30
        };
    }
}

class Communication {
    constructor() {
        this.serverUrl = 'http://localhost:8000';
    }

    async initialize() {
        console.log('📡 Инициализация связи...');
    }

    async sendData(type, data) {
        try {
            const response = await fetch(`${this.serverUrl}/watch/data`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, data })
            });
            return await response.json();
        } catch (error) {
            console.error('Ошибка отправки данных:', error);
        }
    }

    async sendVoiceCommand(command, biometrics) {
        try {
            const response = await fetch(`${this.serverUrl}/watch/voice`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command, biometrics })
            });
            const result = await response.json();
            return result.response;
        } catch (error) {
            console.error('Ошибка отправки голосовой команды:', error);
            return 'Ошибка обработки команды';
        }
    }

    async syncData(data) {
        try {
            const response = await fetch(`${this.serverUrl}/watch/sync`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Ошибка синхронизации:', error);
        }
    }
}

class UserInterface {
    constructor() {
        this.screens = {};
        this.currentScreen = null;
    }

    async initialize() {
        console.log('🎨 Инициализация интерфейса...');
    }

    createScreen(name, config) {
        this.screens[name] = config;
    }

    showScreen(name) {
        this.currentScreen = name;
        console.log(`📱 Показ экрана: ${name}`);
        // Здесь будет реальная отрисовка экрана
    }

    updateElement(id, data) {
        console.log(`🔄 Обновление элемента: ${id}`, data);
        // Здесь будет обновление элемента интерфейса
    }

    setupGestures(gestures) {
        console.log('👆 Настройка жестов:', Object.keys(gestures));
        // Здесь будет настройка жестов
    }

    showNotification(notification) {
        console.log('🔔 Уведомление:', notification);
        // Здесь будет показ уведомления
    }

    showProgressScreen(progress) {
        console.log('📊 Экран прогресса:', progress);
        // Здесь будет показ экрана прогресса
    }

    showQuickActions(actions) {
        console.log('⚡ Быстрые действия:', actions);
        // Здесь будет показ быстрых действий
    }
}

class DataManager {
    constructor() {
        this.data = {};
        this.config = {};
    }

    async initialize() {
        console.log('💾 Инициализация менеджера данных...');
        // Загрузка сохраненных данных
    }

    saveMetric(id, value) {
        this.data[id] = {
            value: value,
            timestamp: Date.now()
        };
    }

    getAllData() {
        return this.data;
    }

    getProgress() {
        return {
            steps: this.data.steps?.value || 0,
            calories: this.data.calories?.value || 0,
            heartRate: this.data.heart_rate?.value || 0
        };
    }

    saveConfig(config) {
        this.config = config;
        // Сохранение в локальное хранилище
    }
}

class VoiceProcessor {
    async initialize() {
        console.log('🎤 Инициализация голосового процессора...');
    }

    async startRecording() {
        console.log('🎤 Начало записи...');
        // Здесь будет реальная запись голоса
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Моковые команды для тестирования
        const commands = [
            'как мое здоровье',
            'добавь задачу медитация',
            'покажи прогресс',
            'что мне делать'
        ];

        return commands[Math.floor(Math.random() * commands.length)];
    }
}

// Запуск приложения
const app = new LifeWatchApp();
app.initialize().then(() => {
    console.log('🚀 Life Watch App запущен!');
}).catch(error => {
    console.error('❌ Ошибка запуска:', error);
});

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LifeWatchApp };
}
