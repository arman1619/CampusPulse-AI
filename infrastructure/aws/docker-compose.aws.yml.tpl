services:
  db-bootstrap:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-auth:${IMAGE_TAG}
    command: ["python", "-m", "app.bootstrap_databases"]
    environment:
      - POSTGRES_ADMIN_URL
    restart: "no"

  frontend:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-frontend:${IMAGE_TAG}
    restart: unless-stopped

  auth-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-auth:${IMAGE_TAG}
    depends_on:
      db-bootstrap:
        condition: service_completed_successfully
    environment:
      - ENVIRONMENT
      - LOG_LEVEL
      - AUTH_DATABASE_URL
      - JWT_SECRET
      - JWT_ALGORITHM
      - JWT_EXPIRE_MINUTES
      - CORS_ORIGINS
      - SEED_DEMO
    restart: unless-stopped

  feedback-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-feedback:${IMAGE_TAG}
    depends_on:
      db-bootstrap:
        condition: service_completed_successfully
    environment:
      - ENVIRONMENT
      - LOG_LEVEL
      - FEEDBACK_DATABASE_URL
      - JWT_SECRET
      - JWT_ALGORITHM
      - INTERNAL_SERVICE_TOKEN
      - AI_SERVICE_URL
      - NOTIFICATION_SERVICE_URL
    restart: unless-stopped

  ai-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-ai:${IMAGE_TAG}
    environment:
      - ENVIRONMENT
      - LOG_LEVEL
      - HF_TOKEN
      - AI_CONFIDENCE_THRESHOLD
      - AI_MODEL_ID
      - AI_PROVIDER
      - AI_BACKEND
      - AI_REQUIRE_LLM
      - AI_API_TIMEOUT_SECONDS
      - AI_MAX_RETRIES
      - AI_MAX_TOKENS
      - AI_TEMPERATURE
    restart: unless-stopped

  notification-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-notification:${IMAGE_TAG}
    depends_on:
      db-bootstrap:
        condition: service_completed_successfully
    environment:
      - ENVIRONMENT
      - LOG_LEVEL
      - NOTIFICATION_DATABASE_URL
      - JWT_SECRET
      - JWT_ALGORITHM
      - INTERNAL_SERVICE_TOKEN
    restart: unless-stopped

  assistant-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-assistant:${IMAGE_TAG}
    depends_on:
      db-bootstrap:
        condition: service_completed_successfully
    environment:
      - ENVIRONMENT
      - LOG_LEVEL
      - ASSISTANT_DATABASE_URL
      - JWT_SECRET
      - JWT_ALGORITHM
      - HF_TOKEN
      - ASSISTANT_MODEL_ID
      - ASSISTANT_PROVIDER
      - ASSISTANT_BACKEND
      - ASSISTANT_REQUIRE_LLM
      - ASSISTANT_API_TIMEOUT_SECONDS
      - ASSISTANT_MAX_RETRIES
      - ASSISTANT_MAX_NEW_TOKENS
      - ASSISTANT_TEMPERATURE
      - ASSISTANT_TOP_P
    restart: unless-stopped

  gateway:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/campuspulse-gateway:${IMAGE_TAG}
    ports: ["8080:8080"]
    depends_on:
      - auth-service
      - feedback-service
      - ai-service
      - notification-service
      - assistant-service
      - frontend
    restart: unless-stopped
    volumes:
      - "${EB_LOG_BASE_DIR}/gateway:/var/log/nginx"
