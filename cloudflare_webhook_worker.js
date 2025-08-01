// Cloudflare Worker: Прокси для Notion API + webhook обработчик
addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url)

    // Если это запрос к Notion API (начинается с /v1/)
    if (url.pathname.startsWith('/v1/')) {
        return handleNotionProxy(request);
    }

    // Если это webhook от Notion (POST запрос без /v1/)
    if (request.method === 'POST' && !url.pathname.startsWith('/v1/')) {
        return handleWebhook(request);
    }

    return new Response('Method Not Allowed', { status: 405 });
}

async function handleNotionProxy(request) {
    const url = new URL(request.url)
    const notionUrl = `https://api.notion.com${url.pathname}${url.search}`

    console.log(`🔗 Проксируем запрос к Notion: ${notionUrl}`);
    console.log(`🔗 Метод запроса: ${request.method}`);
    console.log(`🔗 URL запроса: ${request.url}`);

    // Получаем Authorization заголовок
    const authHeader = request.headers.get('Authorization');
    console.log(`🔗 Получен Authorization заголовок: ${authHeader ? authHeader.substring(0, 30) + '...' : 'ОТСУТСТВУЕТ'}`);

    // Создаем ЧИСТЫЕ заголовки для Notion, чтобы не передавать IP Яндекса
    const headers = new Headers({
        'Authorization': authHeader,
        'Notion-Version': request.headers.get('Notion-Version') || '2022-06-28',
        'Content-Type': request.headers.get('Content-Type') || 'application/json',
        // Заголовки для обхода Cloudflare защиты Notion
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    });

    console.log(`🔗 Authorization заголовок в headers: ${headers.get('Authorization') ? headers.get('Authorization').substring(0, 30) + '...' : 'ОТСУТСТВУЕТ'}`);
    console.log(`🔗 Notion-Version заголовок: ${headers.get('Notion-Version')}`);
    console.log(`🔗 Content-Type заголовок: ${headers.get('Content-Type')}`);

    try {
        console.log(`🚀 Отправляем запрос к Notion: ${notionUrl}`);

        // Создаем новый объект Request для правильного проксирования
        const newRequest = new Request(notionUrl, {
            method: request.method,
            headers: headers,
            body: (request.method !== 'GET' && request.method !== 'HEAD') ? request.body : null
        });

        const response = await fetch(newRequest);

        console.log(`✅ Прокси ответ: ${response.status}`);
        console.log(`✅ Ответ Notion: ${response.status} ${response.statusText}`);

        if (response.status !== 200) {
            const errorText = await response.text();
            console.error(`❌ Ошибка Notion: ${response.status} - ${errorText}`);
            return new Response(errorText, {
                status: response.status,
                headers: response.headers
            });
        }

        const responseBody = await response.text();
        console.log(`✅ Возвращаем ответ: ${response.status}`);
        return new Response(responseBody, {
            status: response.status,
            headers: response.headers
        });

    } catch (error) {
        console.error(`❌ Ошибка прокси: ${error}`);
        return new Response('Proxy Error', { status: 500 });
    }
}

async function handleWebhook(request) {
    console.log('🚀 ПОЛУЧЕН WEBHOOK ОТ NOTION!');
    console.log('📊 URL запроса:', request.url);
    console.log('📊 Метод запроса:', request.method);
    console.log('📊 Заголовки:', Object.fromEntries(request.headers.entries()));

    try {
        const data = await request.json();
        console.log('📊 ТЕЛО WEBHOOK:', JSON.stringify(data, null, 2));

        // Обработка верификации Notion
        if (data.type === 'url_verification') {
            console.log('🔐 Пройдена верификация Notion:', data.challenge);
            return new Response(JSON.stringify({ challenge: data.challenge }), {
                headers: { 'Content-Type': 'application/json' }
            });
        }

        // Пересылка webhook в Яндекс.Функцию
        const yandexUrl = 'https://functions.yandexcloud.net/d4e3265b135595i9nec6'; // notion-updates (новая версия)

        console.log('🔗 Пересылка webhook в Яндекс.Клауд...');
        console.log('📊 Данные webhook:', JSON.stringify(data, null, 2));
        console.log('📊 Тип события:', data.type);

        const yandexResponse = await fetch(yandexUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!yandexResponse.ok) {
            const errorText = await yandexResponse.text();
            console.error(`❌ Ошибка при пересылке в Яндекс.Клауд: ${yandexResponse.status}`, errorText);
        } else {
            console.log('✅ Webhook успешно переслан.');
        }

        return new Response(JSON.stringify({ success: true }), {
            headers: { 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('❌ Критическая ошибка в воркере:', error);
        return new Response('Internal Server Error', { status: 500 });
    }
}
