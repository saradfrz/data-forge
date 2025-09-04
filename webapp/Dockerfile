FROM node:20

WORKDIR /app

# Copy backend package files first
COPY backend/package*.json ./backend/

# Install backend dependencies
RUN npm install --prefix backend

# Copy the rest of backend and frontend
COPY backend ./backend
COPY frontend ./frontend

WORKDIR /app/backend

EXPOSE 3000
CMD ["node", "index.js"]
