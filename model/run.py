import pandas as pd

def postprocessing(df):
    '''
    Definition:
    Refine and extract metrics from the simulation
    
    Parameters:
    df: simulation dataframe
    '''
    # subset to last substep
    df = df[df['substep'] == df.substep.max()]

    # Get the results
    timesteps = df.timestep
    
    # Get metrics
    """ 
    ## Agent quantity
    prey_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'prey']))
    predator_count = agent_ds.map(lambda s: sum([1 for agent in s.values() if agent['type'] == 'predator']))


    ## Food quantity
    food_at_sites = site_ds.map(lambda s: s.sum())
    food_at_prey = agent_ds.map(lambda s: sum([agent['food'] 
                                               for agent 
                                               in s.values() if agent['type'] == 'prey']))
    food_at_predators = agent_ds.map(lambda s: sum([agent['food'] 
                                                    for agent in s.values() 
                                                    if agent['type'] == 'predator']))

    ## Food metrics
    median_site_food = site_ds.map(lambda s: np.median(s)) 
    median_prey_food = agent_ds.map(lambda s: np.median([agent['food'] 
                                                         for agent in s.values() 
                                                         if agent['type'] == 'prey']))
    median_predator_food = agent_ds.map(lambda s: np.median([agent['food'] 
                                                             for agent in s.values() 
                                                             if agent['type'] == 'predator'])) """


    # Create an analysis dataset
    data = (pd.DataFrame({'timestep': timesteps,
                          'run': df.run,
                          'network_resource_demand': df.network_resource_demand,
                          'dex_tokens': df.dex_tokens,
                          'dex_usdc': df.dex_usdc,
                          'dex_token_price': df.dex_token_price,
                          'token_incentives_vested': df.token_incentives_vested,
                          'token_seller_vested': df.token_seller_vested,
                          'token_incentives_vested_cum': df.token_incentives_vested_cum,
                          'token_seller_vested_cum': df.token_seller_vested_cum,
                          'node_amount': df.node_amount,
                          'node_resource_provision': df.node_resource_provision,
                          'node_revenue': df.node_revenue,
                          'node_expenditures': df.node_expenditures,
                          'node_apr': df.node_apr,
                          'node_change_amount': df.node_change_amount,
                          'token_total_supply': df.token_total_supply,
                          'token_burned_supply': df.token_burned_supply,
                          'token_minted_supply': df.token_minted_supply,
                          'token_circulating_supply': df.token_circulating_supply,
                          'token_staked_supply': df.token_staked_supply,
                          'foundation_revenue': df.foundation_revenue,
                          'foundation_expenditures': df.foundation_expenditures,
                          'foundation_cash_reserves': df.foundation_cash_reserves,
                          })       
           )
    
    return data