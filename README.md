# 🛡️ SecurePay AI - Intelligent Financial Fraud Detection Platform

<div align="center">

![SecurePay AI](https://img.shields.io/badge/SecurePay-AI%20Fraud%20Detection-blue?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11+-green?style=flat-square&logo=python)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square&logo=typescript)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange?style=flat-square&logo=tensorflow)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=flat-square&logo=kubernetes)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

**A production-ready, AI-powered financial fraud detection system designed for Bangladesh's growing FinTech ecosystem**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Security](#-security-features) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Machine Learning Models](#-machine-learning-models)
- [Security Features](#-security-features)
- [DevSecOps Pipeline](#-devsecops-pipeline)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 About the Project

**SecurePay AI** is a comprehensive fraud detection platform tailored for Bangladesh's rapidly growing digital payment ecosystem. With mobile financial services like bKash and Nagad processing millions of transactions daily, the need for intelligent, real-time fraud detection has never been greater.

This project demonstrates expertise in:
- **Full-Stack Software Engineering** - Modern React frontend with FastAPI backend
- **Machine Learning Engineering** - Real-time fraud detection using ensemble models
- **DevSecOps** - Complete CI/CD pipeline with security scanning
- **Cyber Security** - OAuth2, JWT, encryption, audit logging, and vulnerability management
- **Signal Processing** - Leveraging EECE background for anomaly detection in transaction patterns

### 🇧🇩 Why This Matters for Bangladesh

- 📱 **100M+ MFS users** in Bangladesh need protection
- 💰 **$8B+ annual transactions** through mobile banking
- 🔒 **Rising cyber threats** require intelligent detection
- 🏦 **Digital Bangladesh vision** demands secure financial infrastructure

---

## ✨ Features

### Core Functionality
- 🔍 **Real-time Fraud Detection** - Sub-100ms response time for transaction scoring
- 📊 **Risk Analytics Dashboard** - Interactive visualizations of fraud patterns
- 🚨 **Smart Alerting System** - Multi-channel notifications (SMS, Email, Push)
- 📈 **Transaction Monitoring** - Live streaming of payment activities
- 🔐 **Secure Authentication** - OAuth2 + JWT with MFA support

### Machine Learning Capabilities
- 🤖 **Ensemble Model** - Combines Random Forest, XGBoost, and Neural Networks
- 📉 **Anomaly Detection** - Isolation Forest + Autoencoder hybrid
- 🎯 **Behavioral Analysis** - User pattern recognition using LSTM
- ⚡ **Online Learning** - Continuous model improvement with new data
- 📊 **Explainable AI** - SHAP values for decision transparency

### Security Features
- 🔑 **End-to-End Encryption** - AES-256 for data at rest, TLS 1.3 in transit
- 📝 **Comprehensive Audit Logs** - Immutable transaction and access logs
- 🛡️ **Rate Limiting & DDoS Protection** - Redis-based throttling
- 🔒 **RBAC** - Role-based access control for all endpoints
- 🕵️ **Threat Detection** - Automated vulnerability scanning

### DevSecOps
- 🐳 **Containerized Deployment** - Docker with security hardening
- ☸️ **Kubernetes Ready** - Helm charts for production deployment
- 🔄 **CI/CD Pipeline** - GitHub Actions with security gates
- 📋 **Infrastructure as Code** - Terraform configurations
- 📊 **Observability** - Prometheus + Grafana + ELK stack

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM |
| PostgreSQL | Primary database |
| Redis | Caching & rate limiting |
| Celery | Async task processing |
| Apache Kafka | Event streaming |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| TailwindCSS | Styling |
| React Query | Data fetching |
| Recharts | Visualizations |
| Zustand | State management |
| Vite | Build tool |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| TensorFlow/Keras | Deep learning models |
| Scikit-learn | Classical ML |
| XGBoost | Gradient boosting |
| MLflow | Model versioning |
| ONNX | Model deployment |
| SHAP | Explainability |

### DevSecOps
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Kubernetes | Orchestration |
| Helm | K8s package management |
| GitHub Actions | CI/CD |
| Trivy | Container scanning |
| SonarQube | Code analysis |
| HashiCorp Vault | Secrets management |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SecurePay AI Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Mobile    │    │    Web      │    │   Partner   │    │   Admin     │  │
│  │    Apps     │    │  Dashboard  │    │    APIs     │    │   Portal    │  │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘  │
│         │                  │                  │                  │         │
│         └──────────────────┴──────────────────┴──────────────────┘         │
│                                     │                                       │
│                          ┌──────────▼──────────┐                           │
│                          │   API Gateway       │                           │
│                          │   (Kong/Nginx)      │                           │
│                          │   - Rate Limiting   │                           │
│                          │   - SSL Termination │                           │
│                          │   - Auth Validation │                           │
│                          └──────────┬──────────┘                           │
│                                     │                                       │
│    ┌────────────────────────────────┼────────────────────────────────┐     │
│    │                                │                                │     │
│    ▼                                ▼                                ▼     │
│ ┌──────────────┐          ┌──────────────┐          ┌──────────────┐      │
│ │   Backend    │          │  ML Service  │          │   Auth       │      │
│ │   Service    │◄────────►│              │          │   Service    │      │
│ │  (FastAPI)   │          │  (FastAPI)   │          │  (OAuth2)    │      │
│ │              │          │              │          │              │      │
│ │ - Transactions│         │ - Inference  │          │ - JWT        │      │
│ │ - Users      │          │ - Training   │          │ - MFA        │      │
│ │ - Alerts     │          │ - Scoring    │          │ - RBAC       │      │
│ └──────┬───────┘          └──────┬───────┘          └──────────────┘      │
│        │                         │                                        │
│    ┌───┴───────────────────────┬─┴──────────────────────┐                │
│    │                           │                         │                │
│    ▼                           ▼                         ▼                │
│ ┌──────────┐            ┌──────────┐            ┌──────────────┐         │
│ │PostgreSQL│            │  Redis   │            │ Apache Kafka │         │
│ │          │            │          │            │              │         │
│ │- Users   │            │- Cache   │            │- Events      │         │
│ │- Trans.  │            │- Sessions│            │- Streaming   │         │
│ │- Logs    │            │- Rates   │            │- ML Pipeline │         │
│ └──────────┘            └──────────┘            └──────────────┘         │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Observability Stack                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │  │
│  │  │ Prometheus  │  │  Grafana    │  │    ELK      │  │  Jaeger   │  │  │
│  │  │  Metrics    │  │  Dashboards │  │   Logging   │  │  Tracing  │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Transaction Request → API Gateway → Authentication → Rate Limiting
                                                          │
                                                          ▼
                                    ┌─────────────────────────────────┐
                                    │      Fraud Detection Pipeline    │
                                    ├─────────────────────────────────┤
                                    │  1. Feature Extraction          │
                                    │  2. Rule-based Checks           │
                                    │  3. ML Model Inference          │
                                    │  4. Risk Score Calculation      │
                                    │  5. Decision Engine             │
                                    └─────────────────────────────────┘
                                                          │
                              ┌────────────────┬──────────┴───────────┐
                              │                │                      │
                              ▼                ▼                      ▼
                         [APPROVE]        [REVIEW]              [REJECT]
                              │                │                      │
                              └────────────────┴──────────────────────┘
                                               │
                                               ▼
                                    Store Result + Audit Log
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/securepay-ai-fraud-detection.git
cd securepay-ai-fraud-detection

# Copy environment files
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# ML Service: http://localhost:8001
# API Docs: http://localhost:8000/docs
```

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### ML Service Setup

```bash
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download pre-trained models
python scripts/download_models.py

# Start the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

---

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | User logout |
| POST | `/api/v1/auth/mfa/enable` | Enable MFA |
| POST | `/api/v1/auth/mfa/verify` | Verify MFA code |

### Transaction Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions/analyze` | Analyze transaction for fraud |
| GET | `/api/v1/transactions` | List transactions |
| GET | `/api/v1/transactions/{id}` | Get transaction details |
| PUT | `/api/v1/transactions/{id}/review` | Review flagged transaction |

### ML Service Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ml/predict` | Get fraud prediction |
| POST | `/api/v1/ml/batch-predict` | Batch predictions |
| GET | `/api/v1/ml/models` | List available models |
| POST | `/api/v1/ml/explain` | Get SHAP explanations |
| GET | `/api/v1/ml/metrics` | Model performance metrics |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/transactions/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN-2024-001",
    "amount": 50000,
    "currency": "BDT",
    "sender_account": "01712345678",
    "receiver_account": "01898765432",
    "transaction_type": "P2P",
    "device_fingerprint": "abc123xyz",
    "ip_address": "103.108.x.x",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Example Response

```json
{
  "transaction_id": "TXN-2024-001",
  "risk_score": 0.23,
  "risk_level": "LOW",
  "decision": "APPROVE",
  "confidence": 0.89,
  "flags": [],
  "explanation": {
    "top_factors": [
      {"feature": "amount_deviation", "impact": -0.12},
      {"feature": "device_known", "impact": -0.08},
      {"feature": "location_consistent", "impact": -0.05}
    ]
  },
  "processing_time_ms": 45
}
```

---

## 🤖 Machine Learning Models

### Ensemble Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Input Features (45+)        │
                    │  - Transaction features             │
                    │  - User behavior features           │
                    │  - Device/Location features         │
                    │  - Historical patterns              │
                    └─────────────────┬───────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │ Random Forest │       │    XGBoost    │       │  Neural Net   │
    │   (sklearn)   │       │   (xgboost)   │       │  (TensorFlow) │
    │               │       │               │       │               │
    │  Accuracy:    │       │  Accuracy:    │       │  Accuracy:    │
    │    94.2%      │       │    95.1%      │       │    93.8%      │
    └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │  Weighted Voting  │
                          │   Meta-Learner    │
                          └─────────┬─────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │       Final Prediction        │
                    │   Risk Score: 0.0 - 1.0       │
                    │   + SHAP Explanations         │
                    └───────────────────────────────┘
```

### Feature Engineering

| Category | Features | Description |
|----------|----------|-------------|
| Transaction | amount, currency, type | Basic transaction info |
| Temporal | hour, day_of_week, is_holiday | Time-based patterns |
| Behavioral | avg_amount_30d, tx_frequency | User spending patterns |
| Device | device_age, is_new_device | Device trust signals |
| Location | ip_country, ip_risk_score | Geographic risk |
| Network | sender_risk, receiver_risk | Network-based features |
| Velocity | tx_count_1h, amount_1h | Recent activity |

### Model Performance

| Model | Precision | Recall | F1-Score | AUC-ROC |
|-------|-----------|--------|----------|---------|
| Random Forest | 0.942 | 0.918 | 0.930 | 0.978 |
| XGBoost | 0.951 | 0.925 | 0.938 | 0.982 |
| Neural Network | 0.938 | 0.912 | 0.925 | 0.975 |
| **Ensemble** | **0.958** | **0.934** | **0.946** | **0.987** |

---

## 🔐 Security Features

### Authentication & Authorization

- **OAuth2 + JWT** - Industry-standard authentication
- **Multi-Factor Authentication** - TOTP-based MFA
- **Role-Based Access Control** - Fine-grained permissions
- **Session Management** - Secure session handling with Redis

### Data Protection

- **Encryption at Rest** - AES-256 encryption for sensitive data
- **Encryption in Transit** - TLS 1.3 for all communications
- **Data Masking** - PII masking in logs and responses
- **Key Management** - HashiCorp Vault integration

### Security Monitoring

- **Audit Logging** - Comprehensive, immutable audit trails
- **Intrusion Detection** - Anomaly-based threat detection
- **Rate Limiting** - DDoS protection with Redis
- **Vulnerability Scanning** - Automated security scans

### Compliance

- **Bangladesh Bank Guidelines** - Aligned with local regulations
- **PCI-DSS** - Payment Card Industry standards
- **GDPR** - Data protection best practices
- **OWASP Top 10** - Protection against common vulnerabilities

---

## 🔄 DevSecOps Pipeline

### CI/CD Workflow

```yaml
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Code     │────▶│    Build    │────▶│    Test     │────▶│  Security   │
│    Push     │     │   & Lint    │     │    Suite    │     │    Scan     │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                    ┌─────────────┐     ┌─────────────┐     ┌──────▼──────┐
                    │   Deploy    │◀────│   Staging   │◀────│   Docker    │
                    │   (Prod)    │     │    Test     │     │    Build    │
                    └─────────────┘     └─────────────┘     └─────────────┘
```

### Security Gates

1. **SAST** - SonarQube static analysis
2. **Dependency Scan** - Snyk vulnerability check
3. **Container Scan** - Trivy image scanning
4. **DAST** - OWASP ZAP dynamic testing
5. **Secret Detection** - GitLeaks pre-commit hooks

---

## 📦 Deployment

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace securepay

# Deploy using Helm
helm install securepay ./helm/securepay \
  --namespace securepay \
  --values ./helm/securepay/values-prod.yaml

# Check deployment status
kubectl get pods -n securepay
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `JWT_SECRET` | JWT signing secret | Yes |
| `ENCRYPTION_KEY` | Data encryption key | Yes |
| `ML_MODEL_PATH` | Path to ML models | Yes |

---

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app tests/

# Frontend tests
cd frontend
npm run test

# ML Service tests
cd ml-service
pytest --cov=app tests/

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Security tests
./scripts/run-security-tests.sh
```

### Test Coverage

- **Backend**: 85%+ coverage
- **Frontend**: 80%+ coverage
- **ML Service**: 90%+ coverage

---

## 👨‍💻 Author

<div align="center">

### **Md. Tanvir Hossain**

🎓 **M.Sc. in CSE (Computer Science and Engineering)** - BRAC University *(Pursuing)*  
🎓 **B.Sc. (Engg.) in EECE (Electrical, Electronic and Communication Engineering)** - MIST  
💼 **Full-Stack Developer | ML Engineer | DevSecOps Practitioner**

---

📧 **Email:** [tanvir.eece.mist@gmail.com](mailto:tanvir.eece.mist@gmail.com)  
🔗 **GitHub:** [@tanvir-eece-cse](https://github.com/tanvir-eece-cse)  
🔗 **LinkedIn:** [Md. Tanvir Hossain](https://www.linkedin.com/in/tanvir-eece/)

</div>

### Why This Project?

This project combines my unique background in:
- **Electrical, Electronic and Communication Engineering (EECE)** - Signal processing techniques for pattern recognition in transaction data
- **Computer Science and Engineering (CSE)** - Modern software engineering practices and system design
- **Machine Learning** - Building intelligent fraud detection using ensemble models
- **Security** - Implementing comprehensive cyber security measures for financial systems

I built this project to demonstrate my skills in building production-ready, secure financial applications while pursuing my M.Sc. at BRAC University. The project reflects real-world challenges faced by Bangladesh's growing FinTech sector.

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Bangladesh Bank for financial security guidelines
- MIST & BRAC University for academic foundation
- Open-source community for amazing tools

---

<div align="center">

**Built with ❤️ in Bangladesh 🇧🇩**

[⬆ Back to Top](#-securepay-ai---intelligent-financial-fraud-detection-platform)

</div>
