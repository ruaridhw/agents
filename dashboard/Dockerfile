FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY src ./src
COPY tsconfig.json ./
ENV LOGS_DIR=/logs PORT=8787
EXPOSE 8787
CMD ["npx", "tsx", "src/index.ts"]
