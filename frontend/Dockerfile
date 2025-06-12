# build env
FROM node:21.7.1-slim

WORKDIR /app

COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы
COPY . .

# Собираем проект
RUN npm run build

# Копируем результат сборки во временную папку, с которой будет работать nginx
CMD cp -r build result_build


