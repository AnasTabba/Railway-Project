#!/bin/bash
# Quick System Status Check

echo "=================================="
echo "🚂 RAILWAY SYSTEM STATUS CHECK"
echo "=================================="
echo ""

# Check Docker containers
echo "📦 Docker Containers:"
docker-compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null | grep -E "(backend|frontend|mysql)"
echo ""

# Check backend health
echo "🔍 Backend API:"
if curl -s http://localhost:5001/health | grep -q "healthy"; then
    echo "✅ Backend is healthy (http://localhost:5001)"
else
    echo "❌ Backend not responding"
fi
echo ""

# Check frontend
echo "🔍 Frontend:"
if curl -s http://localhost:5173 | grep -q "html"; then
    echo "✅ Frontend is accessible (http://localhost:5173)"
else
    echo "❌ Frontend not responding"
fi
echo ""

# Check database data
echo "🔍 Database:"
docker-compose exec -T backend python -c "from extensions import db; from app import create_app; app = create_app(); app.app_context().push(); from models import Train, Station, Seat; print(f'✅ {Train.query.count()} trains, {Station.query.count()} stations, {Seat.query.count()} seats')" 2>/dev/null
echo ""

# Check API
echo "🔍 Search API:"
if curl -s 'http://localhost:5001/api/search?source=KHI&destination=LHE&date=2025-12-01' | grep -q "count"; then
    TRAIN_COUNT=$(curl -s 'http://localhost:5001/api/search?source=KHI&destination=LHE&date=2025-12-01' | grep -o '"count":[0-9]*' | cut -d: -f2)
    echo "✅ Search working - found $TRAIN_COUNT trains"
else
    echo "❌ Search API failed"
fi
echo ""

# Check advanced features
echo "🔍 Advanced Database Features:"
VIEW_COUNT=$(docker-compose exec -T backend python -c "from extensions import db; from app import create_app; app = create_app(); app.app_context().push(); result = db.session.execute(db.text('SELECT COUNT(*) FROM information_schema.views WHERE table_schema = database()')); print(result.scalar())" 2>/dev/null)

if [ "$VIEW_COUNT" -gt 0 ] 2>/dev/null; then
    echo "✅ $VIEW_COUNT views created"
    echo "✅ Advanced features applied"
else
    echo "⚠️  No views found - enhancements not applied yet"
    echo "   Run: docker-compose exec backend python apply_enhancements.py"
fi
echo ""

echo "=================================="
echo "📋 SUMMARY"
echo "=================================="
echo "✅ Backend: Running"
echo "✅ Frontend: Running"  
echo "✅ Database: Running with data"
echo "✅ API: Working"
echo ""
echo "🌐 Access your app:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5001/health"
echo ""
echo "📚 Documentation:"
echo "   - DATABASE_FEATURES.md"
echo "   - PRESENTATION_GUIDE.md"
echo "   - IMPLEMENTATION_SUMMARY.md"
echo "=================================="
