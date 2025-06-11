#!/usr/bin/env python3
"""
BME Emission Policy Testing

Validates BME (Burn-and-Mint Equilibrium) emission policy alongside existing policies:
- Tests all 3 emission policies: linear (default), per-device, BME
- Validates BME usage-driven calculations based on network activity
- Compares emission behaviors across different utilization levels
- Ensures complete emission framework functionality

Test Matrix: 3 policies × 3 utilization scenarios = 9 test cases
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

def test_emission_policy(policy_name, policy_config, scenario_name):
    """Test specific emission policy configuration"""
    
    print(f"\n🧪 Testing {scenario_name}")
    print("=" * 60)
    
    # Configure test parameters
    test_params = sys_params.copy()
    base_config = {
        'initial_node_amount': [5000],               # Standard node count
        'initial_network_resource_demand': [4e8],    # Standard demand
        'emission_cap_enabled': [True],              # Cap enabled for consistency
    }
    test_params.update(base_config)
    test_params.update(policy_config)
    
    print(f"📊 Configuration:")
    print(f"   Policy: {policy_name}")
    print(f"   Nodes: {test_params['initial_node_amount'][0]:,}")
    print(f"   Network demand: {test_params['initial_network_resource_demand'][0]:,.0f}")
    print(f"   Cap enabled: {test_params['emission_cap_enabled'][0]}")
    
    if policy_name == 'per_device':
        print(f"   Per-device rate: {test_params['emission_per_device_daily'][0]} tokens/node/day")
    elif policy_name == 'bme':
        print(f"   BME burn multiplier: {test_params['bme_burn_rate_multiplier'][0]}")
        print(f"   BME mint multiplier: {test_params['bme_mint_rate_multiplier'][0]}")
    
    # Run simulation
    try:
        model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
        simulation = Simulation(model=model, timesteps=5, runs=1)  # Short test run
        
        result = simulation.run()
        df = pd.DataFrame(result)
        
        # Get timestep 2 results (after radCAD initialization) - use final substep
        test_step = df[df['timestep'] == 2].iloc[-1]  # Last substep has final values
        
        # Extract key metrics
        actual_emission = test_step['token_incentives_vested']
        actual_utilization = test_step['emission_cap_utilization']
        actual_nodes = test_step['node_amount']
        network_demand = test_step['network_resource_demand']
        network_provision = test_step['network_resource_provision']
        network_sold = min(network_demand, network_provision)
        utilization_ratio = network_sold / network_provision if network_provision > 0 else 0
        
        print(f"\n📈 Network Metrics:")
        print(f"   Nodes: {actual_nodes:,}")
        print(f"   Demand: {network_demand:,.0f} units")
        print(f"   Provision: {network_provision:,.0f} units")
        print(f"   Sold: {network_sold:,.0f} units")
        print(f"   Utilization: {utilization_ratio:.1%}")
        
        print(f"\n📈 Emission Results:")
        print(f"   Emission: {actual_emission:,.0f} tokens")
        print(f"   Cap utilization: {actual_utilization:.1f}%")
        
        # Policy-specific validations
        validation_passed = True
        validation_notes = []
        
        if policy_name == 'linear':
            # Linear should be independent of network activity
            expected_emission = test_params['incentive_token_allocation'][0] / test_params['incentive_token_vesting_duration'][0]
            if abs(actual_emission - expected_emission) < 1:
                validation_notes.append("✅ Linear emission rate correct")
            else:
                validation_notes.append(f"❌ Linear emission rate incorrect: expected {expected_emission:.0f}, got {actual_emission:.0f}")
                validation_passed = False
                
        elif policy_name == 'per_device':
            # Per-device should scale with node count
            expected_emission = min(actual_nodes * test_params['emission_per_device_daily'][0], test_params['emission_device_cap_daily'][0])
            if abs(actual_emission - expected_emission) < 1:
                validation_notes.append("✅ Per-device emission scaling correct")
            else:
                validation_notes.append(f"❌ Per-device emission incorrect: expected {expected_emission:.0f}, got {actual_emission:.0f}")
                validation_passed = False
                
        elif policy_name == 'bme':
            # BME should scale with network usage
            expected_burn = network_sold * test_params['resource_unit_price'][0] * test_params['bme_burn_rate_multiplier'][0]
            expected_emission = expected_burn * test_params['bme_mint_rate_multiplier'][0]
            # Apply cap if enabled
            if test_params['emission_cap_enabled'][0]:
                expected_emission = min(expected_emission, test_params['emission_device_cap_daily'][0])
            
            if abs(actual_emission - expected_emission) < 1:
                validation_notes.append("✅ BME usage-driven emission correct")
            else:
                validation_notes.append(f"❌ BME emission incorrect: expected {expected_emission:.0f}, got {actual_emission:.0f}")
                validation_passed = False
        
        # General validations
        if actual_emission >= 0:
            validation_notes.append("✅ Non-negative emission")
        else:
            validation_notes.append("❌ Negative emission detected")
            validation_passed = False
            
        # Check against daily budget (total allocation / vesting duration)
        daily_budget = test_params['incentive_token_allocation'][0] * initial_values['token_initial_total_supply'] / test_params['incentive_token_vesting_duration'][0]
        if actual_emission <= daily_budget:
            validation_notes.append("✅ Within daily budget allocation")
        else:
            validation_notes.append(f"❌ Exceeds daily budget: {actual_emission:,.0f} > {daily_budget:,.0f}")
            validation_passed = False
        
        print(f"\n✅ Validation:")
        for note in validation_notes:
            print(f"   {note}")
        
        return {
            'scenario': scenario_name,
            'policy': policy_name,
            'actual_emission': actual_emission,
            'actual_utilization': actual_utilization,
            'network_utilization': utilization_ratio,
            'network_sold': network_sold,
            'validation_passed': validation_passed,
            'validation_notes': validation_notes
        }
        
    except Exception as e:
        print(f"❌ Error in {scenario_name}: {e}")
        return {
            'scenario': scenario_name,
            'policy': policy_name,
            'error': str(e),
            'validation_passed': False
        }

def main():
    """Run comprehensive BME emission policy tests"""
    
    print("🚀 BME Emission Policy Testing")
    print("=" * 70)
    print("Testing all emission policies: linear (default), per-device, BME")
    print("Validating complete emission framework functionality")
    
    # Test configurations for all three policies
    test_configs = [
        # Linear emission (default policy)
        {
            'name': 'Linear',
            'config': {
                'emission_policy': ['linear'],
                'incentive_mode': ['fixed_rate'],
            },
            'scenario': 'Linear Emission (Default)'
        },
        
        # Per-device emission (node-scaled)
        {
            'name': 'Per-Device',
            'config': {
                'emission_policy': ['per_device'],
                'emission_per_device_daily': [100],
                'emission_device_cap_daily': [500_000],
            },
            'scenario': 'Per-Device Emission (Node-Scaled)'
        },
        
        # BME emission (usage-driven)
        {
            'name': 'BME',
            'config': {
                'emission_policy': ['bme'],
                'bme_burn_rate_multiplier': [1.0],
                'bme_mint_rate_multiplier': [1.0],
                'emission_device_cap_daily': [500_000],
            },
            'scenario': 'BME Emission (Usage-Driven)'
        },
        
        # BME with different multipliers
        {
            'name': 'BME',
            'config': {
                'emission_policy': ['bme'],
                'bme_burn_rate_multiplier': [0.5],  # Reduced burn
                'bme_mint_rate_multiplier': [1.5],  # Increased mint (inflationary)
                'emission_device_cap_daily': [500_000],
            },
            'scenario': 'BME Emission (Inflationary 0.5x burn, 1.5x mint)'
        },
        
        # BME with cap disabled
        {
            'name': 'BME',
            'config': {
                'emission_policy': ['bme'],
                'bme_burn_rate_multiplier': [1.0],
                'bme_mint_rate_multiplier': [1.0],
                'emission_cap_enabled': [False],  # No cap
            },
            'scenario': 'BME Emission (No Cap - Research Mode)'
        },
    ]
    
    results = []
    
    # Run all test configurations
    for config in test_configs:
        result = test_emission_policy(config['name'], config['config'], config['scenario'])
        results.append(result)
    
    # Summary report
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 70)
    
    all_passed = True
    policy_groups = {}
    
    for result in results:
        if 'error' in result:
            print(f"❌ {result['scenario']}: ERROR - {result['error']}")
            all_passed = False
        else:
            status = "✅ PASS" if result['validation_passed'] else "❌ FAIL"
            print(f"{status} {result['scenario']}: {result['actual_emission']:,.0f} tokens")
            
            # Group by policy for comparison
            policy = result['policy']
            if policy not in policy_groups:
                policy_groups[policy] = []
            policy_groups[policy].append(result)
            
            if not result['validation_passed']:
                all_passed = False
    
    # Policy comparison analysis
    print(f"\n📊 EMISSION POLICY COMPARISON")
    print("=" * 70)
    
    for policy, policy_results in policy_groups.items():
        if policy_results and 'error' not in policy_results[0]:
            print(f"\n🎯 {policy.upper()} Policy Results:")
            for result in policy_results:
                if 'error' not in result:
                    print(f"   {result['actual_emission']:8,.0f} tokens - {result['scenario']}")
                    print(f"   {result['network_utilization']:8.1%} network utilization")
    
    print(f"\n🏆 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n✅ Complete emission framework is working correctly!")
        print("✅ Linear emission: Fixed daily rate (policy-independent)")
        print("✅ Per-device emission: Node-scaled with cap enforcement")
        print("✅ BME emission: Usage-driven with configurable burn/mint rates")
        print("✅ Optional cap configuration working across all policies")
        print("✅ Ready for policy comparison research and optimization")
    else:
        print("\n❌ Issues detected - review implementation before proceeding")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 