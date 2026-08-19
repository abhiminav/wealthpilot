import { useState } from "react";
import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ShieldCheck,
  Target,
  TrendingUp,
} from "lucide-react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./App.css";

const API_URL = "http://localhost:8000";

type Fund = {
  scheme_name: string;
  fund_house: string;
  category: string;
  fund_score: number;
  cagr: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  explanation: string[];
};

type ProjectionPoint = {
  month: number;
  year: number;
  invested: number;
  portfolio_value: number;
  target_amount: number;
  surplus_or_gap: number;
};

type ScenarioProjection = {
  annual_return: number;
  projection: ProjectionPoint[];
};

type ScenarioProjections = Record<
  "conservative" | "base" | "optimistic",
  ScenarioProjection
>;

type Recommendation = {
  goal_type: string;
  target_amount: number;
  horizon_years: number;
  risk_profile: string;
  allocation: Record<string, number>;
  expected_return: number;
  required_monthly_sip: number;
  sip_allocation: Record<string, number>;
  recommendations: Record<string, Fund[]>;
  projection: ProjectionPoint[];
  scenario_projections: ScenarioProjections;
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatShortCurrency(value: number) {
  if (value >= 10000000) {
    return `₹${(value / 10000000).toFixed(1)}Cr`;
  }

  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(1)}L`;
  }

  if (value >= 1000) {
    return `₹${(value / 1000).toFixed(0)}K`;
  }

  return `₹${value}`;
}

function getRiskHorizonCategory(years: string) {
  const numericYears = Number(years);

  if (!Number.isFinite(numericYears) || numericYears <= 0) {
    return "";
  }

  if (numericYears < 3) {
    return "Less than 3 years";
  }

  if (numericYears < 5) {
    return "3–5 years";
  }

  if (numericYears < 10) {
    return "5–10 years";
  }

  return "10+ years";
}

function App() {
  const [goal, setGoal] = useState("House Down Payment");
  const [target, setTarget] = useState("2500000");
  const [horizon, setHorizon] = useState("8");

  const [step, setStep] = useState<"planner" | "risk">(
    "planner"
  );

  const [age, setAge] = useState("");
  const [incomeStability, setIncomeStability] =
    useState("");

  const [lossTolerance, setLossTolerance] =
    useState("");

  const [experience, setExperience] =
    useState("");

  const [riskScore, setRiskScore] = useState<number | null>(
    null
  );

const [riskProfile, setRiskProfile] = useState<
  string | null
>(null);

  const [result, setResult] =
    useState<Recommendation | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function startRiskAssessment() {
    const horizonCategory = getRiskHorizonCategory(horizon);

    if (!horizonCategory) {
      setError("Please enter a valid investment horizon.");
      return;
    }

    setAge("");
    setIncomeStability("");
    setLossTolerance("");
    setExperience("");
    setRiskScore(null);
    setRiskProfile(null);
    setError("");
    setStep("risk");
  }

  function calculateRiskProfile() {
    let score = 0;

    const incomeScores: Record<string, number> = {
      "Very Stable": 4,
      Stable: 3,
      "Somewhat Unstable": 2,
      Unstable: 1,
    };

    const horizonScores: Record<string, number> = {
      "Less than 3 years": 1,
      "3–5 years": 2,
      "5–10 years": 3,
      "10+ years": 4,
    };

    const lossScores: Record<string, number> = {
      "Sell everything": 1,
      "Sell some": 2,
      Hold: 3,
      "Invest more": 4,
    };

    const experienceScores: Record<string, number> = {
      None: 1,
      Beginner: 2,
      Intermediate: 3,
      Experienced: 4,
    };

    const numericAge = Number(age);

    if (!numericAge || numericAge < 18) {
      throw new Error("Please enter a valid age.");
    }

    const horizonCategory = getRiskHorizonCategory(horizon);

    if (!horizonCategory) {
      throw new Error("Please enter a valid investment horizon.");
    }

    score += incomeScores[incomeStability] ?? 0;
    score += horizonScores[horizonCategory] ?? 0;
    score += lossScores[lossTolerance] ?? 0;
    score += experienceScores[experience] ?? 0;

    if (numericAge < 30) {
      score += 2;
    } else if (numericAge < 45) {
      score += 1;
    }

    let profile = "Aggressive";

    if (score <= 8) {
      profile = "Conservative";
    } else if (score <= 12) {
      profile = "Moderate";
    }

    setRiskScore(score);
    setRiskProfile(profile);

    return profile;
  }

  async function generatePlan() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/api/recommendation`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
          goal_type: goal,
          target_amount: Number(target),
          horizon_years: Number(horizon),
          risk_profile: riskProfile,
          funds_per_asset: 2,
        }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to generate recommendation."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    const finalPoint =
      result.projection[result.projection.length - 1];

    const progress = Math.min(
      100,
      (finalPoint.portfolio_value /
        result.target_amount) *
        100
    );

    return (
      <div className="app">
        <nav className="navbar">
          <div className="brand">
            <div className="brand-mark">W</div>
            <span>WealthPilot</span>
          </div>

          <button
            className="back-button"
            onClick={() => {
              setResult(null);
              setRiskScore(null);
              setRiskProfile(null);
              setError("");
            }}
          >
            ← Modify plan
          </button>
        </nav>

        <main className="results-page">
          <section className="results-hero">
            <div>
              <div className="eyebrow">
                <span className="eyebrow-dot" />
                YOUR INVESTMENT PLAN
              </div>

              <h1>
                Your path to{" "}
                <span>
                  {formatCurrency(
                    result.target_amount
                  )}
                </span>
              </h1>

              <p className="results-subtitle">
                {result.goal_type}
                <span>•</span>
                {result.horizon_years} years
                <span>•</span>
                {result.risk_profile} risk
              </p>
            </div>

            <div className="plan-status">
              <CheckCircle2 size={18} />
              Plan generated
            </div>
          </section>

          <section className="metric-grid">
            <Metric
              label="Required monthly SIP"
              value={formatCurrency(
                result.required_monthly_sip
              )}
              accent
            />

            <Metric
              label="Planning return assumption"
              value={`${(result.expected_return * 100).toFixed(1)}%`}
            />


            <Metric
              label="Equity allocation"
              value={`${result.allocation.Equity}%`}
            />

            <Metric
              label="Investment horizon"
              value={`${result.horizon_years} years`}
            />
          </section>
            <p className="return-assumption-note">
              Planning return assumptions are used to estimate the SIP required
              for your goal. Actual investment returns may be higher or lower.
            </p>

          <section className="results-grid">
            <div className="result-card allocation-card">
              <CardHeading
                title="Asset allocation"
                subtitle="Recommended portfolio structure"
              />

              <div className="allocation-list">
                {Object.entries(
                  result.allocation
                ).map(([asset, percentage]) => (
                  <div
                    className="allocation-row"
                    key={asset}
                  >
                    <div className="allocation-name">
                      <span
                        className={`allocation-dot ${asset.toLowerCase()}`}
                      />
                      {asset}
                    </div>

                    <strong>{percentage}%</strong>
                  </div>
                ))}
              </div>

              <div className="allocation-bar">
                {Object.entries(
                  result.allocation
                ).map(([asset, percentage]) => (
                  <div
                    key={asset}
                    className={`bar-segment ${asset.toLowerCase()}`}
                    style={{
                      width: `${percentage}%`,
                    }}
                  />
                ))}
              </div>
            </div>

            <div className="result-card sip-card">
              <CardHeading
                title="Monthly SIP"
                subtitle="How your monthly investment is allocated"
              />

              <div className="sip-total">
                {formatCurrency(
                  result.required_monthly_sip
                )}
              </div>

              <div className="sip-breakdown">
                {Object.entries(
                  result.sip_allocation
                ).map(([asset, amount]) => (
                  <div key={asset}>
                    <span>{asset}</span>
                    <strong>
                      {formatCurrency(amount)}
                    </strong>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="result-card projection-card">
            <CardHeading
              title="Goal projection"
              subtitle="Estimated portfolio growth over your investment horizon"
            />

            <div className="projection-summary">
              <div>
                <span>Total invested</span>
                <strong>
                  {formatCurrency(finalPoint.invested)}
                </strong>
              </div>

              <div>
                <span>Projected value</span>
                <strong className="projection-value">
                  {formatCurrency(
                    finalPoint.portfolio_value
                  )}
                </strong>
              </div>

              <div>
                <span>Target amount</span>
                <strong>
                  {formatCurrency(
                    result.target_amount
                  )}
                </strong>
              </div>
            </div>

            <div className="chart-wrapper">
              <ResponsiveContainer
                width="100%"
                height={330}
              >
                <LineChart
                  data={result.projection.filter(
                    (_, index) =>
                      index % 6 === 0 ||
                      index ===
                        result.projection.length - 1
                  )}
                  margin={{
                    top: 10,
                    right: 10,
                    left: 5,
                    bottom: 5,
                  }}
                >
                  <XAxis
                    dataKey="year"
                    tickFormatter={(value) =>
                      `${value}y`
                    }
                    stroke="#555b67"
                    tick={{
                      fill: "#777d89",
                      fontSize: 11,
                    }}
                    axisLine={false}
                    tickLine={false}
                  />

                  <YAxis
                    tickFormatter={formatShortCurrency}
                    stroke="#555b67"
                    tick={{
                      fill: "#777d89",
                      fontSize: 11,
                    }}
                    axisLine={false}
                    tickLine={false}
                    width={60}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#151820",
                      border: "1px solid #2a2e38",
                      borderRadius: "10px",
                      color: "#fff",
                    }}
                    labelFormatter={(value) =>
                      `Year ${Number(value).toFixed(1)}`
                    }
                    formatter={(
                      value,
                      name
                    ) => [
                      formatCurrency(Number(value ?? 0)),
                      name === "portfolio_value"
                        ? "Portfolio"
                        : "Invested",
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="portfolio_value"
                    stroke="#9588ff"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{
                      r: 5,
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="invested"
                    stroke="#4f5663"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-legend">
              <span>
                <i className="legend-line portfolio" />
                Projected portfolio
              </span>

              <span>
                <i className="legend-line invested" />
                Amount invested
              </span>
            </div>

            <div className="goal-progress">
              <div className="progress-header">
                <span>Progress toward goal</span>
                <strong>
                  {progress.toFixed(1)}%
                </strong>
              </div>

              <div className="progress-track">
                <div
                  style={{
                    width: `${progress}%`,
                  }}
                />
              </div>
            </div>
          </section>

          <section className="result-card scenario-card">
              <CardHeading
                title="Scenario projections"
                subtitle="How your goal could perform under different return assumptions"
              />

              <div className="scenario-grid">
                {Object.entries(
                  result.scenario_projections
                ).map(([scenario, data]) => {
                  const finalProjection =
                    data.projection[
                      data.projection.length - 1
                    ];

                  const labels: Record<
                    string,
                    string
                  > = {
                    conservative: "Conservative",
                    base: "Base case",
                    optimistic: "Optimistic",
                  };

                  return (
                    <div
                      className={`scenario-item ${scenario}`}
                      key={scenario}
                    >
                      <div className="scenario-header">
                        <span>
                          {labels[scenario]}
                        </span>

                        <strong>
                          {(data.annual_return * 100).toFixed(
                            1
                          )}
                          %
                        </strong>
                      </div>

                      <div className="scenario-value">
                        {formatCurrency(
                          finalProjection.portfolio_value
                        )}
                      </div>

                      <span className="scenario-label">
                        Projected value
                      </span>
                    </div>
                  );
                })}
              </div>

              <p className="scenario-note">
                These projections illustrate a range of
                possible outcomes using the same monthly SIP.
                Actual returns may vary and are not guaranteed.
              </p>
            </section>

          <section className="result-card funds-section">
            <CardHeading
              title="Recommended funds"
              subtitle="Selected using category-relative performance and risk-adjusted fund metrics"
              icon={<CheckCircle2 size={20} />}
            />

            <div className="scoring-methodology">
              <strong>How funds are scored</strong>

              <p>
                Funds are compared with peers in the same category
                using CAGR, Sharpe ratio, volatility, and maximum
                drawdown. Categories with fewer funds receive a
                lower-confidence adjustment to avoid overstating
                small-sample rankings.
              </p>

              <div className="scoring-weights">
                <span>CAGR 30%</span>
                <span>Sharpe 30%</span>
                <span>Volatility 20%</span>
                <span>Drawdown 20%</span>
              </div>
            </div>

            <div className="fund-groups">
              {Object.entries(
                result.recommendations
              ).map(([asset, funds]) => (
                <div
                  className="fund-group"
                  key={asset}
                >
                  <div className="fund-group-title">
                    <span
                      className={`allocation-dot ${asset.toLowerCase()}`}
                    />
                    {asset}
                  </div>

                  <div className="fund-list">
                    {funds.map((fund) => (
                      <div
                      className="fund-row fund-row-detailed"
                      key={fund.scheme_name}
                    >
                      <div className="fund-rank">
                        {funds.indexOf(fund) + 1}
                      </div>

                      <div className="fund-info">
                        <strong>{fund.scheme_name}</strong>

                        <span>
                          {fund.category} · {fund.fund_house}
                        </span>

                        <div className="fund-metrics">
                          <div>
                            <span>CAGR</span>
                            <strong>
                              {(fund.cagr * 100).toFixed(1)}%
                            </strong>
                          </div>

                          <div>
                            <span>Volatility</span>
                            <strong>
                              {(fund.volatility * 100).toFixed(1)}%
                            </strong>
                          </div>

                          <div>
                            <span>Sharpe</span>
                            <strong>
                              {fund.sharpe_ratio.toFixed(2)}
                            </strong>
                          </div>

                          <div>
                            <span>Max Drawdown</span>
                            <strong>
                              {(fund.max_drawdown * 100).toFixed(1)}%
                            </strong>
                          </div>
                        </div>

                        <div className="fund-explanation">
                          <span>Why it was selected</span>

                          <ul>
                            {fund.explanation.map((reason) => (
                              <li key={reason}>{reason}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="fund-score">
                        <strong>
                          {fund.fund_score.toFixed(1)}
                        </strong>
                        <span>Score</span>
                      </div>
                    </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>

          <div className="results-disclaimer">
            <ShieldCheck size={15} />
            <span>
              This recommendation is generated using
              rule-based portfolio allocation and
              historical fund metrics. It is for
              educational purposes and is not financial
              advice.
            </span>
          </div>
        </main>

        <footer>
          <span>WealthPilot</span>
          <span>
            Goal-based Mutual Fund Robo-Advisor
          </span>
        </footer>
      </div>
    );
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="brand">
          <div className="brand-mark">W</div>
          <span>WealthPilot</span>
        </div>

        <div className="nav-links">
          <a href="#planner">Planner</a>
          <a href="#how-it-works">
            How it works
          </a>
          <a href="#about">About</a>
        </div>
      </nav>

      <main>
        {step === "risk" ? (
          <RiskQuestionnaire
            age={age}
            setAge={setAge}
            incomeStability={incomeStability}
            setIncomeStability={setIncomeStability}
            horizon={horizon}
            lossTolerance={lossTolerance}
            setLossTolerance={setLossTolerance}
            experience={experience}
            setExperience={setExperience}
            onBack={() => setStep("planner")}
            onComplete={() => {
              try {
                calculateRiskProfile();
              } catch (err) {
                setError(
                  err instanceof Error
                    ? err.message
                    : "Please complete the risk assessment."
                );
              }
            }}
            onGenerate={generatePlan}
            riskScore={riskScore}
            riskProfile={riskProfile}
            loading={loading}
            error={error}
          />
        ) : (
          <section className="hero" id="planner">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-dot" />
              Goal-based investing
            </div>

            <h1>
              Turn your financial goals
              <span> into a plan.</span>
            </h1>

            <p>
              Build a personalized investment strategy
              based on your goal, timeline, and risk
              profile.
            </p>

            <div className="trust-row">
              <div>
                <ShieldCheck size={17} />
                Rule-based recommendations
              </div>

              <div>
                <BarChart3 size={17} />
                Data-driven analysis
              </div>
            </div>
          </div>

          <div className="planner-card">
            <div className="card-header">
              <div>
                <h2>Build your plan</h2>
                <p>
                  Tell us what you're investing for.
                </p>
              </div>

              <Target size={22} />
            </div>

            <div className="form-grid">
              <label>
                <span>Financial goal</span>

                <select
                  value={goal}
                  onChange={(e) =>
                    setGoal(e.target.value)
                  }
                >
                  <option>
                    House Down Payment
                  </option>
                  <option>Retirement</option>
                  <option>Education</option>
                  <option>Wealth Creation</option>
                  <option>Emergency Fund</option>
                </select>
              </label>

              <label>
                <span>Target amount</span>

                <div className="input-prefix">
                  <b>₹</b>

                  <input
                    type="number"
                    value={target}
                    onChange={(e) =>
                      setTarget(e.target.value)
                    }
                  />
                </div>
              </label>

              <label>
                <span>Investment horizon</span>

                <div className="input-suffix">
                  <input
                    type="number"
                    min="1"
                    value={horizon}
                    onChange={(e) =>
                      setHorizon(e.target.value)
                    }
                  />

                  <b>years</b>
                </div>
              </label>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
            className="primary-button"
            onClick={startRiskAssessment}
          >
            Continue to risk assessment
            <ArrowRight size={18} />
          </button>

            <p className="disclaimer">
              For educational and informational
              purposes only.
            </p>
          </div>
        </section>
        )}
        <section
          className="features"
          id="how-it-works"
        >
          <div className="section-heading">
            <span>HOW IT WORKS</span>
            <h2>
              A plan built around your goal.
            </h2>
          </div>

          <div className="feature-grid">
            <Feature
              icon={<Target />}
              number="01"
              title="Define your goal"
              text="Set a target amount and decide when you need the money."
            />

            <Feature
              icon={<TrendingUp />}
              number="02"
              title="Understand your risk"
              text="Your risk profile and investment horizon determine the strategy."
            />

            <Feature
              icon={<BarChart3 />}
              number="03"
              title="Get your plan"
              text="Receive an allocation, SIP amount, fund selection, and projection."
            />
          </div>
        </section>
      </main>

      <footer>
        <span>WealthPilot</span>
        <span>
          Goal-based Mutual Fund Robo-Advisor
        </span>
      </footer>
    </div>
  );
}

function RiskQuestionnaire({
  age,
  setAge,
  incomeStability,
  setIncomeStability,
  horizon,
  lossTolerance,
  setLossTolerance,
  experience,
  setExperience,
  onBack,
  onComplete,
  onGenerate,
  riskScore,
  riskProfile,
  loading,
  error,
}: {
  age: string;
  setAge: (value: string) => void;
  incomeStability: string;
  setIncomeStability: (value: string) => void;
  horizon: string;
  lossTolerance: string;
  setLossTolerance: (value: string) => void;
  experience: string;
  setExperience: (value: string) => void;
  onBack: () => void;
  onComplete: () => void;
  onGenerate: () => void;
  riskScore: number | null;
  riskProfile: string | null;
  loading: boolean;
  error: string;
}) {
  if (riskProfile && riskScore !== null) {
    return (
      <section className="risk-page">
        <div className="risk-card risk-result">
          <div className="eyebrow">
            <span className="eyebrow-dot" />
            RISK ASSESSMENT COMPLETE
          </div>

          <h1>
            Your risk profile is{" "}
            <span>{riskProfile}</span>
          </h1>

          <p className="risk-result-description">
            Your answers produced a risk score of{" "}
            <strong>{riskScore}</strong>. This profile
            will be used to determine your portfolio
            allocation and fund recommendations.
          </p>

          <div className="risk-score">
            <span>Risk score</span>
            <strong>{riskScore}/18</strong>
          </div>

          <div className="risk-profile-box">
            <div>
              <span>Profile</span>
              <strong>{riskProfile}</strong>
            </div>

            <div>
              <span>Strategy</span>

              <strong>
                {riskProfile === "Conservative"
                  ? "Capital preservation"
                  : riskProfile === "Moderate"
                    ? "Balanced growth"
                    : "Long-term growth"}
              </strong>
            </div>
          </div>

          <div className="risk-actions">
            <button
              className="secondary-button"
              onClick={onBack}
            >
              ← Review plan
            </button>

            <button
              className="primary-button"
              onClick={onGenerate}
              disabled={loading}
            >
              {loading
                ? "Building your plan..."
                : "Generate investment plan"}

              {!loading && (
                <ArrowRight size={18} />
              )}
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="risk-page">
      <div className="risk-card">
        <div className="risk-header">
          <div>
            <div className="eyebrow">
              <span className="eyebrow-dot" />
              STEP 2 OF 2
            </div>

            <h1>Understand your risk.</h1>

            <p>
              A few questions help us build a portfolio
              that matches your ability and willingness
              to take risk.
            </p>
          </div>

          <div className="risk-progress">
            4 questions
          </div>
        </div>

        <div className="risk-question">
          <label>
            <span>01 · AGE</span>

            <h2>How old are you?</h2>

            <p>
              Age helps us understand your investment
              capacity and time horizon.
            </p>

            <input
              className="risk-age-input"
              type="number"
              min="18"
              max="100"
              placeholder="Enter your age"
              value={age}
              onChange={(e) =>
                setAge(e.target.value)
              }
            />
          </label>
        </div>

        <div className="risk-question">
          <label>
            <span>02 · INCOME STABILITY</span>

            <h2>
              How stable is your income?
            </h2>
          </label>

          <Option
            selected={incomeStability}
            value="Very Stable"
            onClick={() =>
              setIncomeStability("Very Stable")
            }
            description="Highly predictable income with strong financial stability."
          />

          <Option
            selected={incomeStability}
            value="Stable"
            onClick={() =>
              setIncomeStability("Stable")
            }
            description="Generally reliable income with limited uncertainty."
          />

          <Option
            selected={incomeStability}
            value="Somewhat Unstable"
            onClick={() =>
              setIncomeStability(
                "Somewhat Unstable"
              )
            }
            description="Income can fluctuate from time to time."
          />

          <Option
            selected={incomeStability}
            value="Unstable"
            onClick={() =>
              setIncomeStability("Unstable")
            }
            description="Income is unpredictable or varies significantly."
          />
        </div>

        <div className="risk-question">
          <label>
            <span>YOUR INVESTMENT HORIZON</span>

            <h2>Your investment horizon</h2>

            <p>
              Based on the goal you entered, you plan to invest for {horizon} {Number(horizon) === 1 ? "year" : "years"}. We use this automatically in your risk assessment.
            </p>
          </label>

          <div className="risk-profile-box">
            <div>
              <span>Goal horizon</span>
              <strong>
                {horizon} {Number(horizon) === 1 ? "year" : "years"}
              </strong>
            </div>

            <div>
              <span>Risk category</span>
              <strong>{getRiskHorizonCategory(horizon)}</strong>
            </div>
          </div>
        </div>

        <div className="risk-question">
          <label>
            <span>03 · LOSS TOLERANCE</span>

            <h2>
              What would you do if your portfolio
              fell 20%?
            </h2>
          </label>

          <Option
            selected={lossTolerance}
            value="Sell everything"
            onClick={() =>
              setLossTolerance("Sell everything")
            }
          />

          <Option
            selected={lossTolerance}
            value="Sell some"
            onClick={() =>
              setLossTolerance("Sell some")
            }
          />

          <Option
            selected={lossTolerance}
            value="Hold"
            onClick={() =>
              setLossTolerance("Hold")
            }
          />

          <Option
            selected={lossTolerance}
            value="Invest more"
            onClick={() =>
              setLossTolerance("Invest more")
            }
          />
        </div>

        <div className="risk-question">
          <label>
            <span>04 · EXPERIENCE</span>

            <h2>
              How experienced are you with investing?
            </h2>
          </label>

          {[
            "None",
            "Beginner",
            "Intermediate",
            "Experienced",
          ].map((option) => (
            <Option
              key={option}
              selected={experience}
              value={option}
              onClick={() =>
                setExperience(option)
              }
            />
          ))}
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="risk-actions">
          <button
            className="secondary-button"
            onClick={onBack}
          >
            ← Back
          </button>

          <button
            className="primary-button"
            onClick={onComplete}
          >
            Calculate my risk profile
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </section>
  );
}

function Metric({
  label,
  value,
  accent = false,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div
      className={`metric-card ${
        accent ? "metric-accent" : ""
      }`}
    >
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function CardHeading({
  title,
  subtitle,
  icon,
}: {
  title: string;
  subtitle: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="result-card-heading">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>

      {icon}
    </div>
  );
}

function Feature({
  icon,
  number,
  title,
  text,
}: {
  icon: React.ReactNode;
  number: string;
  title: string;
  text: string;
}) {
  return (
    <div className="feature-card">
      <div className="feature-top">
        <div className="feature-icon">
          {icon}
        </div>

        <span>{number}</span>
      </div>

      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  );
}

function Option({
  selected,
  value,
  description,
  onClick,
}: {
  selected: string;
  value: string;
  description?: string;
  onClick: () => void;
}) {
  const active = selected === value;

  return (
    <button
      type="button"
      className={`risk-option ${
        active ? "selected" : ""
      }`}
      onClick={onClick}
    >
      <div className="risk-option-radio">
        {active && <span />}
      </div>

      <div>
        <strong>{value}</strong>

        {description && (
          <p>{description}</p>
        )}
      </div>
    </button>
  );
}

export default App;