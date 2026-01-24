#!/bin/bash

# GateKeeper Setup Script
# This script helps set up GateKeeper for the first time

echo "==================================="
echo "  GateKeeper Setup Script"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and update the following:"
    echo "   - SECRET_KEY (generate a secure random key)"
    echo "   - DATABASE_URL (if using external database)"
    echo "   - SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET"
    echo "   - SMTP credentials for email sending"
    echo ""
    read -p "Press Enter to continue after updating .env..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📦 Running database migrations..."
docker-compose exec -T web flask db upgrade

echo ""
echo "🌱 Seeding permissions..."
docker-compose exec -T web flask seed-permissions

echo ""
echo "🌱 Seeding default roles..."
docker-compose exec -T web flask seed-roles

echo ""
echo "👤 Creating super admin user..."
read -p "Enter super admin email: " ADMIN_EMAIL
read -p "Enter super admin name: " ADMIN_NAME

docker-compose exec -T web flask create-super-admin --email "$ADMIN_EMAIL" --name "$ADMIN_NAME"

echo ""
echo "==================================="
echo "  Setup Complete! 🎉"
echo "==================================="
echo ""
echo "Your GateKeeper instance is now running!"
echo ""
echo "🌐 Access the application:"
echo "   Web:  http://localhost:5000"
echo "   API:  http://localhost:5000/api"
echo ""
echo "📊 Monitor services:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "📚 Next steps:"
echo "   1. Configure Supabase authentication"
echo "   2. Set up SMTP for email delivery"
echo "   3. Create your first event"
echo "   4. Import participants via CSV"
echo ""
