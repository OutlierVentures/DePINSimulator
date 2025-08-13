# 🧬 PRD: EvoDePIN - Evolutionary Algorithm Integration for DePIN Simulator

**Version**: 2.0  
**Date**: January 2025  
**Status**: Implementation Ready  
**Priority**: High - Phase 2 Development  

---

## 🎯 Executive Summary

This PRD defines the technical specification for integrating evolutionary algorithms (EA) into the DePIN Simulator to automatically discover optimal token economic configurations. The EvoDePIN module will treat the current simulation as a black-box fitness evaluator, evolving parameter sets to minimize the existing 5-component cost function `J(x_0, π)`.

**Success Metrics**: 
- Automated discovery of parameter sets with 20%+ lower cost than baseline configurations
- Full integration with existing radCAD simulation framework  
- Reproducible experiment pipeline with visualization and reporting

---

## 📋 Current State Analysis

### Existing Architecture Strengths
✅ **Mature Simulation Framework**: radCAD-based with 3,650 timestep capacity  
✅ **Comprehensive Parameter Space**: 25+ tunable parameters in `sys_params.py`  
✅ **Established Cost Function**: 5-component optimization framework in `cost_functions.py`  
✅ **Rich Output Metrics**: 30+ KPIs extracted via `run.postprocessing()`  
✅ **Robust Testing**: Extensive diagnostic test suite in `tests/diagnostics/`  

### Integration Opportunities
🎯 **Parameter Injection**: Direct integration with `sys_params` dictionary structure  
🎯 **Fitness Evaluation**: Leverage existing `calculate_step_cost()` and `calculate_cumulative_cost()`  
🎯 **Simulation Wrapper**: Abstract `radCAD.Simulation.run()` for genome evaluation  
🎯 **Result Analysis**: Extend current visualization pipeline for EA results  

---

## 🏗️ Technical Architecture

### Directory Structure
```
evodepin/                           # New EA module
├── __init__.py                     # Package initialization
├── config/
│   ├── evolution_config.yaml       # EA hyperparameters
│   ├── parameter_bounds.yaml       # Gene value constraints
│   └── fitness_weights.yaml        # Cost function customization
├── core/
│   ├── genome.py                   # TokenGenome class definition
│   ├── simulation_wrapper.py       # radCAD simulation interface
│   ├── fitness_evaluator.py        # Cost extraction and aggregation
│   └── evolution_engine.py         # DEAP-based EA implementation
├── algorithms/
│   ├── nsga_ii.py                  # Multi-objective optimization
│   ├── differential_evolution.py   # Robust single-objective EA
│   └── particle_swarm.py           # Alternative optimization approach
├── analysis/
│   ├── convergence_plots.py        # Fitness over generations
│   ├── parameter_analysis.py       # Gene distribution analysis
│   ├── kpi_visualization.py        # Economic metric plotting
│   └── results_export.py           # Markdown/JSON output
├── experiments/
│   ├── baseline_comparison.py      # Benchmark against default params
│   ├── sensitivity_analysis.py     # Parameter importance ranking
│   └── multi_objective_pareto.py   # Trade-off analysis
└── evolve_tokenomics.py            # Main execution script
```

### Dependencies Integration
```python
# New requirements.txt additions
deap>=1.4.1              # Evolutionary algorithms framework
nevergrad>=0.12.0        # Alternative EA library
pyyaml>=6.0              # Configuration file parsing
joblib>=1.3.0            # Parallel simulation execution
seaborn>=0.12.0          # Enhanced plotting for EA results
```

---

## 🧬 Core Components Specification

### 1. TokenGenome Class (`core/genome.py`)

```python
@dataclass
class TokenGenome:
    """
    Encapsulates DePIN protocol parameters as evolvable genes
    Maps directly to sys_params.py structure for seamless integration
    """
    
    # Node Economics Genes (5 parameters)
    node_setup_cost: float              # [500, 5000] USD
    node_resource_provision_rate: float  # [10000, 1000000] units/day
    node_token_stake: float             # [1000, 50000] tokens
    apr_threshold: float                # [5, 50] percent
    node_growth_cap: float              # [1, 20] percent daily
    
    # Network Economics Genes (3 parameters)  
    resource_unit_price: float          # [0.000001, 0.001] USD/unit
    network_resource_demand_growth_rate: float  # [0.001, 0.1] daily
    initial_network_resource_demand: float     # [1e6, 1e10] units
    
    # Revenue Distribution Genes (3 parameters - constrained sum)
    node_revenue_share: float           # [0.6, 0.9] (auto-adjust others)
    foundation_revenue_share: float     # [0.05, 0.35] 
    buyback_revenue_share: float        # [0.001, 0.1]
    
    # Token Economics Genes (4 parameters)
    incentive_token_allocation: float    # [0.3, 0.7]
    seller_token_allocation: float      # [0.2, 0.5] 
    incentive_vesting_duration: float   # [180, 1095] days
    seller_vesting_duration: float     # [365, 1825] days
    
    # Controller Tuning Genes (3 parameters)
    apr_controller_kp: float            # [0.1, 2.0] proportional gain
    apr_controller_ki: float            # [0.001, 0.2] integral gain  
    apr_controller_kd: float            # [0.0001, 0.1] derivative gain
    
    def to_sys_params(self) -> Dict[str, List[float]]:
        """Convert genome to sys_params format for simulation"""
        
    def validate_constraints(self) -> bool:
        """Ensure economic constraints (revenue shares sum to 1.0, etc.)"""
        
    def mutate(self, mutation_rate: float = 0.1) -> 'TokenGenome':
        """Apply Gaussian mutation within parameter bounds"""
        
    def crossover(self, other: 'TokenGenome') -> Tuple['TokenGenome', 'TokenGenome']:
        """Uniform crossover between two genomes"""
```

### 2. Simulation Wrapper (`core/simulation_wrapper.py`)

```python
class DePINSimulationWrapper:
    """
    Abstracts radCAD simulation for genome evaluation
    Handles parameter injection, execution, and result extraction
    """
    
    def __init__(self, timesteps: int = 365, monte_carlo_runs: int = 1):
        self.timesteps = timesteps
        self.monte_carlo_runs = monte_carlo_runs
        self._base_state = initial_state  # From state_variables.py
        self._base_blocks = state_update_blocks  # From state_update_blocks.py
    
    def simulate_genome(self, genome: TokenGenome) -> SimulationResult:
        """
        Execute full radCAD simulation with genome parameters
        
        Returns:
            SimulationResult: Dataframe + extracted KPIs + cost metrics
        """
        # 1. Convert genome to sys_params format
        params = genome.to_sys_params()
        
        # 2. Create radCAD model with injected parameters
        model = Model(
            initial_state=self._base_state,
            params=params,
            state_update_blocks=self._base_blocks
        )
        
        # 3. Execute simulation
        simulation = Simulation(model=model, timesteps=self.timesteps, runs=self.monte_carlo_runs)
        result = simulation.run()
        
        # 4. Process results using existing pipeline
        df = pd.DataFrame(result)
        processed_df = run.postprocessing(df)
        
        # 5. Calculate fitness metrics
        return SimulationResult(
            raw_data=df,
            processed_data=processed_df,
            fitness_score=self._calculate_fitness(processed_df),
            kpi_summary=self._extract_kpis(processed_df)
        )
    
    def _calculate_fitness(self, df: pd.DataFrame) -> float:
        """Use existing cost_functions.py for fitness calculation"""
        
    def _extract_kpis(self, df: pd.DataFrame) -> Dict[str, float]:
        """Extract key performance indicators for analysis"""
```

### 3. Evolution Engine (`core/evolution_engine.py`)

```python
class EvolutionEngine:
    """
    DEAP-based evolutionary algorithm implementation
    Supports multiple EA strategies with configurable parameters
    """
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.simulator = DePINSimulationWrapper(
            timesteps=config.simulation_timesteps,
            monte_carlo_runs=config.monte_carlo_runs
        )
        self.toolbox = self._setup_deap_toolbox()
        
    def evolve(self) -> EvolutionResult:
        """
        Main evolution loop with configurable algorithm
        
        Returns:
            EvolutionResult: Best genomes, fitness history, Pareto fronts
        """
        # 1. Initialize population
        population = self._create_initial_population()
        
        # 2. Evolution loop with progress tracking
        fitness_history = []
        best_genomes = []
        
        for generation in tqdm(range(self.config.generations)):
            # Evaluate fitness (parallelized)
            fitnesses = self._evaluate_population_parallel(population)
            
            # Selection, crossover, mutation
            population = self._evolve_generation(population, fitnesses)
            
            # Track progress
            best_genome = self._get_best_individual(population, fitnesses)
            best_genomes.append(best_genome)
            fitness_history.append(fitnesses)
            
            # Early stopping criteria
            if self._check_convergence(fitness_history):
                break
                
        return EvolutionResult(
            best_genomes=best_genomes,
            final_population=population,
            fitness_history=fitness_history,
            convergence_data=self._analyze_convergence(fitness_history)
        )
    
    def _evaluate_population_parallel(self, population: List[TokenGenome]) -> List[float]:
        """Parallel genome evaluation using joblib"""
        
    def _setup_deap_toolbox(self) -> base.Toolbox:
        """Configure DEAP framework for TokenGenome evolution"""
```

### 4. Multi-Objective Support (`algorithms/nsga_ii.py`)

```python
class MultiObjectiveEvolution:
    """
    NSGA-II implementation for multi-objective optimization
    Optimizes trade-offs between cost function components
    """
    
    def __init__(self, objectives: List[str]):
        self.objectives = objectives  # e.g., ['price_stability', 'utilization_efficiency']
        
    def evolve_pareto_front(self, population_size: int = 100, generations: int = 50) -> ParetoFront:
        """
        Find Pareto-optimal solutions for multi-objective optimization
        
        Returns:
            ParetoFront: Non-dominated solutions with trade-off analysis
        """
```

---

## 📊 Configuration System

### Evolution Config (`config/evolution_config.yaml`)
```yaml
# Main EA parameters
population_size: 50
generations: 100
mutation_rate: 0.1
crossover_rate: 0.8
elite_size: 5

# Simulation settings
simulation_timesteps: 365  # 1 year for faster evolution
monte_carlo_runs: 1
parallel_workers: 4

# Algorithm selection
algorithm: "nsga_ii"  # Options: nsga_ii, differential_evolution, particle_swarm
selection_method: "tournament"
tournament_size: 3

# Convergence criteria
convergence_threshold: 0.001
convergence_generations: 10
max_stagnation: 20

# Output settings
checkpoint_frequency: 10
save_all_generations: true
export_pareto_front: true
```

### Parameter Bounds (`config/parameter_bounds.yaml`)
```yaml
# Economic constraints for genome validation
node_economics:
  node_setup_cost: [500, 5000]
  node_resource_provision_rate: [10000, 1000000]
  node_token_stake: [1000, 50000]
  apr_threshold: [5, 50]
  node_growth_cap: [1, 20]

network_economics:
  resource_unit_price: [0.000001, 0.001]
  network_resource_demand_growth_rate: [0.001, 0.1]
  initial_network_resource_demand: [1000000, 10000000000]

# Constraint validation
constraints:
  revenue_shares_sum: 1.0
  token_allocations_sum: 1.0
  min_foundation_runway_days: 365
```

---

## 🎯 Implementation Phases

### Phase 2.1: Core Infrastructure (Week 1-2)
- [ ] Implement `TokenGenome` class with parameter mapping
- [ ] Create `DePINSimulationWrapper` for radCAD integration  
- [ ] Build basic evolution engine with DEAP
- [ ] Add configuration system (YAML files)
- [ ] Unit tests for genome validation and constraint checking

### Phase 2.2: Evolution Algorithms (Week 3-4)
- [ ] Implement NSGA-II for multi-objective optimization
- [ ] Add differential evolution and particle swarm alternatives
- [ ] Parallel simulation execution with joblib
- [ ] Convergence detection and early stopping
- [ ] Integration tests with existing diagnostic suite

### Phase 2.3: Analysis & Visualization (Week 5-6)
- [ ] Convergence plotting and fitness tracking
- [ ] Parameter distribution analysis over generations
- [ ] KPI comparison between evolved and baseline configurations
- [ ] Pareto front visualization for trade-off analysis
- [ ] Automated report generation (Markdown + plots)

### Phase 2.4: Experiments & Validation (Week 7-8)
- [ ] Baseline comparison experiments
- [ ] Sensitivity analysis for parameter importance
- [ ] Multi-objective trade-off studies
- [ ] Validation against known optimal configurations
- [ ] Performance benchmarking and optimization

---

## 🧪 Experiment Design

### 1. Baseline Comparison Experiment
```python
# experiments/baseline_comparison.py
def run_baseline_comparison():
    """
    Compare evolved parameters against current sys_params defaults
    Validate that EA can discover configurations with lower cost
    """
    baseline_cost = simulate_with_default_params()
    evolved_results = evolve_parameters(generations=50)
    improvement = calculate_improvement_percentage(baseline_cost, evolved_results.best_fitness)
    
    assert improvement >= 20, f"EA should achieve 20%+ improvement, got {improvement}%"
```

### 2. Multi-Objective Trade-off Analysis
```python
# experiments/multi_objective_pareto.py  
def analyze_protocol_tradeoffs():
    """
    Explore trade-offs between cost function components:
    - Price stability vs. Node profitability
    - Utilization efficiency vs. Foundation sustainability  
    - Economic vs. Decentralization objectives
    """
    pareto_fronts = {
        'price_vs_profitability': evolve_pareto(['price_stability', 'node_profitability']),
        'efficiency_vs_sustainability': evolve_pareto(['utilization_efficiency', 'foundation_sustainability']),
        'economic_vs_decentralization': evolve_pareto(['total_economic', 'decentralization'])
    }
```

### 3. Parameter Sensitivity Ranking
```python
# experiments/sensitivity_analysis.py
def rank_parameter_importance():
    """
    Determine which parameters have the highest impact on fitness
    Guide future manual tuning and constraint refinement
    """
    sensitivity_scores = {}
    for param in TokenGenome.__dataclass_fields__.keys():
        score = calculate_parameter_sensitivity(param)
        sensitivity_scores[param] = score
    
    return sorted(sensitivity_scores.items(), key=lambda x: x[1], reverse=True)
```

---

## 📈 Success Metrics & Validation

### Quantitative Success Criteria
- [ ] **Fitness Improvement**: 20%+ reduction in cumulative cost vs. baseline
- [ ] **Convergence Performance**: Achieve optimal solutions within 50 generations  
- [ ] **Simulation Throughput**: Process 50 genomes in <30 minutes (parallel execution)
- [ ] **Parameter Coverage**: Successfully evolve all 21 genome parameters
- [ ] **Constraint Satisfaction**: 100% of evolved genomes meet economic constraints

### Qualitative Success Criteria
- [ ] **Economic Realism**: Evolved parameters produce economically viable networks
- [ ] **Result Interpretability**: Clear visualization of parameter evolution and trade-offs
- [ ] **Integration Quality**: Seamless operation with existing radCAD simulation
- [ ] **Reproducibility**: Deterministic results with seed control and configuration management
- [ ] **Extensibility**: Architecture supports adding new parameters and objectives

### Validation Framework
```python
# tests/integration/test_evolution_integration.py
class TestEvolutionIntegration:
    
    def test_genome_parameter_injection(self):
        """Verify TokenGenome correctly maps to sys_params"""
        
    def test_simulation_wrapper_execution(self):
        """Ensure simulation runs successfully with evolved parameters"""
        
    def test_fitness_calculation_consistency(self):
        """Validate fitness scores match cost_functions.py calculations"""
        
    def test_constraint_validation(self):
        """Check all economic constraints are enforced"""
        
    def test_convergence_behavior(self):
        """Verify evolution improves fitness over generations"""
```

---

## 🚀 Usage Examples

### Basic Evolution Run
```python
from evodepin import EvolutionEngine, EvolutionConfig

# Configure evolution
config = EvolutionConfig.from_yaml('config/evolution_config.yaml')

# Run evolution
engine = EvolutionEngine(config)
results = engine.evolve()

# Analyze results
print(f"Best fitness: {results.best_fitness}")
print(f"Convergence at generation: {results.convergence_generation}")

# Export results
results.export_summary('results/evolution_summary.md')
results.plot_convergence('results/convergence.png')
```

### Multi-Objective Optimization
```python
from evodepin.algorithms import MultiObjectiveEvolution

# Define objectives
objectives = ['price_stability_cost', 'utilization_efficiency_cost', 'foundation_sustainability_cost']

# Run NSGA-II
mo_evolution = MultiObjectiveEvolution(objectives)
pareto_front = mo_evolution.evolve_pareto_front(population_size=100, generations=75)

# Analyze trade-offs
pareto_front.plot_objective_space('results/pareto_front.png')
pareto_front.export_solutions('results/pareto_solutions.json')
```

### Custom Parameter Bounds
```python
# Override default parameter bounds for specific experiments
custom_bounds = {
    'node_setup_cost': [800, 1200],    # Narrow focus on mid-range hardware
    'apr_threshold': [12, 18],         # Target APR band
    'resource_unit_price': [0.00001, 0.0001]  # Price sensitivity analysis
}

config = EvolutionConfig(parameter_bounds=custom_bounds)
results = EvolutionEngine(config).evolve()
```

---

## 🔧 Integration with Existing Codebase

### 1. Extended LLMLOG.MD Entry
```markdown
## 2025-01-XX: EvoDePIN Evolutionary Algorithm Integration

### Changes:
- Added evodepin/ module with TokenGenome class and evolution framework
- Integrated DEAP/NSGA-II for multi-objective parameter optimization  
- Created simulation wrapper for seamless radCAD integration
- Extended cost_functions.py usage for automated fitness evaluation
- Added comprehensive experiment suite for validation

### Technical Details:
- TokenGenome maps 21 parameters from sys_params.py to evolvable genes
- DePINSimulationWrapper abstracts radCAD execution for EA evaluation
- Multi-objective optimization discovers Pareto-optimal trade-offs
- Parallel simulation execution achieves 4x throughput improvement

### Validation:
- All existing tests pass with EA integration
- Baseline comparison shows 20%+ fitness improvement vs. default parameters
- Economic constraints maintained through genome validation
- Cost function integration verified against existing calculations

### Next Steps:
- Real-time adaptive control using evolved parameters
- LLM-guided mutation for semantic parameter exploration
- Integration with Streamlit UI for interactive evolution
```

### 2. Requirements.txt Update
```txt
# Existing dependencies maintained
numpy>=1.21.0
pandas>=1.5.0
matplotlib>=3.6.0
radcad>=0.11.0
tqdm>=4.64.0

# New EA dependencies  
deap>=1.4.1
nevergrad>=0.12.0
pyyaml>=6.0
joblib>=1.3.0
seaborn>=0.12.0
```

### 3. Updated Main Entry Point
```python
# DePIN_Simulator.py - Enhanced with EA capabilities
def main():
    parser = argparse.ArgumentParser(description='DePIN Simulator with Evolutionary Optimization')
    parser.add_argument('--mode', choices=['simulate', 'evolve', 'analyze'], default='simulate')
    parser.add_argument('--evolution-config', default='evodepin/config/evolution_config.yaml')
    
    args = parser.parse_args()
    
    if args.mode == 'simulate':
        run_traditional_simulation()
    elif args.mode == 'evolve':
        from evodepin import EvolutionEngine, EvolutionConfig
        config = EvolutionConfig.from_yaml(args.evolution_config)
        results = EvolutionEngine(config).evolve()
        results.export_summary(f'results/evolution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
    elif args.mode == 'analyze':
        run_parameter_analysis()
```

---

## 📚 Documentation & Knowledge Transfer

### 1. README.md Updates
```markdown
## 🧬 Evolutionary Optimization (New in v2.0)

The DePIN Simulator now includes automated parameter optimization using evolutionary algorithms:

```bash
# Run basic evolution to optimize all parameters
python DePIN_Simulator.py --mode evolve

# Multi-objective optimization with custom config  
python DePIN_Simulator.py --mode evolve --evolution-config custom_config.yaml

# Analyze parameter sensitivity
python DePIN_Simulator.py --mode analyze
```

**Key Features:**
- 21-parameter genome covering node economics, network dynamics, and token mechanics
- Multi-objective optimization with Pareto front analysis
- Parallel simulation execution for 4x faster convergence
- Integration with existing cost function framework
```

### 2. Technical Documentation
- **Architecture Guide**: Detailed component interaction diagrams
- **Parameter Reference**: Complete genome specification with economic justification
- **Algorithm Comparison**: Performance analysis of different EA approaches
- **Experiment Cookbook**: Step-by-step guide for common optimization tasks

---

## 🎯 Delivery Timeline

| Week | Phase | Deliverables | Success Criteria |
|------|-------|--------------|------------------|
| 1-2 | Core Infrastructure | TokenGenome, SimulationWrapper, Basic EA | Unit tests pass, genome validation works |
| 3-4 | Advanced Algorithms | NSGA-II, parallel execution, convergence detection | Multi-objective optimization functional |
| 5-6 | Analysis & Visualization | Plotting, reporting, KPI extraction | Professional-quality result analysis |
| 7-8 | Experiments & Validation | Baseline comparison, sensitivity analysis | 20%+ improvement demonstrated |

**Final Deliverable**: Production-ready EvoDePIN module with comprehensive documentation, test coverage, and validated performance improvements over baseline configurations.

---

**Stakeholders**: DePIN Protocol Designers, Token Engineers, Research Teams  
**Approval Required**: Architecture Review, Performance Validation, Integration Testing  
**Risk Mitigation**: Fallback to single-objective optimization if multi-objective proves too complex within timeline 