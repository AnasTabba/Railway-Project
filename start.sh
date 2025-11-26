#!/bin/bash

# Railway Management System - Quick Start Script

echo "🚂 Railway Management System - Quick Start"
echo "==========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"
echo ""

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created. Please update with your credentials if needed."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🐳 Starting Docker containers..."
echo ""

# Start services
docker-compose up --build

echo ""
echo "✅ Services started!"
echo ""
echo "🌐 Access the application:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:5000"
echo "   - Database: localhost:3306"
echo ""
echo "📝 Demo Credentials:"
echo "   - Admin: admin@railway.com / admin123"
echo "   - User: john@example.com / user123"
echo ""
echo "📚 Documentation: Check README.md for detailed information"
echo ""
