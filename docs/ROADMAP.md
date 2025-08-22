## DePIN Simulator Roadmap
*Updated: 2025-08-20*

### Status
**Current**: Business APR Controller Stabilization Complete - Advanced simulation framework with stable economic modeling
**Branch**: `v2-update` with business APR controller implementation complete
**Next**: UI Enhancement for Production/MVP Readiness - comprehensive user experience and feature completion

### Architecture Quality Assessment
- ✅ **Excellent foundation**: Modular design, comprehensive documentation, production configs
- ✅ **APR Controller Stability**: Business APR controller implemented with deadband and rate limiting
- ✅ **Production Configurations**: Multiple validated configs (realistic_economics, business_apr_test, etc.)
- ✅ **Custom Demand Schedules**: Multi-phase growth with milestone support fully operational
- 🔄 **UI Enhancement Focus**: Completing comprehensive user experience for production/MVP readiness

---

## Current Priority — UI Enhancement & Documentation (Priority: High)

**Goal**: Comprehensive external user documentation and UI experience optimization
**Timeline**: Ongoing
**Success Criteria**: External users can understand and use all functionalities effectively

### ✅ Business APR Controller Stabilization (COMPLETED)
**Achievement**: Successfully resolved APR controller instabilities through business fundamentals approach
**Solution**: Separated business APR from token price fluctuations for realistic node operator economics

**Technical Implementation Completed**:
- ✅ Business APR calculation implemented separate from display APR
- ✅ Controller operates on business metrics with proper deadband and rate limiting
- ✅ Hysteresis and bounded overshoot constraints implemented
- ✅ Smooth convergence validated with multiple production configurations

**Files Modified**:
- `model/policy_functions.py`: Enhanced `p_node_apr_controller()` with business APR logic
- `model/state_variables.py`: Added `calculate_expected_initial_business_apr()` function

**Results Achieved**: 
- ✅ All timesteps show realistic APR progression without spikes
- ✅ Smooth convergence to target APR across all production configurations
- ✅ 365-day runs complete with stable controller behavior
- ✅ Natural equilibrium approach validated as alternative to controller-based systems

### 1️⃣ Node Decision Model Enhancement 
**Focus**: Dual APR controller framework with configurable weighting

**Enhancement Goal**:
- **Current**: Business APR controller (business fundamentals only)
- **Target**: Parallel computation of fundamentals APR + emission APR with weighted decision making
- **User Control**: Simple qualitative selection (fundamentals-focused / emission-focused / balanced)

**Technical Implementation**:
- **Dual Controller Framework**: Compute both `fundamentals_apr` and `emission_apr` in parallel
- **Weighted Decision Logic**: `decision_apr = fundamentals_apr * fund_weight + emission_apr * emiss_weight`
- **Parameter Mapping**: fundamentals_focused (1.0, 0.0), emission_focused (0.0, 1.0), balanced (0.5, 0.5)
- **UI Integration**: Dropdown "Node operators optimize for: Fundamentals / Emissions / Balanced"

**Files to Edit**:
- `model/policy_functions.py`: Enhanced APR calculation in `p_node_changes`
- `streamlit_app.py`: UI parameter for node decision model selection
- Production configs: Default weighting selections for different scenarios

**Acceptance**:
- ✅ Users can select node operator optimization focus qualitatively via UI dropdown
- ✅ Dual controller framework computes both APR types in parallel
- ✅ Weighted decision logic affects node entrance/exit behavior appropriately
- ✅ Clear documentation explaining fundamentals vs emission APR optimization

### 2️⃣ Configuration Management Overhaul
**Focus**: Review and update all configuration files for current framework

**Current Issue**: Many configs may be outdated after business APR controller implementation
**Goal**: Clean, validated, well-documented configuration library

**Technical Changes**:
- **Audit all configs**: Review each config for compatibility with current framework
- **Remove outdated configs**: Delete deprecated or non-functional configurations  
- **Standardize parameters**: Ensure all configs use current parameter names and ranges
- **Enhanced documentation**: Add clear descriptions and use cases for each config
- **Validation testing**: Ensure all remaining configs complete 365-day simulations successfully

**Files to Review**:
- `config/production/`: All production configurations
- `config/research/`: Research and testing configurations
- `config/templates/`: Template files and documentation

**Acceptance**:
- ✅ All remaining configs are validated and functional
- ✅ Clear documentation for each config's purpose and economic model
- ✅ Removal of any outdated or broken configurations

### 3️⃣ UI Enhancement & Founder Dashboard 
**Focus**: Complete visualization suite and optimal control theory integration

**Chart Additions**:
- **Network tab**: Daily node change (Δ nodes/day) time series
- **Economics tab**: Node expenditures time series  
- **Token tab**: Cumulative token vesting (incentives + seller) over time
- **Token tab**: Token ecosystem supply (total + circulating, absolute + % of initial)

**Founder Dashboard Integration**:
- **Protocol Score**: Real-time J(x_0, π) cost function display with component breakdown
- **Optimization Insights**: Show which policy components are performing well/poorly
- **Policy Comparison**: Side-by-side cost function analysis for different configurations
- **Performance Metrics**: Key founder-focused metrics derived from optimal control theory

**Technical Changes**:
- Add chart generation functions with consistent titles/units
- Implement log-scale guards for all charts (prevent errors on non-positive values)
- Add optimal control theory cost function visualization in Founder Dashboard tab
- Add optional HTML export functionality (default: no PNG saving)

**Files to Edit**:
- `streamlit_app.py`: Chart generation and Founder Dashboard sections
- `model/cost_functions.py`: Integration for real-time cost calculation display

**Acceptance**:
- ✅ All mentioned charts present and error-free
- ✅ Founder Dashboard shows real-time optimal control theory insights
- ✅ Protocol score and component breakdown visible and actionable
- ✅ Charts render correctly across different parameter configurations
- ✅ Optional HTML export works without breaking existing functionality

### 4️⃣ UI Parameter Persistence Enhancement 
**Focus**: Robust handling of complex parameter configurations

**Technical Changes**:
- Validate complex nested parameter handling in save/load cycle
- Ensure `business_growth_phases` and `business_demand_milestones` roundtrip correctly
- Test UI scalar/boolean parameter conversion edge cases
- Persist run configuration alongside results (params.json + summary section)

**Files to Edit**:
- `streamlit_app.py`: Parameter saving/loading logic
- `model/run.py`: Configuration persistence in output

**Acceptance**:
- ✅ Complex growth scenarios save and load correctly from UI
- ✅ All parameter types (scalar, list, boolean) handled consistently  
- ✅ Run reports include complete parameter snapshot for reproducibility

**Current Deliverables - Path to Production/MVP**:
- ✅ APR controller stability achieved across all production configurations
- 🔄 Node decision model enhancement (fundamentals vs emission APR dual controller)
- 🔄 UI Enhancement & Founder Dashboard (optimal control theory integration)
- 🔄 Configuration management overhaul (audit and update all configs)  
- 🔄 Complete chart set with proper error handling and export options
- ✅ Custom demand schedule support fully operational with UI integration
- ✅ Enhanced external user documentation and functionality recap

---

## P1 — Production Configuration Sets (Priority: High)

**Goal**: Curated, documented preset configurations ready for production use  
**Timeline**: 3-4 days after P0  
**Success Criteria**: 4-5 preset configurations with rich metadata and expected outcomes

### 1️⃣ Enhanced Configuration Metadata
**Current**: Basic JSON configs with minimal description  
**Target**: Rich metadata with expected behaviors and parameter guidance

**Configuration Enhancements**:
- Expand `_metadata` with intended behavior descriptions
- Add parameter sensitivity warnings and recommended ranges
- Include expected chart patterns and key metrics to watch  
- Document parameter trade-offs and interaction effects

**New Production Presets**:
- **Founder Scenario Example**: Balanced growth, 15-25% APR, 60-85% utilization
- **Conservative Bootstrap**: Lower emissions, longer vesting, stable reserves  
- **Usage-Driven BME**: Emission tied to usage, demonstrate cap behavior
- **Sustainable Per-Device**: Node-scaled with reasonable emission caps
- **High-Growth Stress**: Aggressive demand growth, controllers ON, dynamic pricing

**Files to Edit**:
- `config/production/*.json`: Enhanced metadata and documentation  
- `config/templates/base_template.json`: Documentation standards

**UI Integration**:
- Configuration selector shows rich descriptions
- In-app guidance for parameter interpretation  
- Clear warnings about parameter interactions

**Acceptance**:
- ✅ 4-5 production configurations with comprehensive documentation
- ✅ Each config includes expected behavior and outcome guidance  
- ✅ UI selector exposes rich metadata to users
- ✅ All configs validated with successful 365-day runs

### 2️⃣ Parameter Validation Framework
**Goal**: Enhanced constraint checking and economic feasibility validation

**Technical Implementation**:
- Expand `validate_params()` with comprehensive economic checks
- Add parameter interaction warnings (e.g., high growth + low APR)
- Implement feasibility bounds (payback period, runway calculations)
- Add configuration comparison tools

**Files to Edit**:  
- `model/sys_params.py`: Enhanced validation functions
- `config_loader.py`: Validation integration

**Acceptance**:
- ✅ Comprehensive parameter validation prevents economically infeasible configs
- ✅ Clear warnings for parameter combinations likely to cause instability
- ✅ Automated feasibility checks (payback periods, runway estimates)

**Deliverables for P1**:
- Production-ready configuration library with rich documentation
- Enhanced parameter validation preventing economic infeasibilities  
- UI integration exposing configuration guidance to users

---

## P2 — Protocol Score Integration (Priority: Optional)

**Goal**: Integrate cost function framework into UI for real-time protocol evaluation  
**Timeline**: 2-3 days (if time permits)  
**Success Criteria**: Protocol Score displayed in UI with component breakdown

### 1️⃣ Cost Function UI Integration
**Current**: Cost function J(x₀,π) calculated but not exposed  
**Target**: Real-time protocol scoring in UI header

**Technical Implementation**:
- Convert cost components to normalized sub-scores (0-100)
- Apply established weights from `cost_functions.py`
- Display topline Protocol Score with breakdown tooltips
- Add component trend analysis over time

**UI Design**:
- Protocol Score in header (100 = ideal)
- Expandable breakdown showing individual component scores
- Time series chart of score evolution
- Component weight visualization

**Files to Edit**:
- `streamlit_app.py`: Protocol Score UI elements
- `model/cost_functions.py`: Score normalization if needed

**Acceptance**:
- ✅ Protocol Score visible in UI header with intuitive 0-100 scale
- ✅ Component breakdown available with tooltips explaining each factor  
- ✅ Score calculation reproducible from same postprocessing used for charts

**Deliverables for P2**:
- Protocol Score MVP integrated into UI
- Real-time cost function feedback during simulations
- Component-level analysis for protocol optimization

---

## Testing Philosophy

### Current Approach: "Stabilize First, Test Second"
**Rationale**: Testing unstable controllers provides false confidence  
**Strategy**: Fix core mathematical functions, then add high-signal validation

### Minimal Testing Framework (Post-P0)
**Focus Areas**:
- **Invariants**: Utilization ≤ 1.0, reserves non-negative, emissions ≤ budget
- **Math Correctness**: Emission policy calculations, controller bounds
- **Integration**: Short simulation asserting expected column presence

**Test Implementation** (if time permits):
```bash
# Critical mathematical functions only
tests/unit/test_emission_policies.py      # Linear, Per-Device, BME calculations  
tests/unit/test_controller_bounds.py      # APR controller stability
tests/unit/test_param_validation.py       # Economic constraint checking

# Integration validation  
tests/integration/test_simulation_flow.py # End-to-end with invariant checking
```

**Not in Scope**: Comprehensive coverage, UI testing, edge case exploration

---

## Success Metrics & Milestones

### P0 Success Criteria (Days 1-7)
- [ ] **APR Stability**: No spikes >50% in any simulation timestep  
- [ ] **Complete Charts**: All roadmap-mentioned visualizations present
- [ ] **UI Reliability**: Complex parameter configurations save/load correctly
- [ ] **Stability Validation**: 365-day simulation completes without mathematical errors

### P1 Success Criteria (Days 8-11)  
- [ ] **Production Configs**: 4-5 documented presets with expected outcome guidance
- [ ] **Parameter Validation**: Enhanced constraint checking prevents infeasible configs
- [ ] **User Experience**: Configuration selection with in-app guidance

### P2 Success Criteria (Days 12-14, Optional)
- [ ] **Protocol Score**: Real-time cost function integration in UI
- [ ] **Component Analysis**: Breakdown of score factors with trend visualization

### Overall Success Definition
**Core Achievement**: Reliable, well-documented DePIN simulation platform  
**Quality Standard**: Production-ready with comprehensive configuration library  
**User Experience**: Intuitive parameter selection with outcome guidance  
**Technical Excellence**: Stable mathematical functions with proper error handling

---

## Risk Assessment & Mitigation

### High-Risk Items
1. **APR Controller Fix**: Complex PID tuning may require multiple iterations
   - *Mitigation*: Start with conservative gains, validate incrementally
2. **UI Parameter Complexity**: Nested configuration persistence edge cases  
   - *Mitigation*: Comprehensive roundtrip testing for all parameter types

### Success Dependencies
- **radCAD Sequencing**: Maintain proper block execution order (timestep ≥2 requirements)
- **Parameter Compatibility**: Preserve backward compatibility with existing configs
- **Performance**: Chart generation must remain responsive with large datasets

**Implementation Philosophy**: Incremental improvements with validation at each step