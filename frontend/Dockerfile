# 1단계: 빌드용 Node 이미지 사용
FROM node:20 AS builder

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 설치를 위한 파일 복사
COPY package*.json ./
RUN npm install

# 전체 소스 복사 (node_modules 제외는 .dockerignore로 처리)
COPY . .

# Vite로 빌드 (결과는 dist/ 폴더에 생성됨)
RUN npm run build

# 2단계: 빌드 결과를 Nginx로 서비스
FROM nginx:stable-alpine

# dist 폴더를 nginx HTML 폴더로 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 사용자 정의 nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 오픈
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]
