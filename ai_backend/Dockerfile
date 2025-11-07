# 1️⃣ Use official Python 3.12 base image
FROM python:3.12-slim

# 2️⃣ Set working directory inside the container
WORKDIR /app

# 3️⃣ Copy your project files
COPY . .

# 4️⃣ Install dependencies
RUN pip install --no-cache-dir -r requirement.txt

# 5️⃣ Expose port 5000 for Flask
EXPOSE 5000

# 6️⃣ Set environment to production
ENV FLASK_ENV=production

# 7️⃣ Run Flask app with Gunicorn (recommended for production)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
