# Node frontend (Vite + React)
FROM node:24.11.0-alpine

WORKDIR /app

# Install deps
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Run dev server binding to all interfaces and fixed port
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]