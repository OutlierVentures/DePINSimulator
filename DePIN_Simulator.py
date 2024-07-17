# Dependences
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# radCAD
from radcad import Model, Simulation, Experiment
from radcad.engine import Engine, Backend

# Experiments
from model import run
pd.options.display.float_format = '{:.5f}'.format

from model.sys_params import sys_params, initial_values
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks

# Set the number of timesteps and runs for the simulation
TIMESTEPS = 365*6
MONTE_CARLO_RUNS = 1

model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

def main():
    result = simulation.run()
    df = pd.DataFrame(result)

    # prepare the plots
    fig, axarr = plt.subplots(4,3, figsize=(16,12))
    
    # get amount of distinct subsets in the simulation
    subsets = df['subset'].unique()

    for subset in subsets:
        subset_df = df[df['subset'] == subset]

        # get the destinctive parameters from sys_params for the subset if they have more than one values in their list
        sweep_params = {key: value for key, value in sys_params.items() if len(value) > 1}
        # compose the legend text for this subset
        legend_text = ''
        for key, value in sweep_params.items():
            # format key
            key_formatted = key.split("network_")[1] if "network_" in key else key
            key_formatted = key_formatted.replace("_"," ")
            
            # construct the legend text
            try:
                legend_text += f'{key_formatted}: {"{:.2e}".format(value[subset])}; '
            except:
                pass

        rdf = run.postprocessing(subset_df)

        # Network Resource Demand
        axarr[0,0].plot(rdf.timestep, rdf.network_resource_demand, label=legend_text)
        axarr[0,0].set_title('Network Resource Demand')
        axarr[0,0].grid('on', which='both')
        axarr[0,0].legend()

        # Node Amounts
        axarr[1,0].plot(rdf.timestep, rdf.node_amount)
        axarr[1,0].set_title('Node Amounts')
        axarr[1,0].grid('on', which='both')
        axarr[1,0].set_yscale('log')

        # Node Change Amounts
        axarr[2,0].plot(rdf.timestep, rdf.node_change_amount, label=subset)
        axarr[2,0].set_title('Node Change Amounts')
        axarr[2,0].grid('on', which='both')

        # Node APR
        axarr[3,0].plot(rdf.timestep, rdf.node_apr, label=subset)
        axarr[3,0].set_title('Node APR')
        axarr[3,0].set_xlabel('Days')
        axarr[3,0].grid('on', which='both')

        # Node Profit
        axarr[0,1].plot(rdf.timestep, rdf.node_profit, label=subset)
        axarr[0,1].set_title('Node Profit')
        axarr[0,1].grid('on', which='both')
        axarr[0,1].set_yscale('log')

        # Node Network Revenue
        axarr[1,1].plot(rdf.timestep, rdf.node_network_revenue, label=subset)
        axarr[1,1].set_title('Node Network Revenue')
        axarr[1,1].grid('on', which='both')
        axarr[1,1].set_yscale('log')

        # Node Incentive Revenue
        axarr[2,1].plot(rdf.timestep, rdf.node_incentive_revenue, label=subset)
        axarr[2,1].set_title('Node Incentive Revenue')
        axarr[2,1].grid('on', which='both')
        axarr[2,1].set_yscale('log')

        # Node Expenditures
        axarr[3,1].plot(rdf.timestep, rdf.node_expenditures, label=subset)
        axarr[3,1].set_title('Node Expenditures')
        axarr[3,1].set_xlabel('Days')
        axarr[3,1].grid('on', which='both')
        axarr[3,1].set_yscale('log')

        # DEX Token Price
        axarr[0,2].plot(rdf.timestep, rdf.dex_token_price, label=subset)
        axarr[0,2].set_title('DEX Token Price')
        axarr[0,2].grid('on', which='both')
        axarr[0,2].set_yscale('log')

        # token seller vested
        axarr[1,2].plot(rdf.timestep, rdf.token_seller_vested, label=subset)
        axarr[1,2].set_title('Token Seller Vested')
        axarr[1,2].grid('on', which='both')

        # token incentives vested
        axarr[2,2].plot(rdf.timestep, rdf.token_incentives_vested, label=subset)
        axarr[2,2].set_title('Token Incentives Vested')
        axarr[2,2].grid('on', which='both')

        # Token Staked Supply
        axarr[3,2].plot(rdf.timestep, rdf.token_staked_supply / initial_values['token_initial_total_supply']*100, label=subset)
        axarr[3,2].set_title('Token Staked Supply / %')
        axarr[3,2].set_xlabel('Days')
        axarr[3,2].grid('on', which='both')


    plt.tight_layout()
    plt.show()



    #rdf = run.postprocessing(df)
    

    # plot results
    """rdf.plot(x='timestep', y=['network_resource_demand', 'dex_tokens', 'dex_usdc', 'dex_token_price',
                            'token_incentives_vested', 'token_seller_vested', 'token_incentives_vested_cum',
                            'token_seller_vested_cum'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')
    
    rdf.pivot(index='timestep', columns='subset', values=['node_amount']).plot(title='Node Amounts')
    rdf.pivot(index='timestep', columns='subset', values=['dex_token_price']).plot(title='Token Price')
    rdf.plot(x='timestep', y=['node_amount', 'node_change_amount', 'token_staked_supply', 'node_apr',
                                'node_network_revenue', 'node_incentive_revenue', 'node_profit', 'node_expenditures'], subplots=True, layout=(4, 2), figsize=(15, 10), title='DePIN Simulation Results')
    """

if __name__ == "__main__":
    main()

