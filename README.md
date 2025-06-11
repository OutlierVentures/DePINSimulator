# DePIN Simulator

A sophisticated token economics modeling tool for Decentralized Physical Infrastructure Networks (DePIN) using optimal control theory and radCAD framework.

## 🚀 Current Status: Phase 1.5 Complete

**Production Ready**: Complete emission framework with 3 distinct emission policies, validated mathematical precision, and comprehensive testing suite.

## ✨ Key Features

- **🎯 Optimal Control Theory**: 5-component cost function J(x_0, π) for protocol optimization
- **📊 Complete Emission Framework**: Linear, Per-Device, and BME emission policies
- **🔬 Mathematical Precision**: radCAD-based dynamical systems modeling
- **🧪 Comprehensive Testing**: Validated 30-day simulations with policy differentiation
- **⚙️ Research Flexibility**: Configurable parameters for policy experimentation
- **📈 Real-time Analytics**: Emission cap utilization and network metrics tracking

## 📋 Emission Policies

The DePIN Simulator supports three distinct emission policies for distributing incentive tokens to node operators:

### 🔄 Linear Emission Policy

**Description**: Fixed daily emission rate over the vesting period, providing predictable token distribution.

**Configuration**:
```python
'emission_policy': ['linear']
'incentive_mode': ['fixed_rate']  # or 'fixed_weighted_rate'
```

**Behavior**: 
- Consistent daily emission (e.g., 6.85M tokens/day)
- Zero variance for budget predictability
- Independent of network activity or node count

**Use Case**: Ideal for protocols requiring predictable token distribution schedules and stable liquidity planning.

**Mathematical Formula**:
```
daily_emission = total_allocation / vesting_duration
```

### 📈 Per-Device Emission Policy

**Description**: Emissions scale proportionally with active node count, incentivizing network growth.

**Configuration**:
```python
'emission_policy': ['per_device']
'emission_per_device_daily': [100]      # Tokens per node per day
'emission_device_cap_daily': [500_000]  # Maximum daily emission
'emission_cap_enabled': [True]          # Enable cap enforcement
```

**Behavior**:
- Scales with network growth (nodes × daily_rate)
- Capped at maximum daily limit (500k tokens)
- Responds to node operator participation

**Use Case**: Perfect for incentivizing early network growth while preventing runaway emissions during rapid expansion.

**Mathematical Formula**:
```
device_emission = active_nodes × emission_per_device_daily
daily_emission = min(device_emission, emission_cap)  # if cap enabled
```

### ⚖️ BME (Burn-and-Mint Equilibrium) Policy

**Description**: Usage-driven emissions based on network activity, creating sustainable token economics.

**Configuration**:
```python
'emission_policy': ['bme']
'bme_burn_rate_multiplier': [1.0]       # Burn rate relative to network revenue
'bme_mint_rate_multiplier': [1.0]       # Mint rate relative to burn amount
'emission_device_cap_daily': [500_000]  # Optional cap
```

**Behavior**:
- Emissions correlate with network usage and revenue
- Self-regulating based on economic activity
- Configurable burn/mint ratios for fine-tuning

**Use Case**: Optimal for mature networks seeking sustainable token economics aligned with utility value.

**Mathematical Formula**:
```
burn_equivalent = network_revenue × bme_burn_rate_multiplier
daily_emission = burn_equivalent × bme_mint_rate_multiplier
```

### 📊 Policy Comparison Summary

| Policy | Daily Emission (30-day avg) | Variance | Cap Utilization | Best For |
|--------|----------------------------|----------|-----------------|----------|
| **Linear** | 6.85M tokens | 0% | N/A | Predictable schedules |
| **Per-Device** | 500k tokens | 0% | 194% | Network growth |
| **BME** | 7.7k tokens | 1.5k tokens | 1.6% | Usage-driven economics |

## 🛠 Installation

**Python 3.9+ and conda environment required**

### Quick Setup
```bash
# Clone repository
git clone https://github.com/OutlierVentures/DePINSimulator.git
cd DePINSimulator

# Create and activate conda environment
conda create -n depin python=3.9
conda activate depin

# Install dependencies
pip install -r requirements.txt
```

### Environment Requirements
⚠️ **Critical**: All Python commands must run in the `depin` conda environment for pandas/numpy compatibility.

## 🚀 Quick Start

### Basic Simulation
```python
# Run default simulation (linear emission)
python DePIN_Simulator.py
```

### Policy Comparison
```python
# Configure different emission policies in model/sys_params.py

# Linear emission (default)
'emission_policy': ['linear']

# Per-device emission
'emission_policy': ['per_device']
'emission_per_device_daily': [100]

# BME emission
'emission_policy': ['bme']
'bme_burn_rate_multiplier': [1.0]
'bme_mint_rate_multiplier': [1.0]
```

### Validation Testing
```bash
# Run Phase 1.5 completion validation
conda activate depin && python tests/diagnostics/phase_1_5_completion_validation.py

# Run specific emission policy tests
conda activate depin && python tests/diagnostics/bme_emission_policy_test.py
```

## ⚙️ Configuration

### Key Parameters

**Network Economics**:
```python
'initial_node_amount': [5000]              # Starting node count
'node_resource_provision_rate': [100000]   # Units per node per day
'resource_unit_price': [0.00002]          # Revenue per unit ($)
'apr_threshold': [15]                      # Target node operator APR (%)
```

**Token Economics**:
```python
'incentive_token_allocation': [0.5]        # 50% for node incentives
'incentive_token_vesting_duration': [730]  # 2-year emission period
'emission_cap_enabled': [True]            # Enable/disable emission caps
```

**BME Configuration**:
```python
'bme_burn_rate_multiplier': [1.0]         # Revenue-to-burn ratio
'bme_mint_rate_multiplier': [1.0]         # Burn-to-mint ratio
```

### Cost Function Weights
```python
# J(x_0, π) optimization targets
'cost_price_stability_weight': [0.30]      # Price stability (30%)
'cost_utilization_weight': [0.25]          # Network efficiency (25%)
'cost_foundation_weight': [0.20]           # Sustainability (20%)
'cost_profitability_weight': [0.15]        # Node profitability (15%)
'cost_decentralization_weight': [0.10]     # Decentralization (10%)
```

## 🧪 Testing

### Comprehensive Test Suite
```bash
# Complete emission framework validation
conda activate depin && python tests/diagnostics/phase_1_5_completion_validation.py

# Individual policy tests
conda activate depin && python tests/diagnostics/bme_emission_policy_test.py
conda activate depin && python tests/diagnostics/optional_cap_configuration_test.py
conda activate depin && python tests/diagnostics/multi_node_emission_test.py

# Foundation economics validation  
conda activate depin && python tests/diagnostics/foundation_economics_validation.py
```

### Expected Test Results
- **Linear Policy**: Perfect consistency (0% variance)
- **Per-Device Policy**: Node-scaled emissions with cap enforcement
- **BME Policy**: Usage-driven variability with network correlation
- **Cap Enforcement**: Proper limits at 500k daily maximum
- **Mathematical Precision**: All calculations validated

## 📈 Example Results
![Default Parameter Results](./img/default_results.jpg)

*Default simulation showing network growth, token economics, and cost function optimization over time.*

## 🗺 Development Roadmap

### Phase 1: Foundation & Cost Function Framework ✅ **COMPLETE**
- ✅ **Cost Function Implementation**: Full `J(x_0, π)` framework with 5 components
- ✅ **Real-time Policy Evaluation**: Cost calculated at each timestep
- ✅ **Mathematical Foundation**: radCAD-based modeling
- ✅ **Volt Capital Fixes**: Network utilization caps and economic constraints

### Phase 1.5: Emission Framework ✅ **COMPLETE**
- ✅ **Linear Emission Policy**: Fixed daily emission (baseline)
- ✅ **Per-Device Emission Policy**: Node-scaled with cap enforcement
- ✅ **BME Emission Policy**: Usage-driven burn-and-mint equilibrium
- ✅ **Optional Cap Configuration**: Research flexibility
- ✅ **Comprehensive Testing**: 30-day validation with policy differentiation
- ✅ **Foundation Economics**: Corrected burn rates and bankruptcy protection

### Phase 2: Optimal Control Theory & Policy Discovery 🎯 **NEXT**
- [ ] **Automated Policy Optimization**: Cost function minimization
- [ ] **Parameter Sweeps**: Sensitivity analysis across emission strategies
- [ ] **Dynamic Policy Adaptation**: Real-time parameter adjustment
- [ ] **Multi-objective Optimization**: Balance stability, growth, and sustainability

### Phase 3: Advanced Analytics & UI
- [ ] **Streamlit Interface**: Interactive policy comparison dashboard
- [ ] **Stress Testing**: Exogenous shock simulation
- [ ] **Machine Learning**: Predictive modeling and pattern recognition

### Phase 4: Production Framework
- [ ] **API Integration**: RESTful API for external tools
- [ ] **Research Platform**: Academic paper generation and dataset publication

---

**Current Status**: **Phase 1.5 Complete** ✅ - Full emission framework operational with 3 validated policies. Ready for Phase 2 optimal control theory and policy discovery research.

## 📊 Validation Results

**30-Day Simulation Results**:
- **Linear Emission**: 205.5M tokens total (perfect consistency)
- **Per-Device Emission**: 15M tokens total (node-scaled, capped)
- **BME Emission**: 232k tokens total (usage-driven, variable)

**Policy Differentiation**: ✅ Confirmed distinct emission patterns
**Cap Enforcement**: ✅ Working correctly across all scenarios  
**Mathematical Precision**: ✅ All calculations validated

## 🤝 Contributing

This project follows rigorous development standards:
- **Marginal Improvements**: Systematic incremental development
- **Comprehensive Testing**: Validation at each development stage
- **Economic Realism**: Parameters based on successful DePIN networks
- **Environment Protection**: All commands must use `conda activate depin`

## 📄 Disclaimer

The DePIN simulator has been prepared by Outlier Ventures ("OV") for educational and general information purposes only. No undertaking, warrant or other assurance is given as to the accuracy, adequacy, validity, reliability, fairness or completeness of any information. The simulator should not be considered a recommendation by OV. Users should conduct their own investigation and analysis. Under no circumstances shall OV have any liability for any loss or damage incurred as a result of using this simulator. Use is solely at the user's own risk.

## 📚 References

*Based on "Designing DePIN Protocols Using Optimal Control Theory" by [Volt Capital](https://volt.capital/blog/designing-depin-protocols-using-optimal-control-theory)*