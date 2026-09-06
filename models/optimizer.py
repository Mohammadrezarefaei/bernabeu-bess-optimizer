import pulp
import numpy as np

def run_bess_optimization(load_series, market_params, power_mw=5.0, capacity_mwh=10.0, eff=0.95):
    """
    Linear programming optimization engine for BESS peak shaving and energy arbitrage
    under Spanish market conditions for bankable financial evaluation.
    """
    timesteps = len(load_series)
    dt = 0.25 # 15-minute intervals
    
    base_price = np.full(96, market_params["base_price"])
    base_price[32:60] = market_params["base_price"] * 0.6  # Cheap solar hours
    base_price[64:88] = market_params["peak_price"]        # Evening peak
    demand_charge_rate = market_params["demand_charge"]
    
    prob = pulp.LpProblem("Bernabeu_BESS_Optimization", pulp.LpMinimize)
    
    p_ch = [pulp.LpVariable(f"P_ch_{t}", 0, power_mw) for t in range(timesteps)]
    p_dis = [pulp.LpVariable(f"P_dis_{t}", 0, power_mw) for t in range(timesteps)]
    soc = [pulp.LpVariable(f"SoC_{t}", 0.1 * capacity_mwh, capacity_mwh) for t in range(timesteps + 1)]
    peak_grid = pulp.LpVariable("Peak_Grid", 0)
    
    # Boundary conditions
    prob += (soc[0] == 0.5 * capacity_mwh)
    prob += (soc[timesteps] == 0.5 * capacity_mwh)
    
    # Objective function: Minimize total energy cost plus demand charge penalty
    energy_cost = pulp.lpSum([(load_series[t] + p_ch[t] - p_dis[t]) * base_price[t] * dt for t in range(timesteps)])
    prob += energy_cost + (peak_grid * demand_charge_rate)
    
    # Constraints loop
    for t in range(timesteps):
        prob += (load_series[t] + p_ch[t] - p_dis[t] <= peak_grid)
        prob += (soc[t+1] == soc[t] + (p_ch[t] * eff - p_dis[t] / eff) * dt)
        
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    optimized_load = [load_series[t] + pulp.value(p_ch[t]) - pulp.value(p_dis[t]) for t in range(timesteps)]
    baseline_cost = sum(load_series[t] * base_price[t] * dt for t in range(timesteps)) + (max(load_series) * demand_charge_rate)
    optimized_cost = pulp.value(prob.objective)
    daily_savings = baseline_cost - optimized_cost
    
    return {
        "Status": pulp.LpStatus[prob.status],
        "Baseline_Cost": baseline_cost,
        "Optimized_Cost": optimized_cost,
        "Daily_Savings": daily_savings,
        "Annual_Savings": daily_savings * 365,
        "Peak_Grid_MW": pulp.value(peak_grid),
        "Optimized_Load": optimized_load
    }
