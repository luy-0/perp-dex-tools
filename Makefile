# Hedge Mode Trading Bot Docker Management
.PHONY: build run run-backpack run-extended interactive logs shell stop clean help status stop-backpack stop-extended logs-backpack logs-extended

# 默认目标：显示所有指令
.DEFAULT_GOAL := list

list:
	@echo "可用的make命令:"
	@awk -F':' '/^[a-zA-Z0-9][^$$#\t ]*:/ {split($$1,A," ");print "  - "A[1]}' $(MAKEFILE_LIST) | grep -v "^  - .PHONY" | grep -v "^  - list"

# Configuration
IMAGE_NAME := hedge-trading-bot
CONTAINER_NAME := hedge-bot
DOCKER_TAG := latest
ENV_FILE ?= .env

# Docker build target
build:
	@echo "Building Hedge Trading Bot Docker image..."
	docker build -t $(IMAGE_NAME):$(DOCKER_TAG) .
	@echo "✅ Build completed successfully"

# Run container interactively (for manual commands)
interactive:
	@echo "Starting interactive container..."
	docker run -it --rm \
		--name $(CONTAINER_NAME)-interactive \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/$(ENV_FILE):/app/.env:ro \
		$(IMAGE_NAME):$(DOCKER_TAG) \
		/bin/bash

# Run Backpack hedge mode
run-backpack:
	@if [ -z "$(TICKER)" ] || [ -z "$(SIZE)" ] || [ -z "$(ITER)" ]; then \
		echo "❌ Error: Missing required parameters"; \
		echo "Usage: make run-backpack TICKER=BTC SIZE=0.01 ITER=10 [TIMEOUT=5]"; \
		exit 1; \
	fi
	@echo "🚀 Starting Backpack hedge mode..."
	@echo "   Ticker: $(TICKER), Size: $(SIZE), Iterations: $(ITER)"
	docker run -d \
		--name $(CONTAINER_NAME)-backpack \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/$(ENV_FILE):/app/.env:ro \
		$(IMAGE_NAME):$(DOCKER_TAG) \
		python hedge_mode.py \
		--exchange backpack \
		--ticker $(TICKER) \
		--size $(SIZE) \
		--iter $(ITER) \
		--fill-timeout $(or $(TIMEOUT),5)
	@echo "✅ Container started. Use 'make logs' to view output"

# Run Extended hedge mode
run-extended:
	@if [ -z "$(TICKER)" ] || [ -z "$(SIZE)" ] || [ -z "$(ITER)" ]; then \
		echo "❌ Error: Missing required parameters"; \
		echo "Usage: make run-extended TICKER=ETH SIZE=0.1 ITER=5 [TIMEOUT=5]"; \
		exit 1; \
	fi
	@echo "🚀 Starting Extended hedge mode..."
	@echo "   Ticker: $(TICKER), Size: $(SIZE), Iterations: $(ITER)"
	docker run -d \
		--name $(CONTAINER_NAME)-extended \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/$(ENV_FILE):/app/.env:ro \
		$(IMAGE_NAME):$(DOCKER_TAG) \
		python hedge_mode.py \
		--exchange extended \
		--ticker $(TICKER) \
		--size $(SIZE) \
		--iter $(ITER) \
		--fill-timeout $(or $(TIMEOUT),5)
	@echo "✅ Container started. Use 'make logs' to view output"

# Generic run command (requires EXCHANGE parameter)
run:
	@if [ -z "$(EXCHANGE)" ] || [ -z "$(TICKER)" ] || [ -z "$(SIZE)" ] || [ -z "$(ITER)" ]; then \
		echo "❌ Error: Missing required parameters"; \
		echo "Usage: make run EXCHANGE=backpack TICKER=BTC SIZE=0.01 ITER=10 [TIMEOUT=5]"; \
		exit 1; \
	fi
	@echo "🚀 Starting $(EXCHANGE) hedge mode..."
	@echo "   Ticker: $(TICKER), Size: $(SIZE), Iterations: $(ITER)"
	docker run -d \
		--name $(CONTAINER_NAME)-$(EXCHANGE) \
		-v $(PWD)/logs:/app/logs \
		-v $(PWD)/$(ENV_FILE):/app/.env:ro \
		$(IMAGE_NAME):$(DOCKER_TAG) \
		python hedge_mode.py \
		--exchange $(EXCHANGE) \
		--ticker $(TICKER) \
		--size $(SIZE) \
		--iter $(ITER) \
		--fill-timeout $(or $(TIMEOUT),5)
	@echo "✅ Container started. Use 'make logs' to view output"

# View real-time logs
logs:
	@echo "📋 Showing real-time logs (Press Ctrl+C to exit)..."
	@if docker ps --format "table {{.Names}}" | grep -q "$(CONTAINER_NAME)"; then \
		ACTIVE_CONTAINER=$$(docker ps --format "{{.Names}}" | grep "$(CONTAINER_NAME)" | head -1); \
		echo "   Following logs for: $$ACTIVE_CONTAINER"; \
		docker logs -f $$ACTIVE_CONTAINER; \
	else \
		echo "❌ No active hedge bot containers found"; \
		echo "Available containers:"; \
		docker ps --filter "ancestor=$(IMAGE_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"; \
	fi

# View logs for specific container
logs-backpack:
	@echo "📋 Showing Backpack hedge bot logs..."
	docker logs -f $(CONTAINER_NAME)-backpack

logs-extended:
	@echo "📋 Showing Extended hedge bot logs..."
	docker logs -f $(CONTAINER_NAME)-extended

# Access running container shell
shell:
	@if docker ps --format "table {{.Names}}" | grep -q "$(CONTAINER_NAME)"; then \
		ACTIVE_CONTAINER=$$(docker ps --format "{{.Names}}" | grep "$(CONTAINER_NAME)" | head -1); \
		echo "🐚 Accessing shell for: $$ACTIVE_CONTAINER"; \
		docker exec -it $$ACTIVE_CONTAINER /bin/bash; \
	else \
		echo "❌ No active hedge bot containers found"; \
		echo "Use 'make interactive' to start a new interactive container"; \
	fi

# Stop running containers
stop:
	@echo "🛑 Stopping hedge bot containers..."
	@for container in $$(docker ps --filter "ancestor=$(IMAGE_NAME)" --format "{{.Names}}"); do \
		echo "   Stopping: $$container"; \
		docker stop $$container; \
		docker rm $$container; \
	done
	@echo "✅ All hedge bot containers stopped"

# Stop specific container
stop-backpack:
	@echo "🛑 Stopping Backpack hedge bot..."
	@docker stop $(CONTAINER_NAME)-backpack 2>/dev/null || echo "Container not running"
	@docker rm $(CONTAINER_NAME)-backpack 2>/dev/null || echo "Container already removed"

stop-extended:
	@echo "🛑 Stopping Extended hedge bot..."
	@docker stop $(CONTAINER_NAME)-extended 2>/dev/null || echo "Container not running"
	@docker rm $(CONTAINER_NAME)-extended 2>/dev/null || echo "Container already removed"

# Show container status
status:
	@echo "📊 Hedge Bot Container Status:"
	@echo "════════════════════════════════════════════════════════════════"
	@docker ps --filter "ancestor=$(IMAGE_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}" || echo "No containers running"
	@echo ""
	@echo "📁 Log Files:"
	@ls -la logs/ 2>/dev/null || echo "No log files found"

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	@echo "Stopping containers..."
	@for container in $$(docker ps --filter "ancestor=$(IMAGE_NAME)" --format "{{.Names}}"); do \
		docker stop $$container; \
		docker rm $$container; \
	done
	@echo "Removing stopped containers..."
	@docker container prune -f --filter "ancestor=$(IMAGE_NAME)"
	@echo "Removing image..."
	@docker rmi $(IMAGE_NAME):$(DOCKER_TAG) 2>/dev/null || echo "Image not found"
	@echo "✅ Cleanup completed"

# Show help
help:
	@echo "🤖 Hedge Mode Trading Bot - Docker Management"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📦 BUILD COMMANDS:"
	@echo "  make build                    Build the Docker image"
	@echo ""
	@echo "🚀 RUN COMMANDS:"
	@echo "  make run-backpack TICKER=BTC SIZE=0.01 ITER=10 [TIMEOUT=5]"
	@echo "                               Run Backpack hedge mode"
	@echo ""
	@echo "  make run-extended TICKER=ETH SIZE=0.1 ITER=5 [TIMEOUT=5]"
	@echo "                               Run Extended hedge mode"
	@echo ""
	@echo "  make run EXCHANGE=backpack TICKER=BTC SIZE=0.01 ITER=10"
	@echo "                               Generic run command"
	@echo ""
	@echo "  make interactive             Start interactive container"
	@echo ""
	@echo "📋 MONITORING COMMANDS:"
	@echo "  make logs                     View real-time logs (auto-detect container)"
	@echo "  make logs-backpack           View Backpack container logs"
	@echo "  make logs-extended           View Extended container logs"
	@echo "  make status                  Show container status and log files"
	@echo ""
	@echo "🔧 MANAGEMENT COMMANDS:"
	@echo "  make shell                   Access running container shell"
	@echo "  make stop                    Stop all hedge bot containers"
	@echo "  make stop-backpack          Stop Backpack container"
	@echo "  make stop-extended          Stop Extended container"
	@echo "  make clean                   Remove containers and image"
	@echo ""
	@echo "📝 EXAMPLES:"
	@echo "  make build"
	@echo "  make run-backpack TICKER=BTC SIZE=0.01 ITER=100"
	@echo "  make logs"
	@echo "  make stop"
	@echo ""
	@echo "⚙️  ENVIRONMENT:"
	@echo "  ENV_FILE=$(ENV_FILE) (can be overridden: make run ENV_FILE=.env.prod ...)"
	@echo "  IMAGE_NAME=$(IMAGE_NAME)"
	@echo "  CONTAINER_NAME=$(CONTAINER_NAME)"