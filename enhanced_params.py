"""
Enhanced parameter collection function for modular UI structure
"""
import streamlit as st

def collect_enhanced_parameters(config_params):
    """
    Collect parameters using enhanced modular structure:
    Core -> Node Economics -> Foundation -> Advanced -> Expert
    """
    
    st.sidebar.markdown("---")
    
    # Core Parameters (Essential for all users)
    st.sidebar.markdown("### 🏗️ Core Parameters")
    
    initial_nodes = st.sidebar.number_input(
        "Initial Node Amount",
        min_value=100,
        max_value=100000,
        value=int(config_params.get('initial_node_amount', [15000])[0]),
        step=500,
        help="🖥️ Number of nodes available at network launch"
    )
    
    resource_price = st.sidebar.number_input(
        "Resource Unit Price ($)",
        min_value=0.00001,
        max_value=1.0,
        value=float(config_params.get('resource_unit_price', [0.00002])[0]),
        format="%.6f",
        help="💰 Price per unit of network resource"
    )
    
    demand_growth = st.sidebar.slider(
        "Network Demand Growth Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=float(config_params.get('network_resource_demand_growth_rate', [0.02])[0]) * 100,
        step=0.1,
        help="📈 Daily demand growth rate"
    )
    
    apr_target = st.sidebar.slider(
        "Target APR (%)",
        min_value=5.0,
        max_value=50.0,
        value=float(config_params.get('apr_threshold', [15])[0]),
        step=1.0,
        help="🎯 Target annual return for node operators"
    )
    
    emission_policy = st.sidebar.selectbox(
        "Emission Policy",
        options=["linear", "per_device", "bme"],
        index=["linear", "per_device", "bme"].index(config_params.get('emission_policy', ['linear'])[0]),
        help="🪙 How tokens are distributed:\n• LINEAR: Fixed daily\n• PER-DEVICE: Scales with nodes\n• BME: Usage-driven"
    )
    
    # Emission policy specific parameters
    emission_per_device = None
    bme_burn_multiplier = None
    bme_mint_multiplier = None
    
    if emission_policy == "per_device":
        emission_per_device = st.sidebar.number_input(
            "Emission per Device (daily)",
            min_value=1,
            max_value=1000,
            value=int(config_params.get('emission_per_device_daily', [100])[0]),
            help="📱 Tokens per node per day"
        )
    elif emission_policy == "bme":
        bme_burn_multiplier = st.sidebar.slider(
            "BME Burn Rate Multiplier",
            min_value=0.1,
            max_value=2.0,
            value=float(config_params.get('bme_burn_rate_multiplier', [1.0])[0]),
            step=0.1,
            help="🔥 Revenue to burn conversion rate"
        )
        bme_mint_multiplier = st.sidebar.slider(
            "BME Mint Rate Multiplier",
            min_value=0.1,
            max_value=2.0,
            value=float(config_params.get('bme_mint_rate_multiplier', [1.0])[0]),
            step=0.1,
            help="🪙 Burn to mint conversion rate"
        )
    
    st.sidebar.markdown("---")
    
    # Node Economics (Important for realistic modeling)
    with st.sidebar.expander("🔧 Node Economics", expanded=False):
        st.markdown("**Node Operator Parameters**")
        
        node_setup_cost = st.number_input(
            "Node Setup Cost ($)",
            min_value=100.0,
            max_value=10000.0,
            value=float(config_params.get('node_setup_cost', [1000.0])[0]),
            step=100.0,
            help="💻 Hardware investment per node"
        )
        
        node_token_stake = st.number_input(
            "Node Token Stake (tokens)",
            min_value=1000,
            max_value=100000,
            value=int(config_params.get('node_token_stake', [10000])[0]),
            step=1000,
            help="🪙 Required token stake per node"
        )
        
        node_revenue_share = st.slider(
            "Node Revenue Share (%)",
            min_value=50.0,
            max_value=95.0,
            value=float(config_params.get('node_revenue_share', [0.75])[0]) * 100,
            step=1.0,
            help="💰 Percentage of revenue to operators"
        )
        
        node_reliability = st.slider(
            "Node Reliability (%)",
            min_value=80.0,
            max_value=99.9,
            value=float(config_params.get('node_reliability', [0.98])[0]) * 100,
            step=0.5,
            help="📡 Node uptime factor"
        )
        
        node_provision_rate = st.number_input(
            "Node Resource Provision Rate",
            min_value=10000,
            max_value=1000000,
            value=int(config_params.get('node_resource_provision_rate', [100000])[0]),
            step=10000,
            help="⚡ Max resources per node per day"
        )
        
        initial_network_demand = st.number_input(
            "Initial Network Demand",
            min_value=10000000,
            max_value=1000000000,
            value=int(config_params.get('initial_network_resource_demand', [300000000])[0]),
            step=10000000,
            help="🌐 Starting demand for network resources"
        )
    
    # Foundation Settings (Important for sustainability)  
    with st.sidebar.expander("🏢 Foundation Settings", expanded=False):
        st.markdown("**Protocol Sustainability**")
        
        foundation_revenue_share = st.slider(
            "Foundation Revenue Share (%)",
            min_value=5.0,
            max_value=40.0,
            value=float(config_params.get('foundation_revenue_share', [0.24])[0]) * 100,
            step=1.0,
            help="🏛️ Revenue for operations"
        )
        
        foundation_cash_burn = st.number_input(
            "Foundation Monthly Burn Rate ($)",
            min_value=50000,
            max_value=5000000,
            value=int(config_params.get('foundation_cash_burn_rate', [1000000])[0]),
            step=50000,
            help="💸 Monthly operational costs"
        )
        
        buyback_burn_share = st.slider(
            "Buyback & Burn Revenue Share (%)",
            min_value=0.0,
            max_value=10.0,
            value=float(config_params.get('buyback_and_burn_revenue_share', [0.01])[0]) * 100,
            step=0.5,
            help="🔥 Revenue used for token buybacks"
        )
    
    # Advanced Parameters (Existing functionality)  
    with st.sidebar.expander("🎯 Advanced Parameters", expanded=False):
        st.markdown("**Token Allocation**")
        
        incentive_allocation = st.slider(
            "Incentive Token Allocation (%)",
            min_value=5.0,
            max_value=50.0,
            value=float(config_params.get('incentive_token_allocation', [0.08])[0]) * 100,
            step=1.0,
            help="🎁 Tokens for node incentives"
        )
        
        seller_allocation = st.slider(
            "Seller Token Allocation (%)",
            min_value=20.0,
            max_value=60.0,
            value=float(config_params.get('seller_token_allocation', [0.4])[0]) * 100,
            step=1.0,
            help="👥 Tokens for team/investors"
        )
        
        seller_vesting_days = st.number_input(
            "Seller Vesting Duration (days)",
            min_value=180,
            max_value=2000,
            value=int(config_params.get('seller_token_vesting_duration', [1095])[0]),
            step=30,
            help="⏰ Team/investor vesting period"
        )
        
        incentive_vesting_days = st.number_input(
            "Incentive Vesting Duration (days)",
            min_value=365,
            max_value=3650,
            value=int(config_params.get('incentive_token_vesting_duration', [1460])[0]),
            step=30,
            help="⏰ Node incentive vesting period"
        )
        
        st.markdown("**Growth Controls**")
        
        node_growth_cap = st.slider(
            "Node Growth Cap (% per day)",
            min_value=0.5,
            max_value=10.0,
            value=float(config_params.get('node_growth_cap', [3])[0]),
            step=0.5,
            help="🚀 Max node growth rate"
        )
        
        # Demand Growth Model (Existing)
        st.markdown("**Demand Growth Model**")
        default_growth_scenario = config_params.get('business_growth_scenario', ['linear'])[0]
        growth_scenario = st.selectbox(
            "Growth Scenario",
            options=['linear', 'exponential', 'logarithmic', 'custom_phases'],
            index=['linear', 'exponential', 'logarithmic', 'custom_phases'].index(default_growth_scenario) if default_growth_scenario in ['linear', 'exponential', 'logarithmic', 'custom_phases'] else 0
        )
        
        phases = []
        milestones = []
        
        if growth_scenario == 'custom_phases':
            # Simplified custom phases for now - keep existing logic
            default_phases = config_params.get('business_growth_phases', [[]])
            default_num_phases = len(default_phases[0]) if default_phases and len(default_phases[0]) > 0 else 3
            
            num_phases = st.number_input("Number of Phases", min_value=1, max_value=6, value=int(default_num_phases))
            
            for i in range(num_phases):
                def_days = default_phases[0][i].get('days', 90) if i < len(default_phases[0]) else 90
                def_rate = default_phases[0][i].get('daily_growth_rate', 0.02) if i < len(default_phases[0]) else 0.02
                
                p_days = st.number_input(f"Phase {i+1} Days", min_value=1, max_value=2000, value=int(def_days), key=f"phase_days_{i}")
                p_rate = st.number_input(f"Phase {i+1} Growth (%)", min_value=-5.0, max_value=10.0, value=float(def_rate), step=0.01, key=f"phase_rate_{i}")
                
                phases.append({
                    'days': p_days,
                    'daily_growth_rate': p_rate,
                    'description': f'Phase {i+1} - {p_rate}% daily growth for {p_days} days'
                })
        
        # Market Dynamics (Existing)
        st.markdown("**Market Dynamics**")
        
        token_market_scenario = st.selectbox(
            "Token Market Scenario",
            options=['stable', 'bull_market', 'bear_market', 'volatile'],
            index=['stable', 'bull_market', 'bear_market', 'volatile'].index(config_params.get('token_market_scenario', ['stable'])[0]) if config_params.get('token_market_scenario', ['stable'])[0] in ['stable', 'bull_market', 'bear_market', 'volatile'] else 0
        )
        
        speculation_factor = st.slider(
            "Token Speculation Factor",
            min_value=0.0,
            max_value=2.0,
            value=float(config_params.get('token_speculation_factor', [0.3])[0]),
            step=0.1
        )
        
        # Utilization Controller (Existing)
        utilization_controller = st.checkbox(
            "Enable Utilization Controller",
            value=bool(config_params.get('utilization_controller_enabled', [False])[0])
        )
        
        utilization_target = 80.0
        if utilization_controller:
            utilization_target = st.slider(
                "Utilization Target (%)",
                min_value=60.0,
                max_value=95.0,
                value=float(config_params.get('utilization_target', [0.8])[0]) * 100,
                step=1.0
            )
        
        # Dynamic Pricing (Existing)
        dynamic_pricing = st.checkbox(
            "Enable Dynamic Resource Pricing",
            value=bool(config_params.get('resource_price_adjustment_enabled', [True])[0])
        )
        
        price_sensitivity = 0.3
        if dynamic_pricing:
            price_sensitivity = st.slider(
                "Price Sensitivity",
                min_value=0.0,
                max_value=1.0,
                value=float(config_params.get('resource_price_utilization_sensitivity', [0.3])[0]),
                step=0.05
            )
    
    # Return all collected parameters
    return {
        # Core parameters
        'initial_nodes': initial_nodes,
        'resource_price': resource_price,
        'demand_growth': demand_growth,
        'apr_target': apr_target,
        'emission_policy': emission_policy,
        'emission_per_device': emission_per_device,
        'bme_burn_multiplier': bme_burn_multiplier,
        'bme_mint_multiplier': bme_mint_multiplier,
        
        # Node economics (with defaults for when expander is closed)
        'node_setup_cost': locals().get('node_setup_cost', config_params.get('node_setup_cost', [1000.0])[0]),
        'node_token_stake': locals().get('node_token_stake', config_params.get('node_token_stake', [10000])[0]),
        'node_revenue_share': locals().get('node_revenue_share', config_params.get('node_revenue_share', [0.75])[0] * 100),
        'node_reliability': locals().get('node_reliability', config_params.get('node_reliability', [0.98])[0] * 100),
        'node_provision_rate': locals().get('node_provision_rate', config_params.get('node_resource_provision_rate', [100000])[0]),
        'initial_network_demand': locals().get('initial_network_demand', config_params.get('initial_network_resource_demand', [300000000])[0]),
        
        # Foundation (with defaults)
        'foundation_revenue_share': locals().get('foundation_revenue_share', config_params.get('foundation_revenue_share', [0.24])[0] * 100),
        'foundation_cash_burn': locals().get('foundation_cash_burn', config_params.get('foundation_cash_burn_rate', [1000000])[0]),
        'buyback_burn_share': locals().get('buyback_burn_share', config_params.get('buyback_and_burn_revenue_share', [0.01])[0] * 100),
        
        # Advanced (with defaults)
        'incentive_allocation': locals().get('incentive_allocation', config_params.get('incentive_token_allocation', [0.08])[0] * 100),
        'seller_allocation': locals().get('seller_allocation', config_params.get('seller_token_allocation', [0.4])[0] * 100),
        'seller_vesting_days': locals().get('seller_vesting_days', config_params.get('seller_token_vesting_duration', [1095])[0]),
        'incentive_vesting_days': locals().get('incentive_vesting_days', config_params.get('incentive_token_vesting_duration', [1460])[0]),
        'node_growth_cap': locals().get('node_growth_cap', config_params.get('node_growth_cap', [3])[0]),
        'growth_scenario': locals().get('growth_scenario', 'linear'),
        'phases': phases,
        'milestones': milestones,
        'token_market_scenario': locals().get('token_market_scenario', 'stable'),
        'speculation_factor': locals().get('speculation_factor', 0.3),
        'utilization_controller': locals().get('utilization_controller', False),
        'utilization_target': utilization_target,
        'dynamic_pricing': locals().get('dynamic_pricing', True),
        'price_sensitivity': price_sensitivity
    }