import marimo

__generated_with = "0.24.0"
app = marimo.App()


@app.cell
def _():
    #----------------------------------------------------------------
    # импорт необходимых модулей

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.integrate import solve_ivp

    return mo, np, plt, solve_ivp


@app.function
def linear_path(t, start, end, start_year=2024.0, end_year=2030.0):
    """Линейная сценарная траектория с фиксацией значений вне горизонта."""
    share = min(1.0, max(0.0, (t - start_year) / (end_year - start_year)))
    return start + share * (end - start)


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

    H = linear_path(t, *scenario["human_capital"])
    M = linear_path(t, *scenario["macro_impulse"])
    P = linear_path(t, *scenario["industrial_policy"])
    R = linear_path(t, *scenario["constraints"])
    Q = linear_path(t, *scenario["extraction_intensity"])
    Z = linear_path(t, *scenario["environmental_measures"])

    # Насыщение (1-X) и пропорциональный отток удерживают состояния
    # в интервале [0, 1] при неотрицательных коэффициентах и входах.
    dT_dt = (alpha_1 * I + alpha_2 * H) * (1 - T) - (beta_1 + beta_2 * E) * T
    dS_dt = (gamma_1 * T + gamma_2 * M) * (1 - S) - (delta_1 + delta_2 * E) * S
    dI_dt = (eta_1 * P + eta_2 * S) * (1 - I) - (mu_1 + mu_2 * R) * I
    dE_dt = rho_1 * Q * (1 - E) - (rho_2 * Z + omega) * E

    return [dT_dt, dS_dt, dI_dt, dE_dt]


@app.cell
def _(np):
    # Периоды полураспада воспроизводят исходные коэффициенты затухания,
    # но делают их интерпретацию явной. Это пока модельные допущения,
    # а не параметры, оцененные по данным Югры.
    half_lives = {
        "technology": np.log(2) / 0.08,
        "social": np.log(2) / 0.05,
        "investment": np.log(2) / 0.10,
        "environment": np.log(2) / 0.10,
    }
    params = {
        "alpha_1": 0.30,
        "alpha_2": 0.20,
        "beta_1": np.log(2) / half_lives["technology"],
        "beta_2": 0.05,
        "gamma_1": 0.25,
        "gamma_2": 0.20,
        "delta_1": np.log(2) / half_lives["social"],
        "delta_2": 0.08,
        "eta_1": 0.30,
        "eta_2": 0.15,
        "mu_1": np.log(2) / half_lives["investment"],
        "mu_2": 0.12,
        "rho_1": 0.25,
        "rho_2": 0.30,
        "omega": np.log(2) / half_lives["environment"],
    }
    return (params,)


@app.cell
def _():
    # Каждая пара означает (уровень в 2024 году, уровень в 2030 году).
    # Будущие значения являются сценарными допущениями, а не официальным
    # точечным прогнозом. В сценариях меняется ограниченный набор мер,
    # чтобы эффект политики не был заранее предопределен всеми входами сразу.
    scenarios = {
        "Базовый": {
            "human_capital": (0.55, 0.55),
            "macro_impulse": (0.50, 0.50),
            "industrial_policy": (0.30, 0.34),
            "constraints": (0.45, 0.40),
            "extraction_intensity": (1.00, 0.90),
            "environmental_measures": (0.35, 0.42),
        },
        "Технологическая модернизация": {
            "human_capital": (0.55, 0.55),
            "macro_impulse": (0.50, 0.50),
            "industrial_policy": (0.30, 0.55),
            "constraints": (0.45, 0.40),
            "extraction_intensity": (1.00, 0.90),
            "environmental_measures": (0.35, 0.42),
        },
        "Экологический": {
            "human_capital": (0.55, 0.55),
            "macro_impulse": (0.50, 0.50),
            "industrial_policy": (0.30, 0.34),
            "constraints": (0.45, 0.40),
            "extraction_intensity": (1.00, 0.90),
            "environmental_measures": (0.35, 0.65),
        },
        "Комбинированный": {
            "human_capital": (0.55, 0.55),
            "macro_impulse": (0.50, 0.50),
            "industrial_policy": (0.30, 0.55),
            "constraints": (0.45, 0.40),
            "extraction_intensity": (1.00, 0.90),
            "environmental_measures": (0.35, 0.65),
        },
    }
    return (scenarios,)


@app.cell
def _(mo):
    data_note = mo.md(r"""
    ### Данные и прогноз до 2030 года

    2024 год принят как базовый, а значения входов в 2030 году являются
    прозрачными сценарными предположениями (Примечание: не являются официальным
    прогнозом. Траектория добычи снижается от 1,00 до 0,90: официальные документы
    Югры фиксировали снижение добычи нефти с 223,1 млн т в 2022 году до 216,0
    млн т в 2023 году и оценку около 208 млн т на следующий период. Индекс
    промышленной политики начинается с умеренного уровня 0,30: Тюменьстат
    сообщает, что затраты на инновации снизились со 133,0 млрд руб. в 2020 году
    до 35,7 млрд руб. в 2024 году, а технологические инновации осуществляли
    9,5% обследованных организаций. Поэтому рост до 0,55 в технологическом
    сценарии — целевое управленческое усилие, а не экстраполяция наблюдаемого
    тренда.

    Источники: [Инвестиционная декларация Югры](https://investugra.ru/upload/004/%D0%A0%D0%B0%D1%81%D0%BF%D0%BE%D1%80%D1%8F%D0%B6%D0%B5%D0%BD%D0%B8%D0%B5%2044-%D1%80%D0%B3.pdf),
    [Тюменьстат — наука и инновации](https://72.rosstat.gov.ru/ofs_nauka_ug),
    [инфографика Тюменьстата за 2024 год](https://72.rosstat.gov.ru/storage/mediabank/%D0%94%D0%B5%D0%BD%D1%8C%20%D0%BD%D0%B0%D1%83%D0%BA%D0%B8_%D0%A5%D0%9C%D0%90%D0%9E_050226.pdf).
    """)
    data_note
    return


@app.cell
def _(np):

    initial_state = [0.45, 0.55, 0.40, 0.60]
    time = np.linspace(2024, 2030, 73)
    weights = {"T": 0.30, "S": 0.30, "I": 0.20, "E": 0.20}

    variables = ["Технологический потенциал", "Социально-экономический потенциал",
                 "Инвестиционно-инновационная активность", "Экологическая нагрузка"]
    return initial_state, time, variables, weights


@app.cell
def _(
    initial_state,
    params,
    plt,
    scenarios,
    solve_ivp,
    time,
    variables,
    weights,
):
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
        _ax.set_xlabel("Год")
        _ax.set_ylabel("Нормированный индекс")
        _ax.grid(True, alpha=0.3)
        _ax.legend(fontsize=8)

    fig.tight_layout()
    fig
    return (results,)


@app.cell
def _(plt, results, time):
    summary_fig, summary_ax = plt.subplots(figsize=(8, 5))
    for _name, _result in results.items():
        summary_ax.plot(time, _result["U"], label=_name, linewidth=2)

    summary_ax.set_title("Интегральный индекс сбалансированного устойчивого развития")
    summary_ax.set_xlabel("Год")
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
    return


if __name__ == "__main__":
    app.run()
