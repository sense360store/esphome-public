# Development Guide

This guide covers setting up your development environment and contributing to the Sense360 ESPHome firmware repository.

## Table of Contents

- [Development Setup](#development-setup)
- [Testing](#testing)
- [Pre-commit Hooks](#pre-commit-hooks)
- [CI/CD Pipeline](#cicd-pipeline)
- [Code Quality](#code-quality)

## Development Setup

### Prerequisites

- Python 3.11 or newer
- Git
- ESPHome 2025.10.0 or newer

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sense360store/esphome-public.git
   cd esphome-public
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Testing

### Validate YAML Configurations

Run the validation script to check all YAML files:

```bash
python3 tests/validate_configs.py
```

This validates:
- YAML syntax
- ESPHome configuration structure
- Required keys and sections
- Package references

### Test ESPHome Compilation

Validate the Release-One product configuration
(`Ceiling-POE-VentIQ-RoomIQ`):

```bash
esphome config products/sense360-ceiling-poe-ventiq-roomiq.yaml
```

Validate a legacy-compatible Mini product (not Release-One):

```bash
esphome config products/sense360-mini-airiq.yaml
```

Test all product configurations (broad legacy sweep — not the Release-One
gate):

```bash
for file in products/*.yaml; do
  echo "Testing: $file"
  esphome config "$file"
done
```

### Run Unit Tests

Execute the LED logic unit tests:

```bash
esphome config tests/esphome/test_led_logic.yaml
```

## Pre-commit Hooks

Pre-commit hooks automatically validate your changes before committing.

### What Gets Checked

- **Trailing whitespace**: Removed automatically
- **End of file fixing**: Ensures files end with newline
- **YAML validation**: Checks syntax and structure
- **YAML linting**: Enforces style guidelines
- **Python formatting**: Black auto-formatter
- **Python linting**: Flake8 code quality checks
- **C++ formatting**: Clang-format for header files
- **ESPHome validation**: Product config validation

### Running Manually

Run all hooks on all files:

```bash
pre-commit run --all-files
```

Run a specific hook:

```bash
pre-commit run yamllint --all-files
```

### Skipping Hooks (Not Recommended)

If you need to commit without running hooks:

```bash
git commit --no-verify
```

**Warning**: CI will still run all checks on push.

## CI/CD Pipeline

### GitHub Actions Workflows

The repository includes automated testing on every push and pull request.

#### Workflow: `validate.yml` (Fast)

Quick validation that runs first:
- YAML syntax checking
- Configuration structure validation
- Runs in ~30 seconds

#### Workflow: `test.yml` (Comprehensive)

Full test suite:
- **validate-yaml**: YAML syntax and linting
- **test-esphome-configs**: Compiles all 10 product configs
- **test-unit-tests**: Runs ESPHome test configurations
- **lint-cpp**: Checks C++ header formatting

> The Release-One build/release gate is
> [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml),
> which builds only the Release-One configuration
> (`Ceiling-POE-VentIQ-RoomIQ`) from
> [`products/sense360-ceiling-poe-ventiq-roomiq.yaml`](../products/sense360-ceiling-poe-ventiq-roomiq.yaml).
> The matrix below belongs to the broad legacy / Mini-board CI sweep
> ([`ci-validate-configs.yml`](../.github/workflows/ci-validate-configs.yml))
> and is **not** the Release-One PR gate.

Matrix testing across product configurations (legacy sweep — not the
Release-One gate):

- `sense360-ceiling-poe-ventiq-roomiq.yaml` — _Release-One; gated by
  [`firmware-build-release.yml`](../.github/workflows/firmware-build-release.yml)._
- `sense360-mini-airiq.yaml` — _legacy-compatible_
- `sense360-mini-airiq-basic.yaml` — _legacy-compatible_
- `sense360-mini-airiq-advanced.yaml` — _legacy-compatible_
- `sense360-mini-airiq-ld2412.yaml` — _legacy-compatible_
- `sense360-mini-presence.yaml` — _legacy-compatible_
- `sense360-mini-presence-basic.yaml` — _legacy-compatible_
- `sense360-mini-presence-advanced.yaml` — _legacy-compatible_
- `sense360-mini-presence-ld2412.yaml` — _legacy-compatible_
- `sense360-ceiling-presence.yaml` — _legacy-compatible_
- `sense360-ceiling-presence-ld2412.yaml` — _legacy-compatible_

### Viewing Test Results

1. Navigate to the **Actions** tab on GitHub
2. Select a workflow run
3. Click on individual jobs to see detailed logs
4. Failed checks will show specific error messages

### Local CI Simulation

Run the same checks locally before pushing:

```bash
# Quick validation
python3 tests/validate_configs.py

# Full ESPHome validation
for file in products/*.yaml; do
  esphome config "$file"
done

# Pre-commit checks
pre-commit run --all-files
```

## Code Quality

### YAML Style Guide

- **Indentation**: 2 spaces
- **Line length**: Max 120 characters (warning only)
- **Comments**: At least 1 space from content
- **Naming**: Use snake_case for IDs and substitutions

Example:

```yaml
substitutions:
  device_name: sensor-living-room
  friendly_name: "Living Room Sensor"

sensor:
  - platform: template
    name: "${friendly_name} Temperature"
    id: room_temperature
    unit_of_measurement: "°C"
```

### Python Style Guide

- **Formatter**: Black (line length: 120)
- **Linter**: Flake8
- **Type hints**: Recommended for new code
- **Docstrings**: Required for public functions

### C++ Style Guide

- **Formatter**: clang-format
- **Naming**: Follow ESPHome conventions
- **Headers**: Include guards required
- **Namespaces**: Use `sense360::` prefix

## Adding New Tests

### Unit Test Structure

Create a new test file in `tests/esphome/`:

```yaml
# tests/esphome/test_new_feature.yaml
substitutions:
  device_name: test-new-feature
  friendly_name: "Test New Feature"

esphome:
  name: ${device_name}
  includes:
    - ../../include/sense360/new_feature.h

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: arduino

script:
  - id: test_feature
    then:
      - lambda: |-
          // Your test code here
          ESP_LOGI("test", "Testing new feature...");
```

### Validation Script

To add custom validation rules, edit `tests/validate_configs.py`:

```python
def validate_custom_rule(self, file_path: Path) -> bool:
    """Add your custom validation logic."""
    # Implementation
    return True
```

## Troubleshooting

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Review the error messages
2. Fix issues manually or let auto-formatters fix them
3. Re-run `git add` on modified files
4. Try committing again

### ESPHome Compilation Errors

Common issues:

- **Missing secrets**: Copy `secrets.example.yaml` to `secrets.yaml`
  (`cp secrets.example.yaml secrets.yaml`). `secrets.yaml` is gitignored.
- **Platform not found**: Update ESPHome to latest version
- **Component errors**: Check ESPHome version compatibility

### CI Failures

If CI fails but local tests pass:

1. Check if you're using the same Python/ESPHome versions
2. Ensure all dependencies are installed
3. Review CI logs for specific errors
4. Test with a clean checkout

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pre-commit run --all-files`
5. Commit with descriptive messages
6. Push to your fork
7. Create a pull request

### Commit Message Guidelines

- Use present tense: "Add feature" not "Added feature"
- Keep first line under 72 characters
- Reference issues: "Fix #123: Description"

Example:

```
Add validation for presence sensor configs

- Validate LD2450 UART configuration
- Check required substitutions
- Add warning for missing timeout settings

Fixes #456
```

## Resources

- [ESPHome Documentation](https://esphome.io)
- [Pre-commit Documentation](https://pre-commit.com)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [YAML Specification](https://yaml.org/spec/)
