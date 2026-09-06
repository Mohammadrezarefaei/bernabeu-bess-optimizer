def calculate_bankable_financials(annual_savings, capex_eur=3500000.0):
    """
    Computes financial metrics for a 70/30 debt-to-equity BESS project structure.
    - capex_eur: Estimated capital expenditure for a 5 MW / 10 MWh LFP system (~3.5M EUR)
    """
    debt_ratio = 0.70
    equity_ratio = 0.30
    
    total_debt = capex_eur * debt_ratio
    total_equity = capex_eur * equity_ratio
    
    # Annual operational and maintenance costs (estimated at 2% of Capex)
    annual_opex = capex_eur * 0.02
    net_annual_cash_flow = annual_savings - annual_opex
    
    # Simple Payback Period (Years)
    payback_period = capex_eur / net_annual_cash_flow if net_annual_cash_flow > 0 else 0
    
    # Estimated annual debt service (assuming 7% interest rate over 10 years)
    annual_interest_rate = 0.07
    loan_term_years = 10
    annual_debt_service = total_debt * (
        annual_interest_rate * (1 + annual_interest_rate)**loan_term_years
    ) / ((1 + annual_interest_rate)**loan_term_years - 1)
    
    # DSCR (Debt Service Coverage Ratio): Net Cash Flow / Annual Debt Service 
    # Banks typically look for a DSCR >= 1.25 for project finance stability
    dscr = net_annual_cash_flow / annual_debt_service if annual_debt_service > 0 else 0
    
    return {
        "Total_Capex_EUR": capex_eur,
        "Debt_70_Percent_EUR": total_debt,
        "Equity_30_Percent_EUR": total_equity,
        "Net_Annual_Cash_Flow_EUR": net_annual_cash_flow,
        "Payback_Period_Years": payback_period,
        "Annual_Debt_Service_EUR": annual_debt_service,
        "DSCR": dscr
    }
