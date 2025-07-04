export PYTHON_VERSION=3.13
export ENVIRONMENT=localhost
VENV_DIR ?= .venv
KERNEL_NAME=ai-kernel

install:
	@echo "🚀 Creating virtual environment with uv..."
	@if ! command -v uv &> /dev/null; then \
        echo "❌ uv is not installed. Please install it with: pip install uv"; \
        exit 1; \
    fi
	@if [ ! -d "$(VENV_DIR)" ]; then \
        uv venv $(VENV_DIR) --python=$(PYTHON_VERSION); \
    else \
        echo "✅ Virtual environment already exists."; \
    fi
	@echo "📦 Installing dependencies with uv pip..."
	@. $(VENV_DIR)/bin/activate && uv pip install -r requirements.in && uv pip install ipykernel && uv pip install -e .
	@echo "🔌 Registering Jupyter kernel..."
	@$(VENV_DIR)/bin/python -m ipykernel install --user --name=$(KERNEL_NAME) --display-name="Python (uv)"
	@echo "✅ uv virtual environment ready for Jupyter Notebook."

# This command will generate the exact requirements.txt file needed to build the Docker image in the CI/CD pipeline.
# It will run a Docker container to generate the requirements.txt file in the same environment as the CI/CD pipeline.
# Then it will copy the requirements.txt file from the container to the host.
# NOTE: We should run this command every time we want to update the requirements.txt file.
# Generar requirements.txt (a partir de un lock o de requirements.in)
generate-requirements:
	@echo "📋 Generando requirements.txt desde el entorno .uv con uv pip freeze..."
	@command -v uv >/dev/null 2>&1 || pip install --user uv
	@. $(VENV_DIR)/bin/activate && uv pip freeze > src/requirements.txt
	@echo "✅ requirements.txt generado"


###############################################################################
# APPLICATION EXECUTION
###############################################################################

# Run development server
run-dev:
	@echo "🚀 Starting development server..."
	@( \
        if [ ! -d .venv ]; then make install; fi; \
        source .venv/bin/activate; \
        langgraph dev; \
    )

# Run API server
run-api:
	@echo "🚀 Starting API server..."
	@( \
        if [ ! -d .venv ]; then make install; fi; \
        source .venv/bin/activate; \
        PYTHONPATH=${PWD} uvicorn api:app --reload --host 0.0.0.0 --port 8000 --log-level debug; \
    )

# Run a python script for single question
run-question:
	@echo "🚀 Running a single question"
	@( \
        if [ ! -d .venv ]; then make install; fi; \
        source .venv/bin/activate; \
		python main.py --question "cual es el estado de la ruta de chos malal?"; \
	)

###############################################################################
# Build and Deploy
###############################################################################

# Variables for Docker
IMAGE_NAME ?= agent-rutas
IMAGE_TAG ?= latest

# Build Docker image
build:
	@echo "🔨 Building Docker image..."
	@docker build --platform=linux/amd64 -t $(IMAGE_NAME):$(IMAGE_TAG) .
	@echo "✅ Docker image built successfully: $(IMAGE_NAME):$(IMAGE_TAG)"

# Run Docker container
run-docker:
	@echo "🚀 Running Docker container..."
	@docker run --platform=linux/amd64 \
		--name agent-rutas-container \
		-p 8000:8000 \
		--rm \
		$(IMAGE_NAME):$(IMAGE_TAG)

# Run Docker container in background
run-docker-bg:
	@echo "🚀 Running Docker container in background..."
	@docker run --platform=linux/amd64 \
		--name agent-rutas-container \
		-p 8000:8000 \
		-d \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✅ Docker container is running in background!"

# Stop Docker container
stop-docker:
	@echo "🛑 Stopping Docker container..."
	@docker stop agent-rutas-container || true
	@echo "✅ Docker container stopped!"

# View Docker logs
logs-docker:
	@docker logs -f agent-rutas-container

# Clean Docker images and containers
clean-docker:
	@echo "🧹 Cleaning Docker containers and images..."
	@docker stop agent-rutas-container || true
	@docker rm agent-rutas-container || true
	@docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	@echo "✅ Docker cleanup completed!"