FROM maven:3.9.11-eclipse-temurin-17-noble AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B || true

COPY src ./src
RUN mvn package -DskipTests -B


FROM eclipse-temurin:17-jre-noble

WORKDIR /app

# Instala Python para ejecutar las pruebas de integración.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Crea un entorno virtual e instala PyTest y requests.
COPY requirements-test.txt .

RUN python3 -m venv /opt/pytest-env \
    && /opt/pytest-env/bin/pip install \
        --no-cache-dir \
        -r requirements-test.txt

# Permite usar python y pytest directamente.
ENV PATH="/opt/pytest-env/bin:$PATH"

RUN mkdir -p /data /uploads

COPY --from=builder /app/target/*.jar app.jar

# Copia las pruebas al contenedor.
COPY tests ./tests

EXPOSE 8080

ENTRYPOINT [ "java", \
    "-jar", \
    "app.jar", \
    "--spring.sql.init.mode=always", \
    "--spring.datasource.url=jdbc:h2:file:/data/cine3;AUTO_SERVER=TRUE", \
    "--spring.jpa.hibernate.ddl-auto=update", \
    "--app.upload-dir=/uploads", \
    "--debug"]