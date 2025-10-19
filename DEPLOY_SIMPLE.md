# Deploy Simplificado - Apenas 2 Serviços

A aplicação foi **simplificada** para rodar com apenas **2 serviços** no Render:

1. ✅ **Backend** (Web Service) - Processa tudo
2. ✅ **Frontend** (Static Site) - Interface React

**Removido:**
- ❌ Worker Celery separado
- ❌ Redis
- ❌ Complexidade de múltiplos serviços

## 🚀 Deploy no Render (5 minutos)

### Passo 1: Criar Conta no Render

1. Acesse https://render.com
2. Clique em **"Get Started"**
3. Faça login com **GitHub**
4. Autorize o Render

### Passo 2: Usar Blueprint (Automático)

1. No Dashboard, clique em **"New +"**
2. Selecione **"Blueprint"**
3. Conecte o repositório:
   - Clique em **"Connect repository"**
   - Busque: `MusicMade`
   - Clique em **"Connect"**

4. O Render detecta o `render.yaml` automaticamente
5. Você verá **3 serviços**:
   - ✅ musicmade-backend (Web Service)
   - ✅ musicmade-frontend (Static Site)
   - ✅ musicmade-db (PostgreSQL)

6. Clique em **"Apply"**
7. Aguarde 5-10 minutos

### Passo 3: Atualizar URLs (Após Deploy)

Após o primeiro deploy, você precisa ajustar as URLs:

1. **Copie a URL do backend**:
   - Exemplo: `https://musicmade-backend.onrender.com`

2. **Atualize o Frontend**:
   - Vá em: `musicmade-frontend` → **"Environment"**
   - Edite `REACT_APP_API_URL`:
     ```
     REACT_APP_API_URL=https://musicmade-backend.onrender.com
     ```
   - Clique em **"Save Changes"** (vai fazer redeploy)

3. **Atualize CORS no Backend**:
   - Copie a URL do frontend (ex: `https://musicmade-frontend.onrender.com`)
   - Vá em: `musicmade-backend` → **"Environment"**
   - Edite `ALLOWED_ORIGINS`:
     ```
     ALLOWED_ORIGINS=https://musicmade-frontend.onrender.com
     ```
   - Clique em **"Save Changes"**

### Pronto! 🎉

Sua aplicação está no ar:
- **Frontend**: `https://musicmade-frontend.onrender.com`
- **Backend API**: `https://musicmade-backend.onrender.com/docs`

---

## 🔧 Como Funciona Agora

### Processamento Síncrono

Ao invés de Celery + Redis, usamos **FastAPI BackgroundTasks**:

```python
# Quando você faz upload e clica em "Separate":
1. Backend cria um job no banco de dados
2. Inicia processamento em background (mesmo processo)
3. Frontend faz polling a cada 2 segundos para ver o status
4. Quando completa, mostra os resultados
```

### Vantagens

✅ **Mais simples**: Apenas 2 serviços
✅ **Sem Redis**: Economia de um serviço
✅ **Sem Worker**: Tudo em um Web Service
✅ **Fácil de debugar**: Menos componentes
✅ **Deploy rápido**: Menos configuração

### Limitações

⚠️ **1 processamento por vez**: Não pode processar múltiplos áudios simultaneamente
⚠️ **Reiniciar perde jobs**: Se o serviço reiniciar, jobs em andamento são perdidos
⚠️ **Timeout possível**: Arquivos muito grandes podem dar timeout

### Quando Funciona Bem

✅ Para testes e demos
✅ Para uso pessoal/portfólio
✅ Para 1 usuário por vez
✅ Arquivos até 50MB

---

## 🆘 Troubleshooting

### Serviço não inicia

1. Vá em **"Logs"** do serviço
2. Procure por erros
3. Verifique se instalou todas as dependências

### "Service Unavailable" no primeiro acesso

- **Normal!** Serviço gratuito "dorme" após 15 minutos
- Aguarde 30-60 segundos
- Recarregue a página

### Separação falha

1. Verifique se arquivo é < 100MB
2. Use qualidade "Fast" para testes
3. Veja logs do backend

### Frontend não conecta

1. Confirme `REACT_APP_API_URL` está correto
2. Teste: `https://seu-backend.onrender.com/health`
3. Deve retornar: `{"status": "healthy"}`

---

## 📊 Monitoramento

### Health Check

Teste se está funcionando:
```bash
curl https://musicmade-backend.onrender.com/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Logs

- Acesse cada serviço no Dashboard
- Clique em **"Logs"**
- Veja em tempo real o que está acontecendo

---

## 💡 Próximos Passos

### Se quiser melhorar no futuro:

1. **Upgrade para Starter** ($7/mês):
   - Sem spin down
   - Mais RAM
   - Melhor performance

2. **Adicionar Redis** (se precisar processar múltiplos áudios):
   - Voltar para arquitetura com Worker

3. **Armazenamento externo**:
   - AWS S3 para arquivos grandes
   - Cloudinary para assets

---

## 📚 Documentação Completa

- **README.md**: Visão geral e funcionalidades
- **QUICKSTART.md**: Desenvolvimento local
- **DEPLOY.md**: Deploy completo (com worker)

---

**Dúvidas?** Abra uma issue no GitHub!
**Link**: https://github.com/eduardocaduuu/MusicMade/issues
