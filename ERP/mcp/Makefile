# ERP MCP Server Makefile

.PHONY: help install start test clean deactivate

help: ## Show this help message
	@echo "ERP MCP Server Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and setup virtual environment
	@echo "Installing ERP MCP Server..."
	@./install.sh

start: ## Start the MCP server
	@echo "Starting ERP MCP Server..."
	@./start_server.sh

test: ## Run tests
	@echo "Running tests..."
	@./test_with_venv.sh

clean: ## Remove virtual environment
	@echo "Cleaning up..."
	@rm -rf venv/
	@echo "Virtual environment removed"

deactivate: ## Deactivate virtual environment
	@echo "To deactivate virtual environment, run: deactivate"

setup: install ## Alias for install

run: start ## Alias for start

check: ## Check if virtual environment exists
	@if [ -d "venv" ]; then \
		echo "✓ Virtual environment exists"; \
	else \
		echo "✗ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi

deps: ## Show installed dependencies
	@echo "Installed dependencies:"
	@source venv/bin/activate && pip list

update: ## Update dependencies
	@echo "Updating dependencies..."
	@source venv/bin/activate && pip install --upgrade -r requirements.txt
