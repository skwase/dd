# Render deployment checklist

1) Создать Web Service на Render:
   - Тип: Docker
   - Build from a Dockerfile (укажи, что Dockerfile лежит в репозитории)

2) В GitHub добавить секреты (Settings → Secrets and variables → Actions):
   - RENDER_API_KEY
   - RENDER_SERVICE_ID

3) Сделать push в main/master.

4) Workflow вызовет Render API и сервис перезагрузится.

После успешной сборки Render даст URL сервиса — именно его ты используешь как "готовую ссылку".
