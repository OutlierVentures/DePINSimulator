"""
Emission Cap Utilization Validation Test
Tests the new emission cap utilization tracking functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from model.policy_functions import p_token_vesting
from model.sys_params import sys_params

def get_base_params():
    """Get base parameters needed for p_token_vesting"""
    return {
        'incentive_token_allocation': 0.5,
        'seller_token_allocation': 0.35,
        'idle_token_allocation': 0.1,
        'seller_token_vesting_duration': 730,
        'incentive_token_vesting_duration': 730,
        'incentive_early_weight_ratio': 0.8,
        'incentive_mode': 'fixed_rate',
        'node_token_stake': 1000
    }

def get_base_state():
    """Get base state needed for p_token_vesting"""
    return {
        'timestep': 100,
        'token_incentives_vested': 0,
        'token_incentives_vested_cum': 10000000,
        'token_seller_vested': 0,
        'token_seller_vested_cum': 5000000
    }

def get_base_history():
    """Get base state history"""
    return [[{'token_total_supply': 1000000000, 'dex_tokens': 50000000}]]

def test_emission_cap_utilization_under_cap():
    """Test cap utilization when under the cap"""
    
    # Test parameters
    params = get_base_params()
    params.update({
        'emission_policy': 'per_device',
        'emission_per_device_daily': 100,  # 100 tokens per node per day
        'emission_device_cap_daily': 500000,  # 500k daily cap
        'initial_node_amount': 3000  # 3k nodes = 300k tokens (under cap)
    })
    
    # Test state
    prev_state = get_base_state()
    prev_state['node_amount'] = 3000
    
    # Mock state history
    state_history = get_base_history()
    
    # Execute function
    result = p_token_vesting(params, 1, state_history, prev_state)
    
    # Calculate expected values
    expected_device_emission = 3000 * 100  # 300k tokens
    expected_cap_utilization = (300000 / 500000) * 100  # 60%
    
    print(f"✅ Emission Cap Utilization - Under Cap Test")
    print(f"   Active nodes: {prev_state['node_amount']:,}")
    print(f"   Tokens per node: {params['emission_per_device_daily']:,}")
    print(f"   Device-based emission: {expected_device_emission:,} tokens")
    print(f"   Emission cap: {params['emission_device_cap_daily']:,} tokens")
    print(f"   Expected cap utilization: {expected_cap_utilization:.1f}%")
    print(f"   Actual cap utilization: {result['emission_cap_utilization']:.1f}%")
    
    # Validate cap utilization calculation
    assert abs(result['emission_cap_utilization'] - expected_cap_utilization) < 0.01, \
        f"Cap utilization should be {expected_cap_utilization}%, got {result['emission_cap_utilization']}%"
    
    print(f"   ✅ Under cap utilization: PASSED")
    return True

def test_emission_cap_utilization_at_cap():
    """Test cap utilization when exactly at the cap"""
    
    # Test parameters
    params = {
        'emission_policy': 'per_device',
        'emission_per_device_daily': 100,  # 100 tokens per node per day
        'emission_device_cap_daily': 500000,  # 500k daily cap
        'incentive_token_allocation': 0.5,
        'initial_node_amount': 5000  # 5k nodes = 500k tokens (exactly at cap)
    }
    
    # Test state
    prev_state = {
        'node_amount': 5000,
        'timestep': 100,
        'token_incentives_vested_cum': 10000000
    }
    
    # Mock state history
    state_history = [[{'token_total_supply': 1000000000}]]
    
    # Execute function
    result = p_token_vesting(params, 1, state_history, prev_state)
    
    # Calculate expected values
    expected_device_emission = 5000 * 100  # 500k tokens
    expected_cap_utilization = (500000 / 500000) * 100  # 100%
    
    print(f"\n✅ Emission Cap Utilization - At Cap Test")
    print(f"   Active nodes: {prev_state['node_amount']:,}")
    print(f"   Tokens per node: {params['emission_per_device_daily']:,}")
    print(f"   Device-based emission: {expected_device_emission:,} tokens")
    print(f"   Emission cap: {params['emission_device_cap_daily']:,} tokens")
    print(f"   Expected cap utilization: {expected_cap_utilization:.1f}%")
    print(f"   Actual cap utilization: {result['emission_cap_utilization']:.1f}%")
    
    # Validate cap utilization calculation
    assert abs(result['emission_cap_utilization'] - expected_cap_utilization) < 0.01, \
        f"Cap utilization should be {expected_cap_utilization}%, got {result['emission_cap_utilization']}%"
    
    print(f"   ✅ At cap utilization: PASSED")
    return True

def test_emission_cap_utilization_over_cap():
    """Test cap utilization when over the cap (capped)"""
    
    # Test parameters
    params = {
        'emission_policy': 'per_device',
        'emission_per_device_daily': 100,  # 100 tokens per node per day
        'emission_device_cap_daily': 500000,  # 500k daily cap
        'incentive_token_allocation': 0.5,
        'initial_node_amount': 7000  # 7k nodes = 700k tokens (over cap)
    }
    
    # Test state
    prev_state = {
        'node_amount': 7000,
        'timestep': 100,
        'token_incentives_vested_cum': 10000000
    }
    
    # Mock state history
    state_history = [[{'token_total_supply': 1000000000}]]
    
    # Execute function
    result = p_token_vesting(params, 1, state_history, prev_state)
    
    # Calculate expected values
    expected_device_emission = 7000 * 100  # 700k tokens (before capping)
    expected_cap_utilization = (700000 / 500000) * 100  # 140% (over cap)
    
    print(f"\n✅ Emission Cap Utilization - Over Cap Test")
    print(f"   Active nodes: {prev_state['node_amount']:,}")
    print(f"   Tokens per node: {params['emission_per_device_daily']:,}")
    print(f"   Device-based emission: {expected_device_emission:,} tokens")
    print(f"   Emission cap: {params['emission_device_cap_daily']:,} tokens")
    print(f"   Expected cap utilization: {expected_cap_utilization:.1f}%")
    print(f"   Actual cap utilization: {result['emission_cap_utilization']:.1f}%")
    
    # Validate cap utilization calculation (shows over 100%)
    assert abs(result['emission_cap_utilization'] - expected_cap_utilization) < 0.01, \
        f"Cap utilization should be {expected_cap_utilization}%, got {result['emission_cap_utilization']}%"
    
    # But actual emission should be capped at 500k
    assert result['token_incentives_vested'] <= params['emission_device_cap_daily'], \
        f"Actual emission should be capped at {params['emission_device_cap_daily']}"
    
    print(f"   ✅ Over cap utilization: PASSED")
    return True

def test_emission_cap_utilization_linear_policy():
    """Test that linear policy returns 0% cap utilization (N/A)"""
    
    # Test parameters
    params = {
        'emission_policy': 'linear',
        'incentive_mode': 'fixed_rate',
        'incentive_token_allocation': 0.5,
        'incentive_token_vesting_duration': 730,
        'initial_node_amount': 5000
    }
    
    # Test state
    prev_state = {
        'node_amount': 5000,
        'timestep': 100,
        'token_incentives_vested_cum': 10000000
    }
    
    # Mock state history
    state_history = [[{'token_total_supply': 1000000000}]]
    
    # Execute function
    result = p_token_vesting(params, 1, state_history, prev_state)
    
    print(f"\n✅ Emission Cap Utilization - Linear Policy Test")
    print(f"   Emission policy: {params['emission_policy']}")
    print(f"   Expected cap utilization: 0% (N/A for linear)")
    print(f"   Actual cap utilization: {result['emission_cap_utilization']:.1f}%")
    
    # Linear policy should return 0% (N/A)
    assert result['emission_cap_utilization'] == 0, \
        f"Linear policy should return 0% cap utilization, got {result['emission_cap_utilization']}%"
    
    print(f"   ✅ Linear policy cap utilization: PASSED")
    return True

def run_all_tests():
    """Run all emission cap utilization validation tests"""
    print("🧪 Emission Cap Utilization Validation Tests")
    print("=" * 50)
    
    try:
        test_emission_cap_utilization_under_cap()
        test_emission_cap_utilization_at_cap() 
        test_emission_cap_utilization_over_cap()
        test_emission_cap_utilization_linear_policy()
        
        print("\n" + "=" * 50)
        print("🎉 All Emission Cap Utilization Tests PASSED!")
        print("\n✅ Diagnostic functionality validated:")
        print("   • Cap utilization calculated correctly for all scenarios")
        print("   • Under cap: Shows actual percentage (e.g., 60%)")
        print("   • At cap: Shows 100% utilization") 
        print("   • Over cap: Shows over 100% (diagnostic of cap being hit)")
        print("   • Linear policy: Returns 0% (N/A, as expected)")
        print("\n📊 Enables policy analysis:")
        print("   • Track emission efficiency across different policies")
        print("   • Identify when per-device caps are too restrictive")
        print("   • Inform BME parameter design based on cap behavior")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    run_all_tests() 