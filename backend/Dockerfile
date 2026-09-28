# Java 17 기반 이미지
FROM openjdk:21

# JAR 복사 (Gradle 기준)
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar

# 실행
ENTRYPOINT ["java", "-jar", "/app.jar"]
