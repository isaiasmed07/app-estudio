# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios
COPY . .

# Instala las dependencias desde requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Comando de inicio de la aplicación
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app"]
