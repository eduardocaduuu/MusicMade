# Quick Start Guide - MusicMade

## Desenvolvimento Local

### Requisitos
- Python 3.9+
- Node.js 16+
- Redis
- FFmpeg

### 1. Backend Setup (5 minutos)

```bash
# Navegue para o diretório do backend
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

# Inicie o servidor
uvicorn app.main:app --reload
```

Backend disponível em: http://localhost:8000
Documentação da API: http://localhost:8000/docs

### 2. Celery Worker (Terminal separado)

```bash
cd backend
# Certifique-se de que o Redis está rodando
redis-server

# Em outro terminal, ative o ambiente virtual e inicie o worker
celery -A app.workers.celery_worker worker --loglevel=info
```

### 3. Frontend Setup (5 minutos)

```bash
# Navegue para o diretório do frontend
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env.local

# Inicie o servidor de desenvolvimento
npm start
```

Frontend disponível em: http://localhost:3000

## Docker (Mais fácil)

### Inicie todos os serviços com um comando:

```bash
# Na raiz do projeto
docker-compose up --build
```

Serviços:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usando a Aplicação

### 1. Upload de Arquivo
- Arraste um arquivo MP3, WAV, FLAC ou MP4
- Ou clique para selecionar
- Máximo 100MB

### 2. Configure a Separação
- **Algoritmo**:
  - Demucs (recomendado) - Melhor qualidade
  - Spleeter - Mais rápido
- **Qualidade**:
  - Fast - Processamento rápido
  - High - Melhor resultado

### 3. Aguarde o Processamento
- O processamento pode levar 2-5 minutos dependendo do arquivo
- Você verá o progresso em tempo real

### 4. Reproduza os Instrumentos Separados
- Use os controles de cada instrumento
- Solo (S): Isola apenas esse instrumento
- Mute (M): Silencia o instrumento
- Volume: Ajusta o volume individual
- Download: Baixa o track separado

### 5. Gere Tablatura (Opcional)
- Selecione um instrumento separado
- Escolha o tipo (Guitarra, Baixo, Piano)
- Configure a afinação
- Clique em "Generate Tablature"
- Baixe ou visualize a tablatura gerada

## Formatos Suportados

### Upload
- **Formatos**: MP3, WAV, FLAC, MP4, M4A
- **Tamanho máximo**: 100MB
- **Sample rate**: Qualquer (será convertido automaticamente)

### Download
- **Formato de saída**: WAV (sem perda)
- **Tracks separados**: Cada instrumento em arquivo individual

## Instrumentos Detectados

### Demucs (Padrão)
- Vocals (vocais)
- Drums (bateria)
- Bass (baixo)
- Other (outros instrumentos: guitarra, piano, etc.)

### Spleeter
- Vocals (vocais)
- Drums (bateria)
- Bass (baixo)
- Piano
- Other (outros)

## Tablatura

### Instrumentos Suportados
- **Guitarra**:
  - Standard (E A D G B E)
  - Drop D (D A D G B E)
  - Half Step Down
- **Baixo**:
  - Standard (E A D G)
  - 5 String (B E A D G)
- **Piano**:
  - Notação simplificada com notas e oitavas

### Formato de Saída
- Tablatura ASCII (arquivo .txt)
- Fácil de ler e imprimir
- Compatível com qualquer editor de texto

## Dicas de Uso

### Melhores Resultados
1. Use arquivos de alta qualidade (WAV ou FLAC)
2. Evite arquivos muito comprimidos (MP3 < 128kbps)
3. Para tablatura, use tracks com instrumento bem definido
4. Escolha "High Quality" se tiver tempo

### Performance
- Primeira separação pode demorar mais (download do modelo)
- Arquivos menores processam mais rápido
- Use "Fast" para testes rápidos

### Troubleshooting
- **Separação falhou**: Verifique se o arquivo é válido
- **Worker não responde**: Reinicie o Celery worker
- **Sem progresso**: Verifique se o Redis está rodando
- **Frontend não conecta**: Verifique as URLs em .env.local

## Estrutura do Projeto

```
MusicMade/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── api/     # Endpoints
│   │   ├── models/  # Modelos de dados
│   │   ├── services/# Lógica de negócio
│   │   └── workers/ # Celery tasks
│   └── requirements.txt
├── frontend/        # React App
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── package.json
└── docker-compose.yml
```

## API Endpoints

### Upload
```
POST /api/upload
```

### Separação
```
POST /api/separate/{file_id}
GET  /api/jobs/{job_id}
WS   /api/jobs/{job_id}/ws
```

### Áudio
```
GET /api/tracks/{track_id}/download
GET /api/tracks/{track_id}/stream
```

### Tablatura
```
POST /api/tracks/{track_id}/tablature
GET  /api/tablature/{tablature_id}
```

## Próximos Passos

1. **Desenvolvimento Local**: Teste todas as funcionalidades
2. **Deploy no Render**: Siga o guia em `DEPLOY.md`
3. **Personalize**: Ajuste cores, logos, textos
4. **Contribua**: Abra issues ou PRs no GitHub

## Suporte

- **Documentação**: README.md
- **Deploy**: DEPLOY.md
- **Issues**: https://github.com/eduardocaduuu/MusicMade/issues
- **API Docs**: http://localhost:8000/docs (quando rodando)

## Licença

MIT License - Veja LICENSE para detalhes

---

Feito com ❤️ usando IA e tecnologias modernas
