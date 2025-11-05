# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /code

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación (el directorio 'app')
COPY ./app /code/app

# Exponer el puerto en el que correrá uvicorn
EXPOSE 8000

# Comando para ejecutar la aplicación
# Inicia uvicorn, apuntando al objeto 'app' dentro del módulo 'app.main'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]