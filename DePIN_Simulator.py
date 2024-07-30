# Dependences
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

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
TIMESTEPS = 365*10
MONTE_CARLO_RUNS = 1

model = Model(initial_state=initial_state, params=sys_params, state_update_blocks=state_update_blocks)
simulation = Simulation(model=model, timesteps=TIMESTEPS, runs=MONTE_CARLO_RUNS)

def main():

    # run the simulation
    result = simulation.run()
    df = pd.DataFrame(result)
    # get amount of distinct subsets in the simulation
    subsets = df['subset'].unique()

    # prepare the plots
    fig, axarr = plt.subplots(4,4, figsize=(16,12))
    custom_lines = [Line2D([0], [0], linestyle='solid', color='black'),
                    Line2D([0], [0], linestyle='dashed', color='black'),
                    Line2D([0], [0], linestyle=':', color='black'),]

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
        axarr[0,0].plot(rdf.timestep, rdf.network_resource_demand, label=legend_text, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,0].set_title('Network Resource Demand / Resource Units')
        axarr[0,0].grid('on', which='both')
        axarr[0,0].legend()

         # Network Utilization
        axarr[1,0].plot(rdf.timestep, rdf.network_resource_demand_supply_ratio, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[1,0].set_title('Network Demand / Supply Ratio / -')
        axarr[1,0].grid('on', which='both')

        # Node Amounts
        axarr[2,0].plot(rdf.timestep, rdf.node_amount, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[2,0].set_title('Node Amounts / Nodes')
        axarr[2,0].grid('on', which='both')
        axarr[2,0].set_yscale('log')

        # Node Change Amounts
        axarr[3,0].plot(rdf.timestep, rdf.node_change_amount, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,0].set_title('Node Change Amounts / Nodes')
        axarr[3,0].grid('on', which='both')

        # Node APR
        axarr[0,1].plot(rdf.timestep, rdf.node_apr, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,1].set_title('Node APR / %')
        axarr[0,1].set_xlabel('Days')
        axarr[0,1].grid('on', which='both')

        # Node Profit
        axarr[1,1].plot(rdf.timestep, rdf.node_profit, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[1,1].set_title('Node Profit / $')
        axarr[1,1].grid('on', which='both')
        axarr[1,1].set_yscale('log')

        # Node Network and Incentive Revenue 
        axarr[2,1].plot(rdf.timestep, rdf.node_network_revenue, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Network', linestyle='solid')
        axarr[2,1].plot(rdf.timestep, rdf.node_incentive_revenue, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Incentives', linestyle='dashed')
        axarr[2,1].set_title('Node Revenue / $')
        axarr[2,1].legend(custom_lines, ['Network', 'Incentives'])
        axarr[2,1].grid('on', which='both')
        axarr[2,1].set_yscale('log')

        # Node Expenditures
        axarr[3,1].plot(rdf.timestep, rdf.node_expenditures, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,1].set_title('Node Expenditures / %')
        axarr[3,1].set_xlabel('Days')
        axarr[3,1].grid('on', which='both')
        axarr[3,1].set_yscale('log')

        # DEX Token Price
        axarr[0,2].plot(rdf.timestep, rdf.dex_token_price, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,2].set_title('DEX Token Price / $')
        axarr[0,2].grid('on', which='both')
        axarr[0,2].set_yscale('log')

        # Liquidity Pool Reserves
        print(rdf.dex_tokens)
        print(rdf.dex_usdc)
        axarr[1,2].plot(rdf.timestep, rdf.dex_tokens, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[1,2].plot(rdf.timestep, rdf.dex_usdc, color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[1,2].set_title('Liquidity Pool Reserves / $')
        axarr[1,2].grid('on', which='both')
        axarr[1,2].legend(custom_lines, ['Token', 'USDC'])

        # Token Vesting
        axarr[2,2].plot(rdf.timestep, rdf.token_seller_vested, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Seller Vested', linestyle='solid')
        axarr[2,2].plot(rdf.timestep, rdf.token_incentives_vested, color=list(mcolors.TABLEAU_COLORS.keys())[subset], label='Incentive Vested', linestyle='dashed')
        axarr[2,2].set_title('Cumulative Token Vesting / Tokens')
        axarr[2,2].legend(custom_lines, ['Seller Vested', 'Incentive Vested'])
        axarr[2,2].grid('on', which='both')

        # Token Staked Supply
        axarr[3,2].plot(rdf.timestep, rdf.token_staked_supply / initial_values['token_initial_total_supply']*100, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[3,2].set_title('Token Staked Supply / %')
        axarr[3,2].set_xlabel('Days')
        axarr[3,2].grid('on', which='both')

        # Foundation Financial Reserves
        axarr[0,3].plot(rdf.timestep, rdf.foundation_cash_reserves, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[0,3].set_title('Foundation Cash Reserves / $')
        axarr[0,3].grid('on', which='both')

        # Foundation Finances
        axarr[1,3].plot(rdf.timestep, rdf.foundation_revenue - rdf.foundation_expenditures, color=list(mcolors.TABLEAU_COLORS.keys())[subset])
        axarr[1,3].set_title('Foundation Cash Flow / $')
        axarr[1,3].grid('on', which='both')

        # Token Mint & Burn Supply
        axarr[2,3].plot(rdf.timestep, rdf.token_burned_supply_cum / initial_values['token_initial_total_supply']*100, label='Burned', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[2,3].plot(rdf.timestep, rdf.token_minted_supply_cum / initial_values['token_initial_total_supply']*100, label='Minted', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[2,3].set_title('Token Burn & Mint Supply / %')
        axarr[2,3].legend(custom_lines, ['Burned', 'Minted'])
        axarr[2,3].grid('on', which='both')

        # Token Ecosystem Supply
        axarr[3,3].plot(rdf.timestep, rdf.token_total_supply / initial_values['token_initial_total_supply']*100, label='Total Supply', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='solid')
        axarr[3,3].plot(rdf.timestep, rdf.token_circulating_supply / initial_values['token_initial_total_supply']*100, label='Circulating Supply', color=list(mcolors.TABLEAU_COLORS.keys())[subset], linestyle='dashed')
        axarr[3,3].set_title('Token Ecosystem Supply / %')
        axarr[3,3].set_xlabel('Days')
        axarr[3,3].legend(custom_lines, ['Total Supply', 'Circulating Supply'])
        axarr[3,3].grid('on', which='both')

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

