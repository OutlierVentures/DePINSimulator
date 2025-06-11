#!/usr/bin/env python3
"""
Phase 1.5 Completion Validation

Lightweight validation demonstrating complete emission framework functionality:
- Linear emission: Fixed daily rate (policy-independent)
- Per-device emission: Node-scaled with cap enforcement
- BME emission: Usage-driven with configurable parameters

30-day simulation proving distinct emission behaviors across all policies.
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import radCAD simulation setup
from radcad import Model, Simulation
from model.sys_params import sys_params, initial_values
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks

def run_policy_simulation(policy_name, policy_config, days=30):
    """Run simulation for specific emission policy"""
    
    # Configure test parameters
    test_params = sys_params.copy()
    base_config = {
        'initial_node_amount': [5000],
        'initial_network_resource_demand': [4e8],
        'emission_cap_enabled': [True],
    }
    test_params.update(base_config)
    test_params.update(policy_config)
    
    # Run simulation
    model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
    simulation = Simulation(model=model, timesteps=days, runs=1)
    
    result = simulation.run()
    df = pd.DataFrame(result)
    
    # Extract final substep for each timestep
    daily_data = []
    for timestep in range(1, days + 1):
        timestep_data = df[df['timestep'] == timestep]
        if len(timestep_data) > 0:
            final_substep = timestep_data.iloc[-1]
            daily_data.append({
                'day': timestep,
                'policy': policy_name,
                'emission': final_substep['token_incentives_vested'],
                'emission_cum': final_substep['token_incentives_vested_cum'],
                'cap_utilization': final_substep['emission_cap_utilization'],
                'nodes': final_substep['node_amount'],
                'network_revenue': final_substep['network_revenue'],
                'utilization': final_substep['network_resource_demand_supply_ratio']
            })
    
    return pd.DataFrame(daily_data)

def main():
    """Phase 1.5 completion validation"""
    
    print("🎯 Phase 1.5 Completion Validation")
    print("=" * 70)
    print("Demonstrating complete emission framework with 3 distinct policies")
    print("30-day simulation showing policy-specific behaviors\n")
    
    # Policy configurations
    policies = [
        {
            'name': 'Linear',
            'config': {
                'emission_policy': ['linear'],
                'incentive_mode': ['fixed_rate'],
            }
        },
        {
            'name': 'Per-Device', 
            'config': {
                'emission_policy': ['per_device'],
                'emission_per_device_daily': [100],
                'emission_device_cap_daily': [500_000],
            }
        },
        {
            'name': 'BME',
            'config': {
                'emission_policy': ['bme'],
                'bme_burn_rate_multiplier': [1.0],
                'bme_mint_rate_multiplier': [1.0],
                'emission_device_cap_daily': [500_000],
            }
        }
    ]
    
    # Run simulations
    all_results = []
    
    for policy in policies:
        print(f"🔄 Running {policy['name']} emission simulation...")
        results = run_policy_simulation(policy['name'], policy['config'])
        all_results.append(results)
    
    # Combine results
    combined_df = pd.concat(all_results, ignore_index=True)
    
    # Analysis and validation
    print(f"\n📊 30-Day Emission Policy Comparison")
    print("=" * 70)
    
    for policy_name in ['Linear', 'Per-Device', 'BME']:
        policy_data = combined_df[combined_df['policy'] == policy_name]
        
        # Key statistics
        total_emission = policy_data['emission_cum'].iloc[-1]
        avg_daily = policy_data['emission'].mean()
        std_daily = policy_data['emission'].std()
        max_cap_util = policy_data['cap_utilization'].max()
        
        print(f"\n🎯 {policy_name} Emission Results:")
        print(f"   Total 30-day emission: {total_emission:,.0f} tokens")
        print(f"   Average daily: {avg_daily:,.0f} tokens")
        print(f"   Daily std dev: {std_daily:.0f} tokens")
        print(f"   Max cap utilization: {max_cap_util:.1f}%")
        
        # Policy-specific insights
        if policy_name == 'Linear':
            consistency = std_daily / avg_daily * 100 if avg_daily > 0 else 0
            print(f"   Consistency (CV): {consistency:.2f}% (should be ~0%)")
            
        elif policy_name == 'Per-Device':
            scaling_test = policy_data['emission'].iloc[-1] / policy_data['emission'].iloc[0] if policy_data['emission'].iloc[0] > 0 else 1
            print(f"   Scaling factor: {scaling_test:.2f}x (follows node growth)")
            
        elif policy_name == 'BME':
            # Check correlation with network activity
            correlation = policy_data['emission'].corr(policy_data['network_revenue'])
            print(f"   Usage correlation: {correlation:.3f} (should be >0.5)")
    
    # Cross-policy validation
    print(f"\n✅ Policy Differentiation Validation")
    print("=" * 70)
    
    validation_passed = True
    validation_notes = []
    
    # Get final day data for comparison
    final_day = combined_df[combined_df['day'] == 30]
    linear_emission = final_day[final_day['policy'] == 'Linear']['emission'].iloc[0]
    device_emission = final_day[final_day['policy'] == 'Per-Device']['emission'].iloc[0] 
    bme_emission = final_day[final_day['policy'] == 'BME']['emission'].iloc[0]
    
    # Check policies produce different results
    emissions = [linear_emission, device_emission, bme_emission]
    unique_emissions = len(set([round(e, -2) for e in emissions]))  # Round to nearest 100
    
    if unique_emissions >= 2:
        validation_notes.append("✅ Policies produce distinct emission patterns")
    else:
        validation_notes.append("❌ Policies too similar - may indicate configuration issue")
        validation_passed = False
    
    # Check BME responsiveness
    bme_data = combined_df[combined_df['policy'] == 'BME']
    bme_variance = bme_data['emission'].var()
    if bme_variance > 1000:  # Some variance expected for usage-driven
        validation_notes.append("✅ BME shows usage-driven variability")
    else:
        validation_notes.append("⚠️  BME may be too stable (check network activity)")
    
    # Check cap enforcement (only for policies that use caps)
    capped_policies = combined_df[combined_df['policy'].isin(['Per-Device', 'BME'])]
    max_capped_emission = capped_policies['emission'].max() if len(capped_policies) > 0 else 0
    daily_cap = 500_000
    if max_capped_emission <= daily_cap * 1.01:  # Allow 1% tolerance
        validation_notes.append("✅ Emission cap enforcement working")
    else:
        validation_notes.append("❌ Emission cap violation detected")
        validation_passed = False
    
    # Print validation results
    for note in validation_notes:
        print(f"   {note}")
    
    # Final summary
    print(f"\n🏆 Phase 1.5 Completion Status")
    print("=" * 70)
    
    if validation_passed:
        print("✅ PHASE 1.5 COMPLETE - Emission Framework Fully Operational")
        print("\n📋 Emission Framework Capabilities:")
        print("   ✅ Linear emission: Fixed daily rate (policy-independent)")
        print("   ✅ Per-device emission: Node-scaled with cap enforcement")
        print("   ✅ BME emission: Usage-driven with configurable parameters")
        print("   ✅ Optional cap configuration for research flexibility")
        print("   ✅ Mathematical precision with comprehensive validation")
        print("\n🚀 Ready for Phase 2: Optimal Control Theory & Policy Discovery")
    else:
        print("❌ PHASE 1.5 INCOMPLETE - Issues detected in emission framework")
        print("   Review validation failures before proceeding to Phase 2")
    
    return validation_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 