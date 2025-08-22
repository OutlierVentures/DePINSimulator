#!/usr/bin/env python3
"""
Simple test script to verify DePIN simulation runs with recent changes
"""

import sys
import os
import pandas as pd

# Add project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import radCAD simulation setup
from radcad import Model, Simulation
from model.sys_params import sys_params
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model import run

def test_basic_simulation():
    """Test basic simulation functionality"""
    print("🧪 Testing DePIN Simulation Basic Functionality")
    print("=" * 60)
    
    try:
        # Configure short test parameters
        test_params = sys_params.copy()
        
        print("📊 Configuration:")
        print(f"   Initial nodes: {test_params['initial_node_amount'][0]:,}")
        print(f"   Emission policy: {test_params['emission_policy'][0]}")
        print(f"   Test timesteps: 5")
        
        # Run short simulation
        model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
        simulation = Simulation(model=model, timesteps=5, runs=1)
        
        print("\n🔄 Running simulation...")
        result = simulation.run()
        df = pd.DataFrame(result)
        
        print("✅ Simulation completed successfully!")
        print(f"📊 Generated {len(df)} rows of data")
        
        # Validate key columns exist
        expected_columns = [
            'network_resource_demand', 
            'node_amount', 
            'dex_token_price',
            'node_apr'
        ]
        
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"⚠️  Missing expected columns: {missing_columns}")
        else:
            print("✅ All core columns present")
        
        # Check new features
        new_features = [
            'fundamental_token_price',
            'token_market_multiplier', 
            'resource_unit_price_current',
            'utilization_error_cum'
        ]
        
        present_features = [col for col in new_features if col in df.columns]
        print(f"🆕 New features present: {present_features}")
        
        # Basic data validation
        final_step = df[df['timestep'] == df['timestep'].max()].iloc[-1]
        print(f"\n📈 Final Results:")
        print(f"   Node count: {final_step['node_amount']:,.0f}")
        print(f"   Token price: ${final_step['dex_token_price']:.6f}")
        print(f"   Node APR: {final_step['node_apr']:.1f}%")
        
        if 'fundamental_token_price' in df.columns:
            print(f"   Fundamental price: ${final_step['fundamental_token_price']:.6f}")
        if 'resource_unit_price_current' in df.columns:
            print(f"   Resource price: ${final_step['resource_unit_price_current']:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emission_policies():
    """Test different emission policies"""
    print("\n🧪 Testing Emission Policies")
    print("=" * 60)
    
    policies = ['linear', 'per_device', 'bme']
    results = {}
    
    for policy in policies:
        try:
            print(f"\nTesting {policy} emission policy...")
            test_params = sys_params.copy()
            test_params['emission_policy'] = [policy]
            
            if policy == 'per_device':
                test_params['emission_per_device_daily'] = [50]
            elif policy == 'bme':
                test_params['bme_burn_rate_multiplier'] = [1.0]
                test_params['bme_mint_rate_multiplier'] = [1.0]
            
            model = Model(initial_state=initial_state, params=test_params, state_update_blocks=state_update_blocks)
            simulation = Simulation(model=model, timesteps=3, runs=1)
            
            result = simulation.run()
            df = pd.DataFrame(result)
            
            final_emission = df[df['timestep'] == df['timestep'].max()]['token_incentives_vested'].iloc[-1]
            results[policy] = final_emission
            
            print(f"   ✅ {policy}: {final_emission:,.0f} tokens emitted")
            
        except Exception as e:
            print(f"   ❌ {policy}: Error - {e}")
            results[policy] = f"Error: {e}"
    
    print(f"\n📊 Emission Policy Results:")
    for policy, result in results.items():
        if isinstance(result, (int, float)):
            print(f"   {policy}: {result:,.0f} tokens")
        else:
            print(f"   {policy}: {result}")
    
    return results

if __name__ == "__main__":
    print("🚀 DePIN Simulation Test Suite")
    print("=" * 70)
    
    # Test 1: Basic simulation
    basic_test_passed = test_basic_simulation()
    
    if basic_test_passed:
        # Test 2: Emission policies
        emission_results = test_emission_policies()
        
        print(f"\n🏆 Overall Test Results:")
        print(f"   ✅ Basic simulation: {'PASS' if basic_test_passed else 'FAIL'}")
        
        emission_pass_count = sum(1 for result in emission_results.values() if isinstance(result, (int, float)))
        print(f"   📊 Emission policies: {emission_pass_count}/3 passed")
        
        if basic_test_passed and emission_pass_count >= 2:
            print("\n🎉 Simulation is ready for UI development!")
        else:
            print("\n⚠️  Some issues detected - review before proceeding")
    else:
        print(f"\n❌ Basic simulation failed - fix core issues first")