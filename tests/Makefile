# Makefile for ESPHome unit tests
# Compiles and runs native C++ tests for extracted logic

CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -I./include -O2
LDFLAGS = -lm

# Directories
SRC_DIR = unit
BUILD_DIR = build
BIN_DIR = bin

# Test files
TEST_SOURCES = $(wildcard $(SRC_DIR)/test_*.cpp)
TEST_BINARIES = $(patsubst $(SRC_DIR)/%.cpp,$(BIN_DIR)/%,$(TEST_SOURCES))

# Colors for output
GREEN = \033[0;32m
RED = \033[0;31m
NC = \033[0m # No Color
BOLD = \033[1m

.PHONY: all clean test run_tests help

# Default target
all: $(TEST_BINARIES)

# Create directories
$(BUILD_DIR) $(BIN_DIR):
	@mkdir -p $@

# Compile each test
$(BIN_DIR)/%: $(SRC_DIR)/%.cpp | $(BIN_DIR)
	@echo "$(BOLD)Compiling $<...$(NC)"
	@$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)
	@echo "$(GREEN)✓ Built $@$(NC)"

# Run all tests
test: $(TEST_BINARIES)
	@echo ""
	@echo "$(BOLD)========================================$(NC)"
	@echo "$(BOLD)  Running All Tests$(NC)"
	@echo "$(BOLD)========================================$(NC)"
	@echo ""
	@EXIT_CODE=0; \
	for test in $(TEST_BINARIES); do \
		echo "$(BOLD)Running $$test...$(NC)"; \
		if ./$$test; then \
			echo "$(GREEN)✓ $$test PASSED$(NC)"; \
		else \
			echo "$(RED)✗ $$test FAILED$(NC)"; \
			EXIT_CODE=1; \
		fi; \
		echo ""; \
	done; \
	echo "$(BOLD)========================================$(NC)"; \
	if [ $$EXIT_CODE -eq 0 ]; then \
		echo "$(GREEN)$(BOLD)All tests passed!$(NC)"; \
	else \
		echo "$(RED)$(BOLD)Some tests failed!$(NC)"; \
	fi; \
	echo "$(BOLD)========================================$(NC)"; \
	exit $$EXIT_CODE

# Run individual test
run_%: $(BIN_DIR)/%
	@echo "$(BOLD)Running $<...$(NC)"
	@./$<

# Quick test (compile and run immediately)
quick: all test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(BIN_DIR)
	@echo "$(GREEN)✓ Clean complete$(NC)"

# Help target
help:
	@echo "$(BOLD)ESPHome Test Suite$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo "  $(BOLD)make all$(NC)          - Compile all tests"
	@echo "  $(BOLD)make test$(NC)         - Run all tests"
	@echo "  $(BOLD)make quick$(NC)        - Compile and run all tests"
	@echo "  $(BOLD)make run_<test>$(NC)   - Run specific test (e.g., make run_test_led_logic)"
	@echo "  $(BOLD)make clean$(NC)        - Remove build artifacts"
	@echo "  $(BOLD)make help$(NC)         - Show this help message"
	@echo ""
	@echo "Individual tests:"
	@for test in $(TEST_SOURCES); do \
		basename=`basename $$test .cpp`; \
		echo "  - $$basename"; \
	done

# Show test coverage summary (basic)
coverage:
	@echo "$(BOLD)Test Coverage Summary$(NC)"
	@echo "========================================"
	@echo "Header files:"
	@ls -1 ../include/sense360/*.h | wc -l | xargs echo "  Total headers:"
	@echo ""
	@echo "Test files:"
	@ls -1 $(SRC_DIR)/test_*.cpp | wc -l | xargs echo "  Total test files:"
	@echo ""
	@echo "Test executables:"
	@echo "  $(words $(TEST_BINARIES)) tests"
	@echo "========================================"

# Generate detailed coverage report with gcov
coverage-report: clean
	@echo "$(BOLD)Generating coverage report...$(NC)"
	@mkdir -p $(BIN_DIR) coverage
	@for src in $(SRC_DIR)/test_*.cpp; do \
		name=$$(basename $$src .cpp); \
		echo "Compiling $$name with coverage..."; \
		$(CXX) -std=c++11 -Wall -Wextra -I../include -O0 --coverage \
			-fprofile-arcs -ftest-coverage \
			$$src -o $(BIN_DIR)/$$name -lm; \
	done
	@echo ""
	@echo "$(BOLD)Running tests for coverage...$(NC)"
	@for test in $(BIN_DIR)/test_*; do \
		if [ -x "$$test" ]; then \
			./$$test || true; \
		fi; \
	done
	@echo ""
	@echo "$(BOLD)Generating HTML report...$(NC)"
	@gcovr --root ../include \
		--exclude-unreachable-branches \
		--exclude-throw-branches \
		-s \
		--html coverage/index.html \
		--html-details \
		--xml coverage/coverage.xml \
		. 2>/dev/null || echo "$(RED)gcovr not installed. Run: pip install gcovr$(NC)"
	@echo ""
	@echo "$(GREEN)Coverage report generated in coverage/index.html$(NC)"

# Clean coverage artifacts
clean-coverage:
	@rm -rf coverage *.gcda *.gcno $(BIN_DIR)/*.gcda $(BIN_DIR)/*.gcno
