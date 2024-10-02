FROM maven:3-amazoncorretto-21-alpine AS build

WORKDIR /app
COPY . .

RUN mvn clean install


FROM openjdk:21-jdk-slim AS deploy
WORKDIR /app

COPY --from=build /app/target/simpleTaskTrackerWebApp-1.0-SNAPSHOT.jar /app/simpleTaskTrackerWebApp.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "simpleTaskTrackerWebApp.jar"]