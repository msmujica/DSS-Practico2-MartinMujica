FROM maven:3.9.11-eclipse-temurin-17-noble

WORKDIR /app

COPY pom.xml .

RUN mvn dependency:go-offline -B || true

COPY src ./src

RUN mvn package -DskipTests -B \
    && cp target/*.jar app.jar

RUN mkdir -p /data /uploads

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar", "--spring.sql.init.mode=always", "--spring.datasource.url=jdbc:h2:file:/data/cine3;AUTO_SERVER=TRUE", "--spring.jpa.hibernate.ddl-auto=update", "--app.upload-dir=/uploads", "--debug"]