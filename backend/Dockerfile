# Java 21 런타임 이미지 (openjdk 공식 이미지는 더 이상 관리되지 않아 Eclipse Temurin 사용)
FROM eclipse-temurin:21-jre

# JAR 복사 (Gradle 기준)
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar

# 실행
ENTRYPOINT ["java", "-jar", "/app.jar"]
