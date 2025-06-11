#!/usr/bin/env python3
"""
Multi-Node Emission Cap Testing

Validates emission cap utilization tracking across different starting node counts:
- 2,000 nodes: Should be ~40% cap utilization
- 5,000 nodes: Should be 100% cap utilization  
- 7,500 nodes: Should exceed 100% but be capped

Tests the mathematical accuracy and cap enforcement of the emission system.
"""

import sys
import os
import pandas as pd

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import radCAD simulation setup
from radcad import Model, Simulation
from model.sys_params import sys_params, initial_values
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model import run

def test_node_count_scenario(node_count, scenario_name):
    """Test emission cap utilization for a specific node count"""
    
    print(f"\n🧪 Testing {scenario_name}")
    print("=" * 50)
    
    # Configure test parameters
    test_params = sys_params.copy()
    test_params.update({
        'emission_policy': ['per_device'],
        'emission_per_device_daily': [100],      # 100 tokens per node per day
        'emission_device_cap_daily': [500_000],  # 500k daily cap
        'initial_node_amount': [node_count],     # Variable node count
    })
    
    # Calculate expected utilization
    expected_utilization = (node_count * 100) / 500_000 * 100
    expected_actual_emission = min(node_count * 100, 500_000)
    
    print(f"📊 Configuration:")
    print(f"   Nodes: {node_count:,}")
    print(f"   Per-node emission: {test_params['emission_per_device_daily'][0]} tokens/day")
    print(f"   Daily cap: {test_params['emission_device_cap_daily'][0]:,} tokens")
    print(f"   Expected utilization: {expected_utilization:.1f}%")
    print(f"   Expected actual emission: {expected_actual_emission:,} tokens")
    
    # Run simulation
    try:
        model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
        simulation = Simulation(model=model, timesteps=5, runs=1)  # Short test run
        
        result = simulation.run()
        df = pd.DataFrame(result)
        
        # Get timestep 2 results (after radCAD initialization completes)
        # Note: timestep 1 shows 0 nodes due to execution order, timestep 2 shows proper initialization
        first_step = df[df['timestep'] == 2].iloc[0]
        
        actual_utilization = first_step['emission_cap_utilization']
        actual_emission = first_step['token_incentives_vested']
        actual_nodes = first_step['node_amount']
        
        print(f"\n📈 Results:")
        print(f"   Actual nodes: {actual_nodes:,}")
        print(f"   Actual utilization: {actual_utilization:.1f}%")
        print(f"   Actual emission: {actual_emission:,} tokens")
        
        # Validation checks
        utilization_match = abs(actual_utilization - expected_utilization) < 0.1
        emission_match = abs(actual_emission - expected_actual_emission) < 1
        cap_enforcement = actual_emission <= 500_000
        
        print(f"\n✅ Validation:")
        print(f"   Utilization accuracy: {'✅ PASS' if utilization_match else '❌ FAIL'}")
        print(f"   Emission accuracy: {'✅ PASS' if emission_match else '❌ FAIL'}")
        print(f"   Cap enforcement: {'✅ PASS' if cap_enforcement else '❌ FAIL'}")
        
        return {
            'scenario': scenario_name,
            'node_count': node_count,
            'expected_utilization': expected_utilization,
            'actual_utilization': actual_utilization,
            'expected_emission': expected_actual_emission,
            'actual_emission': actual_emission,
            'utilization_match': utilization_match,
            'emission_match': emission_match,
            'cap_enforcement': cap_enforcement,
            'overall_pass': utilization_match and emission_match and cap_enforcement
        }
        
    except Exception as e:
        print(f"❌ Error in {scenario_name}: {e}")
        return {
            'scenario': scenario_name,
            'node_count': node_count,
            'error': str(e),
            'overall_pass': False
        }

def main():
    """Run comprehensive multi-node emission cap tests"""
    
    print("🚀 Multi-Node Emission Cap Testing")
    print("=" * 60)
    print("Testing emission cap utilization across different node counts")
    print("Validating mathematical accuracy and cap enforcement")
    
    # Test scenarios
    scenarios = [
        (2000, "Below Cap (2K nodes)"),
        (5000, "At Cap (5K nodes)"),
        (7500, "Above Cap (7.5K nodes)")
    ]
    
    results = []
    
    # Run all test scenarios
    for node_count, scenario_name in scenarios:
        result = test_node_count_scenario(node_count, scenario_name)
        results.append(result)
    
    # Summary report
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for result in results:
        if 'error' in result:
            print(f"❌ {result['scenario']}: ERROR - {result['error']}")
            all_passed = False
        else:
            status = "✅ PASS" if result['overall_pass'] else "❌ FAIL"
            print(f"{status} {result['scenario']}: {result['actual_utilization']:.1f}% utilization")
            if not result['overall_pass']:
                all_passed = False
    
    print(f"\n🏆 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n✅ Emission cap utilization tracking is working correctly!")
        print("✅ Mathematical calculations are accurate")
        print("✅ Cap enforcement is properly implemented")
        print("✅ Ready for optional cap configuration implementation")
    else:
        print("\n❌ Issues detected - review implementation before proceeding")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 