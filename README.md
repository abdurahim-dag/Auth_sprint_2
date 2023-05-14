# Проектная работа 7 спринта

Упростите регистрацию и аутентификацию пользователей в Auth-сервисе, добавив вход через социальные сервисы. Список сервисов выбирайте исходя из целевой аудитории онлайн-кинотеатра — подумайте, какими социальными сервисами они пользуются. Например, использовать [OAuth от Github](https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps){target="_blank"} — не самая удачная идея. Ваши пользователи не разработчики и вряд ли имеют аккаунт на Github. А вот добавить VK, Google, Yandex или Mail будет хорошей идеей.

    Вам не нужно делать фронтенд в этой задаче и реализовывать собственный сервер OAuth. Нужно реализовать протокол со стороны потребителя.
    
    Информация по OAuth у разных поставщиков данных: 
    
    - [Yandex](https://yandex.ru/dev/oauth/?turbo=true){target="_blank"},
    - [VK](https://vk.com/dev/access_token){target="_blank"},
    - [Google](https://developers.google.com/identity/protocols/oauth2){target="_blank"},
    - [Mail](https://api.mail.ru/docs/guides/oauth/){target="_blank"}.

# Решение.

## Структура приложения.
- auth/app: исходный код сервиса авторизации;
- auth/app/tests: тесты.

## Компоненты приложения, описанные в Docker compose:
- auth: сервиса авторизации;
- auth-db: БД хранилище учетных данных авторизации;
- auth-redis: хранилище токенов JWT;
- auth-tests: тесты.

## Сборка и запуск проекта на docker compose
1. Перейдите в папку решения: cd auth
2. На основе файла .env.example создайте копию .env
3. Замените параметры доступа к email в соответствии с вашим сервером почты переменные в .env AUTH_EMAIL_*
4. Запустите контейнер командой: docker compose --env-file .env up -d --no-deps --build
5. context: .context:
5. После первого запуска перезапустите повторно контейнер тестов auth-tests
6. Создаём супер пользователя, на сервере авторизации: docker exec -it auth bash -c "flask superuser create"
7. Openapi по пути: auth/api/v1/
   docker compose --env-file .env up -d --no-deps --build
   docker compose down --remove-orphans -v
   Контейнеры поднялись, и после второго запуска auth-tests тесты прошли...

### Алгорит oauth
1. Пользователь хочет войти с помощью соц. сети.
2. Попадает на http://auth/auth/api/v1/oauth/login?social=yandex
3. Сервис ридеректит куда надо. 
3. После согласия пользователь соц сеть ридеректит на http://auth/auth/api/v1/oauth/authorize?social=yandex
3.1. Получаем информацию от соц. сети, если нет то сообщаем об этом.
3.2. Добавляем учётные данные пользователя.
4. В случаи успешного добавления то генерим JWT токены как обычно.
