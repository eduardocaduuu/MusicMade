# MusicMade - AI Music Instrument Separator & Tablature Generator

Uma aplicação web moderna que utiliza inteligência artificial para separar instrumentos musicais de arquivos de áudio e gerar tablaturas automaticamente.

## 🎵 Funcionalidades

- **Separação de Instrumentos**: Separa vocals, guitarra, baixo, bateria, piano e outros instrumentos usando IA
- **Geração de Tablatura**: Cria tablaturas automaticamente para guitarra, baixo e piano
- **Player Avançado**: Reproduza tracks separados com controles individuais de volume e solo/mute
- **Visualização de Waveform**: Veja a forma de onda de cada instrumento separado
- **Download Individual**: Baixe cada track separado ou todos de uma vez
- **Interface Moderna**: Design responsivo e intuitivo com drag-and-drop

## 🚀 Tecnologias

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Demucs**: IA de última geração para separação de fonte de áudio
- **Librosa**: Análise de áudio e detecção de pitch para tablaturas
- **SQLAlchemy**: ORM para gerenciamento de banco de dados
- **Celery + Redis**: Processamento assíncrono de jobs

### Frontend
- **React 18**: Biblioteca UI com TypeScript
- **Tailwind CSS**: Framework CSS utilitário
- **Wavesurfer.js**: Visualização de waveform
- **Axios**: Cliente HTTP
- **React Query**: Gerenciamento de estado do servidor

## 📋 Pré-requisitos

### Para Desenvolvimento Local

```bash
# Python 3.9+
python --version

# Node.js 16+
node --version

# FFmpeg (necessário para processamento de áudio)
ffmpeg -version

# Redis (para sistema de filas)
redis-server --version
```

## 🛠️ Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/eduardocaduuu/MusicMade.git
cd MusicMade
```

### 2. Configure o Backend

```bash
cd backend

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp ../.env.example .env
# Edite .env com suas configurações
```

### 3. Configure o Frontend

```bash
cd ../frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env.local
# Edite .env.local com suas configurações
```

### 4. Inicie os Serviços

#### Terminal 1 - Backend:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Celery Worker:
```bash
cd backend
celery -A app.workers.celery_worker worker --loglevel=info
```

#### Terminal 3 - Redis:
```bash
redis-server
```

#### Terminal 4 - Frontend:
```bash
cd frontend
npm start
```

A aplicação estará disponível em:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação da API: http://localhost:8000/docs

## 🐳 Docker

```bash
# Construa e inicie todos os serviços
docker-compose up --build

# Em modo detached
docker-compose up -d

# Pare os serviços
docker-compose down
```

## 📦 Deploy no Render

### Backend

1. Faça fork deste repositório
2. Crie um novo **Web Service** no Render
3. Conecte seu repositório GitHub
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

5. Adicione variáveis de ambiente:
   - `DATABASE_URL`: (Render fornece automaticamente se adicionar PostgreSQL)
   - `REDIS_URL`: (Render fornece automaticamente se adicionar Redis)
   - `SECRET_KEY`: (gere uma chave segura)
   - `ENVIRONMENT`: production

6. Adicione serviços gratuitos:
   - PostgreSQL (grátis até 1GB)
   - Redis (grátis até 25MB)

### Frontend

1. Crie um novo **Static Site** no Render
2. Configure:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`

3. Adicione variável de ambiente:
   - `REACT_APP_API_URL`: URL do seu backend no Render

### Worker Celery (Opcional - para separação assíncrona)

1. Crie um novo **Background Worker** no Render
2. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && celery -A app.workers.celery_worker worker --loglevel=info`

## 📖 Como Usar

1. **Upload de Arquivo**
   - Arraste um arquivo de áudio ou clique para selecionar
   - Formatos suportados: MP3, WAV, FLAC, MP4 (até 100MB)

2. **Separação de Instrumentos**
   - Escolha o algoritmo (Demucs recomendado)
   - Selecione a qualidade (Fast ou High Quality)
   - Clique em "Separate Instruments"
   - Aguarde o processamento (pode levar alguns minutos)

3. **Player de Áudio**
   - Use os controles individuais para cada instrumento
   - Solo/Mute instrumentos específicos
   - Ajuste volume de cada track
   - Todos os tracks ficam sincronizados

4. **Geração de Tablatura**
   - Selecione um instrumento separado
   - Escolha o tipo de instrumento (Guitarra, Baixo, Piano)
   - Configure afinação (se necessário)
   - Clique em "Generate Tablature"
   - Visualize ou baixe a tablatura

5. **Download**
   - Baixe tracks individuais ou todos juntos
   - Baixe tablaturas em formato TXT ou PDF

## 🏗️ Estrutura do Projeto

```
MusicMade/
├── backend/               # API FastAPI
│   ├── app/
│   │   ├── api/          # Endpoints da API
│   │   ├── core/         # Configurações
│   │   ├── models/       # Modelos de dados
│   │   ├── services/     # Lógica de negócio
│   │   └── workers/      # Celery workers
│   └── requirements.txt
├── frontend/             # React App
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API clients
│   │   └── types/       # TypeScript types
│   └── package.json
├── docker-compose.yml   # Configuração Docker
└── README.md
```

## 🔧 API Endpoints

### Upload
- `POST /api/upload` - Upload de arquivo de áudio

### Separação
- `POST /api/separate/{file_id}` - Inicia separação de instrumentos
- `GET /api/jobs/{job_id}` - Status do job de separação
- `WS /api/jobs/{job_id}/ws` - WebSocket para updates em tempo real

### Áudio
- `GET /api/tracks/{track_id}` - Download de track separado
- `GET /api/tracks/{track_id}/stream` - Stream de áudio

### Tablatura
- `POST /api/tablature/{track_id}` - Gera tablatura
- `GET /api/tablature/{tablature_id}` - Baixa tablatura

## 🎯 Roadmap

- [ ] Suporte para mais instrumentos (violino, saxofone, etc.)
- [ ] Editor de tablatura interativo
- [ ] Exportação para Guitar Pro
- [ ] Detecção automática de acordes
- [ ] Análise de tempo e compasso
- [ ] Autenticação de usuários
- [ ] Histórico de processamentos
- [ ] API pública

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👏 Agradecimentos

- [Demucs](https://github.com/facebookresearch/demucs) - Separação de fonte de áudio
- [Librosa](https://librosa.org/) - Análise de áudio
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [React](https://reactjs.org/) - Biblioteca UI

## 📧 Contato

Eduardo Cadu - [@eduardocaduuu](https://github.com/eduardocaduuu)

Link do Projeto: [https://github.com/eduardocaduuu/MusicMade](https://github.com/eduardocaduuu/MusicMade)
