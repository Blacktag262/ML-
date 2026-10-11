const form = document.getElementById("risk-form");
const submitBtn = document.getElementById("submit-btn");
const emptyState = document.getElementById("result-empty");
const resultContent = document.getElementById("result-content");
const errorMessage = document.getElementById("error-message");
const resultStatus = document.getElementById("result-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorMessage.classList.add("hidden");
  resultContent.classList.add("hidden");
  emptyState.classList.remove("hidden");
  resultStatus.textContent = "ANALYZING";
  submitBtn.disabled = true;
  submitBtn.querySelector("span:first-child").textContent = "Analyzing profile…";

  const raw = Object.fromEntries(new FormData(form).entries());
  const billAverage = Number(raw.AVG_BILL_INPUT || 0);
  const payAverage = Number(raw.AVG_PAY_INPUT || 0);
  const payload = {
    LIMIT_BAL: Number(raw.LIMIT_BAL), AGE: Number(raw.AGE),
    SEX: Number(raw.SEX), EDUCATION: Number(raw.EDUCATION), MARRIAGE: Number(raw.MARRIAGE),
    PAY_0: Number(raw.PAY_0), PAY_2: Number(raw.PAY_2), PAY_3: Number(raw.PAY_3),
    PAY_4: Number(raw.PAY_4), PAY_5: Number(raw.PAY_5), PAY_6: Number(raw.PAY_6)
  };
  // Form provides average statement values; expand them into six monthly values for the model.
  for (let i = 1; i <= 6; i++) {
    payload[`BILL_AMT${i}`] = billAverage;
    payload[`PAY_AMT${i}`] = payAverage;
  }

  try {
    const response = await fetch("/predict", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to generate an assessment.");

    emptyState.classList.add("hidden");
    resultContent.classList.remove("hidden");
    resultStatus.textContent = "ASSESSMENT COMPLETE";
    document.getElementById("risk-score").textContent = result.risk_score.toFixed(1);
    document.getElementById("risk-level").textContent = `${result.risk_level.toUpperCase()} RISK`;
    document.getElementById("prediction-message").textContent = result.message;
    document.getElementById("risk-meter-fill").style.width = `${Math.max(0, Math.min(100, result.risk_score))}%`;
  } catch (error) {
    emptyState.classList.add("hidden");
    errorMessage.textContent = error.message;
    errorMessage.classList.remove("hidden");
    resultStatus.textContent = "NEEDS ATTENTION";
  } finally {
    submitBtn.disabled = false;
    submitBtn.querySelector("span:first-child").textContent = "Generate assessment";
  }
});
