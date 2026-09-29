import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    print("Hello, World!")
    return


@app.cell
def _():
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.integrate import solve_ivp


    return np, plt, solve_ivp


@app.function
def regional_model(t, state, params, scenario):
    """Система динамики технологического, социально-экономического,
    инвестиционно-инновационного и экологического потенциалов региона."""
    T, S, I, E = state

    alpha_1 = params["alpha_1"]
    alpha_2 = params["alpha_2"]
    beta_1 = params["beta_1"]
    beta_2 = params["beta_2"]

    gamma_1 = params["gamma_1"]
    gamma_2 = params["gamma_2"]
    delta_1 = params["delta_1"]
    delta_2 = params["delta_2"]

    eta_1 = params["eta_1"]
    eta_2 = params["eta_2"]
    mu_1 = params["mu_1"]
    mu_2 = params["mu_2"]

    rho_1 = params["rho_1"]
    rho_2 = params["rho_2"]
    omega = params["omega"]

    H = scenario["human_capital"]
    Y = scenario["economic_result"]
    P = scenario["industrial_policy"]
    R = scenario["constraints"]
    Q = scenario["extraction_intensity"]
    Z = scenario["environmental_measures"]

    dT_dt = alpha_1 * I + alpha_2 * H - beta_1 * T - beta_2 * E
    dS_dt = gamma_1 * T + gamma_2 * Y - delta_1 * S - delta_2 * E
    dI_dt = eta_1 * P + eta_2 * S - mu_1 * I - mu_2 * R
    dE_dt = rho_1 * Q - rho_2 * Z - omega * E

    return [dT_dt, dS_dt, dI_dt, dE_dt]


@app.cell
def _():
    params = {
        "alpha_1": 0.30,
        "alpha_2": 0.20,
        "beta_1": 0.08,
        "beta_2": 0.05,
        "gamma_1": 0.25,
        "gamma_2": 0.20,
        "delta_1": 0.05,
        "delta_2": 0.08,
        "eta_1": 0.30,
        "eta_2": 0.15,
        "mu_1": 0.10,
        "mu_2": 0.12,
        "rho_1": 0.25,
        "rho_2": 0.30,
        "omega": 0.10,
    }

    return (params,)


@app.cell
def _():
    scenarios = {
        "Инерционный": {
            "human_capital": 0.55,
            "economic_result": 0.65,
            "industrial_policy": 0.45,
            "constraints": 0.45,
            "extraction_intensity": 0.75,
            "environmental_measures": 0.35,
        },
        "Технологическая модернизация": {
            "human_capital": 0.70,
            "economic_result": 0.70,
            "industrial_policy": 0.75,
            "constraints": 0.30,
            "extraction_intensity": 0.72,
            "environmental_measures": 0.55,
        },
        "Сбалансированное развитие": {
            "human_capital": 0.78,
            "economic_result": 0.72,
            "industrial_policy": 0.78,
            "constraints": 0.25,
            "extraction_intensity": 0.65,
            "environmental_measures": 0.78,
        },
    }

    return (scenarios,)


@app.cell
def _(np, plt):

    initial_state = [0.45, 0.55, 0.40, 0.60]
    time = np.linspace(0, 15, 301)
    weights = {"T": 0.30, "S": 0.30, "I": 0.20, "E": 0.20}

    variables = ["Технологический потенциал", "Социально-экономический потенциал",
                 "Инвестиционно-инновационная активность", "Экологическая нагрузка"]

    return initial_state, time, variables, weights


@app.cell
def _(initial_state, params, plt, scenarios, solve_ivp, time, variables, weights):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    axes = axes.ravel()
    results = {}

    for _name, _scenario in scenarios.items():
        solution = solve_ivp(
            regional_model,
            t_span=(time[0], time[-1]),
            y0=initial_state,
            t_eval=time,
            args=(params, _scenario),
            method="RK45",
        )

        if not solution.success:
            raise RuntimeError(solution.message)

        T, S, I, E = solution.y
        U = (
            weights["T"] * T
            + weights["S"] * S
            + weights["I"] * I
            - weights["E"] * E
        )
        results[_name] = {"T": T, "S": S, "I": I, "E": E, "U": U}

        for _ax, _series in zip(axes, (T, S, I, E)):
            _ax.plot(time, _series, label=_name, linewidth=2)

    for _ax, _title in zip(axes, variables):
        _ax.set_title(_title)
        _ax.set_xlabel("Условное время")
        _ax.set_ylabel("Нормированный индекс")
        _ax.grid(True, alpha=0.3)
        _ax.legend(fontsize=8)

    fig.tight_layout()
    fig
    return fig, results


@app.cell
def _(plt, results, time):
    summary_fig, summary_ax = plt.subplots(figsize=(8, 5))
    for _name, _result in results.items():
        summary_ax.plot(time, _result["U"], label=_name, linewidth=2)

    summary_ax.set_title("Интегральный индекс сбалансированного устойчивого развития")
    summary_ax.set_xlabel("Условное время")
    summary_ax.set_ylabel("Индекс U(t)")
    summary_ax.grid(True, alpha=0.3)
    summary_ax.legend()
    summary_fig.tight_layout()

    for _name, _result in results.items():
        print(
            _name,
            "T =", round(_result["T"][-1], 3),
            "S =", round(_result["S"][-1], 3),
            "I =", round(_result["I"][-1], 3),
            "E =", round(_result["E"][-1], 3),
            "U =", round(_result["U"][-1], 3),
        )

    summary_fig
    return summary_ax, summary_fig


if __name__ == "__main__":
    app.run()
