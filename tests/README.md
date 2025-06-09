# DePIN Simulator Tests

## Structure

- `unit/` - Unit tests for individual functions and classes
- `integration/` - Integration tests for system components
- `diagnostics/` - Diagnostic scripts and validation tools (legacy)

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=model

# Run specific test directory
pytest tests/unit/
pytest tests/integration/

# Run diagnostic scripts
python tests/diagnostics/validation_check.py
python tests/diagnostics/demand_saturation_test.py
```

## Test Guidelines

- Unit tests: Test individual functions in isolation
- Integration tests: Test component interactions
- Property-based testing for financial calculations
- Test mathematical invariants and conservation laws
- Focus on `cost_functions.py`, `policy_functions.py`, `utils.py`

## Current Status

⚠️ **Test coverage is currently 0%** - This is a critical gap that needs addressing in Phase 2.

Legacy diagnostic scripts have been preserved in `diagnostics/` folder for reference. 