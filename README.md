# BioInsight 🌱

An intelligent plant disease diagnosis system using AI/ML for agricultural health monitoring and treatment recommendations.

## 🌟 **Overview**

BioInsight is a comprehensive agricultural technology platform that helps farmers and agricultural professionals:
- **Diagnose plant diseases** using advanced AI/ML models
- **Get treatment recommendations** based on weather conditions
- **Monitor crop health** through real-time dashboards
- **Access insights** via web dashboard and mobile PWA

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PWA Client   │    │ Central Dashboard │    │   Backend API   │
│   (Mobile)     │◄──►│   (Web UI)      │◄──►│   (FastAPI)     │
│                │    │                 │    │                 │
│ • Plant Scans  │    │ • Analytics     │    │ • AI Inference  │
│ • History      │    │ • Queue Mgmt    │    │ • Weather Data   │
│ • Results      │    │ • System Health  │    │ • Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- **Node.js 18+** (for frontend development)
- **Python 3.12+** (for backend)
- **Docker Desktop** (optional, for containerized setup)

### **Option 1: Docker (Recommended)**
```bash
# Clone and start all services
git clone <repository-url>
cd BioInsight
docker-compose up -d --build

# Access applications:
# Backend: http://localhost:8000
# Dashboard: http://localhost:5173
# PWA: http://localhost:3000
```

### **Option 2: Manual Setup**
```bash
# Backend
cd backend
pip install -r requirements.txt
python app/main.py

# Central Dashboard (Terminal 1)
cd central-dashboard
npm install
npm run dev

# PWA Client (Terminal 2)
cd pwa-client
npm install
npm run dev
```

## 📁 **Project Structure**

```
BioInsight/
├── 📂 backend/                 # FastAPI backend
│   ├── 📂 app/
│   │   ├── 📂 api/            # API routes
│   │   ├── 📂 ai/             # AI/ML inference
│   │   ├── 📂 models/          # Database models
│   │   └── 📂 services/       # Business logic
│   ├── 📄 requirements.txt
│   └── 🐳 Dockerfile
├── 📂 central-dashboard/        # React web dashboard
│   ├── 📂 src/
│   │   ├── 📂 components/      # UI components
│   │   ├── 📂 routes/         # Page routes
│   │   └── 📂 services/       # API services
│   ├── 📄 package.json
│   └── 🐳 Dockerfile
├── 📂 pwa-client/             # React PWA application
│   ├── 📂 src/
│   │   ├── 📂 components/      # Mobile components
│   │   └── 📂 routes/         # PWA pages
│   ├── 📄 package.json
│   └── 🐳 Dockerfile
├── 🐳 docker-compose.yml        # Multi-service orchestration
└── 📚 DOCKER_SETUP.md          # Docker setup guide
```

## 🔧 **Technology Stack**

### **Backend**
- **FastAPI** - High-performance API framework
- **SQLAlchemy** - Database ORM
- **PyTorch** - AI/ML model serving
- **MobileViT** - Plant disease classification
- **SQLite** - Database (development)

### **Frontend**
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Vite** - Build tool
- **Hugeicons** - Icon library

### **Infrastructure**
- **Docker** - Containerization
- **Docker Compose** - Service orchestration
- **SSL/TLS** - Secure communication

## 🌱 **Features**

### **AI-Powered Diagnosis**
- ✅ **Plant disease detection** using MobileViT vision models
- ✅ **Confidence scoring** with risk assessment
- ✅ **Weather-aware recommendations** for treatment
- ✅ **Unknown object detection** for non-plant items

### **Real-Time Monitoring**
- ✅ **Diagnosis queue** with live status updates
- ✅ **Processing dashboard** for system administrators
- ✅ **Weather integration** for environmental context
- ✅ **Historical tracking** of disease patterns

### **User Experience**
- ✅ **Mobile PWA** for field use
- ✅ **Web dashboard** for management
- ✅ **Offline support** for rural areas
- ✅ **Responsive design** for all devices

## 🔗 **API Endpoints**

### **Authentication**
- `POST /api/pw/auth/login` - User authentication
- `GET /api/pw/auth/me` - User profile

### **Diagnosis**
- `POST /api/pw/diagnosis/request` - Submit plant scan
- `GET /api/pw/diagnosis/status/{job_id}` - Check scan status
- `GET /api/cd/diagnoses/queue` - View diagnosis queue
- `GET /api/cd/diagnoses/` - List all diagnoses

### **Weather**
- `GET /api/pw/weather/current_weather` - Current conditions
- `GET /api/cd/weather/current` - Dashboard weather data

## 🛠️ **Development**

### **Environment Variables**
```bash
# Backend
DATABASE_URL=sqlite:///./data/bioinsight.db
PYTHONPATH=/app

# Frontend
VITE_API_URL=http://localhost:8000
```

### **Database Setup**
```bash
# Initialize database
cd backend
python -c "from app.database.session import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

### **Testing**
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd central-dashboard
npm test

# PWA tests
cd pwa-client
npm test
```

## 📊 **Monitoring & Health**

### **Health Checks**
- **Backend**: `GET /health` - Service status
- **Database**: Connection monitoring
- **AI Models**: Inference service health

### **Performance Metrics**
- **Inference time**: AI model processing speed
- **Queue processing**: Job completion rates
- **API response times**: Service performance

## 🔐 **Security**

- **JWT Authentication** - Secure user sessions
- **SSL/TLS Encryption** - Data in transit protection
- **Input Validation** - Prevent injection attacks
- **Rate Limiting** - API abuse prevention

## 🌍 **Deployment**

### **Development**
```bash
docker-compose up -d --build
```

### **Production**
```bash
# Build production images
docker-compose -f docker-compose.prod.yml up -d --build
```

### **Environment Variables**
```bash
# Production settings
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key
SSL_CERT_PATH=/path/to/cert.pem
```

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### **Code Standards**
- **Python**: Follow PEP 8 style
- **TypeScript**: Use strict mode
- **Commits**: Conventional commit messages
- **Tests**: Include unit and integration tests

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

### **Documentation**
- [API Documentation](./docs/api.md)
- [Docker Setup Guide](./DOCKER_SETUP.md)
- [Development Guide](./docs/development.md)

### **Issues**
- **Bug Reports**: Create GitHub issue with template
- **Feature Requests**: Submit enhancement proposals
- **Questions**: Use GitHub Discussions

## 📈 **Roadmap**

### **Version 2.0**
- [ ] **Multi-language support** for global farmers
- [ ] **Advanced analytics** with predictive insights
- [ ] **IoT sensor integration** for real-time monitoring
- [ ] **Mobile app** (native iOS/Android)

### **Version 1.5**
- [ ] **Batch processing** for multiple images
- [ ] **Export functionality** for reports
- [ ] **User management** with role-based access
- [ ] **Cloud deployment** options

---

**🌱 BioInsight - Empowering farmers with AI-driven plant health monitoring**
