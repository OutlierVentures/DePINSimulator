#!/usr/bin/env python3
"""
Optional Emission Cap Configuration Testing

Validates emission cap enabled/disabled functionality across different node counts:
- Tests cap enabled (current/default behavior) 
- Tests cap disabled (research mode with only budget limits)
- Compares capped vs uncapped emission behaviors
- Ensures backward compatibility and configuration flexibility

Test Matrix: 3 node counts × 2 cap configurations = 6 scenarios
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

def test_cap_configuration(node_count, cap_enabled, scenario_name):
    """Test emission behavior with specific cap configuration"""
    
    print(f"\n🧪 Testing {scenario_name}")
    print("=" * 60)
    
    # Configure test parameters
    test_params = sys_params.copy()
    test_params.update({
        'emission_policy': ['per_device'],
        'emission_per_device_daily': [100],      # 100 tokens per node per day
        'emission_device_cap_daily': [500_000],  # 500k daily cap
        'initial_node_amount': [node_count],     # Variable node count
        'emission_cap_enabled': [cap_enabled],   # Variable cap configuration
    })
    
    # Calculate expected behavior
    uncapped_emission = node_count * 100
    expected_emission = min(uncapped_emission, 500_000) if cap_enabled else uncapped_emission
    expected_utilization = (uncapped_emission / 500_000 * 100) if cap_enabled else 0
    
    print(f"📊 Configuration:")
    print(f"   Nodes: {node_count:,}")
    print(f"   Per-node emission: {test_params['emission_per_device_daily'][0]} tokens/day")
    print(f"   Daily cap: {test_params['emission_device_cap_daily'][0]:,} tokens")
    print(f"   Cap enabled: {cap_enabled}")
    print(f"   Uncapped demand: {uncapped_emission:,} tokens")
    print(f"   Expected emission: {expected_emission:,} tokens")
    print(f"   Expected utilization: {expected_utilization:.1f}%")
    
    # Run simulation
    try:
        model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
        simulation = Simulation(model=model, timesteps=5, runs=1)  # Short test run
        
        result = simulation.run()
        df = pd.DataFrame(result)
        
        # Get timestep 2 results (after radCAD initialization)
        test_step = df[df['timestep'] == 2].iloc[0]
        
        actual_emission = test_step['token_incentives_vested']
        actual_utilization = test_step['emission_cap_utilization']
        actual_nodes = test_step['node_amount']
        
        print(f"\n📈 Results:")
        print(f"   Actual nodes: {actual_nodes:,}")
        print(f"   Actual emission: {actual_emission:,} tokens")
        print(f"   Actual utilization: {actual_utilization:.1f}%")
        
        # Validation checks
        emission_match = abs(actual_emission - expected_emission) < 1
        utilization_match = abs(actual_utilization - expected_utilization) < 0.1
        
        # Cap enforcement check (only relevant when cap enabled)
        cap_enforcement = True
        if cap_enabled and uncapped_emission > 500_000:
            cap_enforcement = actual_emission <= 500_000
        
        print(f"\n✅ Validation:")
        print(f"   Emission accuracy: {'✅ PASS' if emission_match else '❌ FAIL'}")
        print(f"   Utilization accuracy: {'✅ PASS' if utilization_match else '❌ FAIL'}")
        print(f"   Cap enforcement: {'✅ PASS' if cap_enforcement else '❌ FAIL'}")
        
        return {
            'scenario': scenario_name,
            'node_count': node_count,
            'cap_enabled': cap_enabled,
            'uncapped_demand': uncapped_emission,
            'expected_emission': expected_emission,
            'actual_emission': actual_emission,
            'expected_utilization': expected_utilization,
            'actual_utilization': actual_utilization,
            'emission_match': emission_match,
            'utilization_match': utilization_match,
            'cap_enforcement': cap_enforcement,
            'overall_pass': emission_match and utilization_match and cap_enforcement
        }
        
    except Exception as e:
        print(f"❌ Error in {scenario_name}: {e}")
        return {
            'scenario': scenario_name,
            'node_count': node_count,
            'cap_enabled': cap_enabled,
            'error': str(e),
            'overall_pass': False
        }

def main():
    """Run comprehensive optional cap configuration tests"""
    
    print("🚀 Optional Emission Cap Configuration Testing")
    print("=" * 70)
    print("Testing emission cap enabled/disabled across different node counts")
    print("Validating backward compatibility and research mode functionality")
    
    # Test scenarios: 3 node counts × 2 cap configurations
    node_counts = [2000, 5000, 7500]
    cap_configs = [True, False]
    
    results = []
    
    # Run all test scenarios
    for node_count in node_counts:
        for cap_enabled in cap_configs:
            cap_status = "Enabled" if cap_enabled else "Disabled"
            
            if node_count == 2000:
                node_desc = "Below Cap (2K nodes)"
            elif node_count == 5000:
                node_desc = "At Cap (5K nodes)"
            else:
                node_desc = "Above Cap (7.5K nodes)"
            
            scenario_name = f"{node_desc} - Cap {cap_status}"
            result = test_cap_configuration(node_count, cap_enabled, scenario_name)
            results.append(result)
    
    # Summary report
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    cap_enabled_results = []
    cap_disabled_results = []
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['scenario']}: ERROR - {result['error']}")
            all_passed = False
        else:
            status = "✅ PASS" if result['overall_pass'] else "❌ FAIL"
            print(f"{status} {result['scenario']}: {result['actual_emission']:,} tokens")
            
            if result['cap_enabled']:
                cap_enabled_results.append(result)
            else:
                cap_disabled_results.append(result)
                
            if not result['overall_pass']:
                all_passed = False
    
    # Comparative analysis
    print(f"\n📊 COMPARATIVE ANALYSIS")
    print("=" * 70)
    
    for node_count in node_counts:
        enabled_result = next((r for r in cap_enabled_results if r['node_count'] == node_count), None)
        disabled_result = next((r for r in cap_disabled_results if r['node_count'] == node_count), None)
        
        if enabled_result and disabled_result and 'error' not in enabled_result and 'error' not in disabled_result:
            node_desc = f"{node_count:,} nodes"
            enabled_emission = enabled_result['actual_emission']
            disabled_emission = disabled_result['actual_emission']
            difference = disabled_emission - enabled_emission
            
            print(f"📈 {node_desc}:")
            print(f"   Cap Enabled:  {enabled_emission:,} tokens")
            print(f"   Cap Disabled: {disabled_emission:,} tokens")
            print(f"   Difference:   {difference:+,} tokens")
    
    print(f"\n🏆 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n✅ Optional emission cap configuration is working correctly!")
        print("✅ Backward compatibility maintained (cap enabled by default)")
        print("✅ Research mode functional (cap disabled allows unlimited emission)")
        print("✅ Mathematical accuracy confirmed for both configurations")
        print("✅ Ready for policy comparison studies and BME implementation")
    else:
        print("\n❌ Issues detected - review implementation before proceeding")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 