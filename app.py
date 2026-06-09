from flask import Flask, request, jsonify, render_template_string
import pickle
import pandas as pd

app = Flask(__name__)

# Load model
with open("insomnia_model.pkl", 'rb') as f:
    model = pickle.load(f)

HTML ='''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>AI-Based Insomnia Risk Analyzer</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --card: #1a1a26;
    --border: #2a2a3d;
    --accent: #7c6af7;
    --accent2: #f76a8c;
    --green: #4ade80;
    --yellow: #fbbf24;
    --red: #f87171;
    --text: #e8e8f0;
    --muted: #6b6b8a;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 20% 20%, rgba(124,106,247,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(247,106,140,0.06) 0%, transparent 50%);
    animation: bgShift 10s ease-in-out infinite alternate;
    z-index: 0;
    pointer-events: none;
  }
  @keyframes bgShift {
    0% { transform: translate(0,0); }
    100% { transform: translate(2%, 2%); }
  }
  .container {
    max-width: 780px;
    margin: 0 auto;
    padding: 48px 24px;
    position: relative;
    z-index: 1;
  }
  header { text-align: center; margin-bottom: 48px; }
  .badge {
    display: inline-block;
    background: rgba(124,106,247,0.15);
    border: 1px solid rgba(124,106,247,0.3);
    color: var(--accent);
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 100px;
    margin-bottom: 20px;
  }
  h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(28px, 5vw, 44px);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #e8e8f0 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .subtitle {
    color: var(--muted);
    font-size: 15px;
    font-weight: 300;
    line-height: 1.6;
  }
  .form-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px;
    margin-bottom: 24px;
  }
  .section-title {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media(max-width: 560px) { .grid { grid-template-columns: 1fr; } }
  .field { display: flex; flex-direction: column; gap: 8px; }
  label {
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    letter-spacing: 0.02em;
  }
  .input-wrap { position: relative; }
  input[type=range] {
    -webkit-appearance: none;
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 4px;
    outline: none;
    margin: 8px 0 4px;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 0 0 4px rgba(124,106,247,0.2);
    transition: box-shadow 0.2s;
  }
  input[type=range]:hover::-webkit-slider-thumb {
    box-shadow: 0 0 0 6px rgba(124,106,247,0.3);
  }
  input[type=range]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
    border: none;
    box-shadow: 0 0 0 4px rgba(124,106,247,0.2);
  }
  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: var(--muted);
  }
  .val-badge {
    display: inline-block;
    background: rgba(124,106,247,0.15);
    color: var(--accent);
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 13px;
    padding: 2px 10px;
    border-radius: 6px;
    min-width: 36px;
    text-align: center;
  }
  .toggle-group {
    display: flex;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
  }
  .toggle-group input { display: none; }
  .toggle-group label {
    flex: 1;
    text-align: center;
    padding: 10px;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.2s;
    margin: 0;
  }
  .toggle-group input:checked + label {
    background: var(--accent);
    color: white;
  }
  .submit-btn {
    width: 100%;
    padding: 16px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border: none;
    border-radius: 12px;
    color: white;
    font-family: 'Syne', sans-serif;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.3s;
    margin-top: 8px;
    position: relative;
    overflow: hidden;
  }
  .submit-btn::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s;
  }
  .submit-btn:hover::before { left: 100%; }
  .submit-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(124,106,247,0.4); }
  .submit-btn:active { transform: translateY(0); }
  .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
  #result {
    display: none;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px;
    text-align: center;
    animation: slideUp 0.5s cubic-bezier(0.34,1.56,0.64,1);
  }
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(30px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .risk-icon { font-size: 56px; margin-bottom: 16px; display: block; }
  .risk-label {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    margin-bottom: 8px;
  }
  .risk-desc {
    color: var(--muted);
    font-size: 14px;
    margin-bottom: 28px;
    line-height: 1.6;
  }
  .prob-bars { display: flex; flex-direction: column; gap: 12px; text-align: left; }
  .prob-row { display: flex; flex-direction: column; gap: 6px; }
  .prob-top { display: flex; justify-content: space-between; font-size: 13px; }
  .prob-track {
    height: 6px;
    background: var(--border);
    border-radius: 6px;
    overflow: hidden;
  }
  .prob-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 1s cubic-bezier(0.34,1.56,0.64,1);
    width: 0;
  }
  .low-fill  { background: var(--green); }
  .mid-fill  { background: var(--yellow); }
  .high-fill { background: var(--red); }
  .advice {
    margin-top: 28px;
    background: var(--surface);
    border-radius: 12px;
    padding: 20px;
    text-align: left;
  }
  .advice-title {
    font-family: 'Syne', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 12px;
  }
  .advice ul { list-style: none; display: flex; flex-direction: column; gap: 8px; }
  .advice li { font-size: 13px; color: var(--muted); display: flex; gap: 8px; align-items: flex-start; }
  .advice li::before { content: '→'; color: var(--accent); flex-shrink: 0; }
  .reset-btn {
    margin-top: 20px;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 10px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }
  .reset-btn:hover { border-color: var(--accent); color: var(--accent); }
  .stress-field-custom { grid-column: 1 / -1; }
  .stress-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    margin-top: 12px;
  }
  .stress-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 14px;
    padding: 16px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  .stress-card:hover {
    border-color: var(--accent);
    background: rgba(124, 106, 247, 0.08);
    transform: translateY(-3px);
  }
  .stress-card.active {
    border-color: var(--accent);
    background: rgba(124, 106, 247, 0.15);
    box-shadow: 0 0 0 2px rgba(124, 106, 247, 0.2);
  }
  .stress-emoji { font-size: 32px; line-height: 1; }
  .stress-text {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.3;
    font-weight: 500;
  }
  .stress-card.active .stress-text { color: var(--accent); }

  .job-field-custom { grid-column: 1 / -1; }
  .job-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    margin-top: 12px;
  }
  .job-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 14px;
    padding: 14px 10px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
  }
  .job-card:hover {
    border-color: var(--accent2);
    background: rgba(247, 106, 140, 0.08);
    transform: translateY(-3px);
  }
  .job-card.active {
    border-color: var(--accent2);
    background: rgba(247, 106, 140, 0.15);
    box-shadow: 0 0 0 2px rgba(247, 106, 140, 0.2);
  }
  .job-emoji { font-size: 26px; line-height: 1; }
  .job-text { font-size: 12px; color: var(--text); line-height: 1.3; font-weight: 600; }
  .job-card.active .job-text { color: var(--accent2); }
  .job-desc { font-size: 10px; color: var(--muted); line-height: 1.4; font-weight: 400; font-style: italic; }
  .job-card.active .job-desc { color: rgba(247,106,140,0.7); }
  .job-activity-tag {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 6px;
    background: rgba(247, 106, 140, 0.12);
    color: var(--accent2);
    opacity: 0;
    transition: opacity 0.2s;
  }
  .job-card.active .job-activity-tag { opacity: 1; }
  .activity-hint {
    margin-top: 10px;
    font-size: 12px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border);
  }
  .activity-hint span { color: var(--accent2); font-weight: 600; }

  footer { text-align: center; margin-top: 40px; padding: 20px 0; }
  footer p { color: var(--muted); font-size: 13px; font-family: 'Syne', sans-serif; letter-spacing: 0.08em; }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="badge">AI-Powered Assessment</div>
    <h1>Insomnia Risk<br/>Analyzer</h1>
    <p class="subtitle">Answer a few questions about your lifestyle<br/>and our AI will assess your insomnia risk.</p>
  </header>

  <div class="form-card">
    <div class="section-title">Sleep & Body</div>
    <div class="grid">
      <div class="field">
        <label>Age: <span class="val-badge" id="age-val">25</span></label>
        <div class="input-wrap">
          <input type="range" id="age" min="18" max="65" value="25"
                 oninput="document.getElementById('age-val').textContent=this.value"/>
          <div class="range-labels"><span>18</span><span>65</span></div>
        </div>
      </div>
      <div class="field">
        <label>Sleep Hours/Night: <span class="val-badge" id="sleep-val">7</span></label>
        <div class="input-wrap">
          <input type="range" id="sleep_hours" min="1" max="10" step="0.5" value="7"
                 oninput="document.getElementById('sleep-val').textContent=this.value"/>
          <div class="range-labels"><span>1h</span><span>10h</span></div>
        </div>
      </div>
      <div class="field stress-field-custom">
        <label>How\'s Your Stress Level?</label>
        <input type="hidden" id="stress_level" value="5"/>
        <div class="stress-cards">
          <div class="stress-card" onclick="selectStressCard(this, 2)">
            <div class="stress-emoji">😌</div>
            <div class="stress-text">Calm &<br/>Relaxed</div>
          </div>
          <div class="stress-card" onclick="selectStressCard(this, 4)">
            <div class="stress-emoji">🙂</div>
            <div class="stress-text">Occasional<br/>Stress</div>
          </div>
          <div class="stress-card active" onclick="selectStressCard(this, 6)">
            <div class="stress-emoji">😐</div>
            <div class="stress-text">Moderate<br/>Stress</div>
          </div>
          <div class="stress-card" onclick="selectStressCard(this, 8)">
            <div class="stress-emoji">😟</div>
            <div class="stress-text">Frequently<br/>Stressed</div>
          </div>
          <div class="stress-card" onclick="selectStressCard(this, 10)">
            <div class="stress-emoji">😰</div>
            <div class="stress-text">Constantly<br/>Overwhelmed</div>
          </div>
        </div>
      </div>
      <div class="field">
        <label>Exercise Days/Week: <span class="val-badge" id="ex-val">3</span></label>
        <div class="input-wrap">
          <input type="range" id="exercise_days" min="0" max="7" value="3"
                 oninput="document.getElementById('ex-val').textContent=this.value"/>
          <div class="range-labels"><span>0</span><span>7</span></div>
        </div>
      </div>

      <!-- Job / Daily Activity Type -->
      <div class="field job-field-custom">
        <label>Job / Daily Activity Type
          <span style="font-size:11px; color:var(--muted); font-weight:400; margin-left:6px;">
            — counts toward your overall activity score
          </span>
        </label>
        <input type="hidden" id="job_activity_score" value="1"/>
        <div class="job-cards">
          <div class="job-card active" onclick="selectJobCard(this, 1)">
            <div class="job-emoji">🖥️</div>
            <div class="job-text">Desk / Office</div>
            <div class="job-desc">sitting most of the day</div>
            <div class="job-activity-tag">Low</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 1)">
            <div class="job-emoji">🏠</div>
            <div class="job-text">Work from Home</div>
            <div class="job-desc">seated, minimal movement</div>
            <div class="job-activity-tag">Low</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 2)">
            <div class="job-emoji">🚗</div>
            <div class="job-text">Driving / Transport</div>
            <div class="job-desc">seated, short walks</div>
            <div class="job-activity-tag">Light</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 2)">
            <div class="job-emoji">📚</div>
            <div class="job-text">Student</div>
            <div class="job-desc">mostly sitting, campus walks</div>
            <div class="job-activity-tag">Light</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 3)">
            <div class="job-emoji">👟</div>
            <div class="job-text">On Your Feet</div>
            <div class="job-desc">standing & walking all day</div>
            <div class="job-activity-tag">Moderate</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 3)">
            <div class="job-emoji">🧹</div>
            <div class="job-text">Homemaker</div>
            <div class="job-desc">light chores & childcare</div>
            <div class="job-activity-tag">Moderate</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 4)">
            <div class="job-emoji">🔨</div>
            <div class="job-text">Daily Labour</div>
            <div class="job-desc">heavy physical work all day</div>
            <div class="job-activity-tag">Heavy</div>
          </div>
          <div class="job-card" onclick="selectJobCard(this, 1)">
            <div class="job-emoji">🛋️</div>
            <div class="job-text">Not Working</div>
            <div class="job-desc">mostly inactive at home</div>
            <div class="job-activity-tag">Sedentary</div>
          </div>
        </div>
        <div class="activity-hint" id="activity-hint">
          💡 Effective activity score: exercise days <span id="ex-days-hint">3</span> + job bonus
          <span id="job-bonus-hint">+0</span> =
          <span id="effective-score-hint">3</span> / 7
        </div>
      </div>
    </div>

    <div class="section-title" style="margin-top:28px">Habits</div>
    <div class="grid">
      <div class="field">
        <label>Screen Time Before Bed: <span class="val-badge" id="screen-val">2</span>h</label>
        <input type="range" id="screen_time" min="0" max="13" step="0.5" value="2"
               oninput="document.getElementById('screen-val').textContent=this.value"/>
        <div class="range-labels"><span>0h</span><span>13h</span></div>
      </div>
      <div class="field">
        <label>Caffeine Cups/Day: <span class="val-badge" id="caff-val">2</span></label>
        <input type="range" id="caffeine_cups" min="0" max="8" value="2"
               oninput="document.getElementById('caff-val').textContent=this.value"/>
        <div class="range-labels"><span>0</span><span>8</span></div>
      </div>
      <div class="field">
        <label>Nap During Day?</label>
        <div class="toggle-group">
          <input type="radio" name="nap" id="nap0" value="0" checked/>
          <label for="nap0">No</label>
          <input type="radio" name="nap" id="nap1" value="1"/>
          <label for="nap1">Yes</label>
        </div>
      </div>
      <div class="field">
        <label>Irregular Sleep Schedule?</label>
        <div class="toggle-group">
          <input type="radio" name="irreg" id="irreg0" value="0" checked/>
          <label for="irreg0">No</label>
          <input type="radio" name="irreg" id="irreg1" value="1"/>
          <label for="irreg1">Yes</label>
        </div>
      </div>
    </div>

    <button class="submit-btn" onclick="predict()">Analyze My Sleep Risk →</button>
  </div>

  <div id="result"></div>

  <footer>
    <p>Developed with <span style="color:#7c6af7; font-weight:500;"> love❤️</span></p>
  </footer>

</div>

<script>
const advice = {
  0: ["Maintain your current sleep schedule","💧 Stay hydrated throughout the day","🏃 Continue regular physical activity and exercise","Continue limiting screen time before bed"],
  1: ["Try to get 7-8 hours of sleep consistently","Reduce screen time 1 hour before bed","Cut caffeine intake after noon","Add light exercise 3-4 days a week","Practice relaxation techniques before sleep"],
  2: ["Consult a sleep specialist immediately","Set a strict consistent sleep/wake schedule","Avoid all caffeine after 12pm","No screens at least 2 hours before bed","Try meditation or deep breathing exercises","Consider cognitive behavioral therapy for insomnia"]
};

// keep track of current job bonus for the hint
let currentJobBonus = 0;

function updateActivityHint() {
  const ex = +document.getElementById('exercise_days').value;
  const effective = Math.min(7, ex + currentJobBonus);
  document.getElementById('ex-days-hint').textContent = ex;
  document.getElementById('job-bonus-hint').textContent = '+' + currentJobBonus;
  document.getElementById('effective-score-hint').textContent = effective;
}

// wire exercise slider to also refresh the hint
document.getElementById('exercise_days').addEventListener('input', updateActivityHint);

function selectStressCard(element, value) {
  document.querySelectorAll('.stress-card').forEach(card => card.classList.remove('active'));
  element.classList.add('active');
  document.getElementById('stress_level').value = value;
}

function selectJobCard(element, score) {
  document.querySelectorAll('.job-card').forEach(card => card.classList.remove('active'));
  element.classList.add('active');
  document.getElementById('job_activity_score').value = score;
  // bonus = score - 1  (sedentary=0, light=1, moderate=2, heavy=3)
  currentJobBonus = score - 1;
  updateActivityHint();
}

async function predict() {
  const btn = document.querySelector('.submit-btn');
  btn.textContent = 'Analyzing...';
  btn.disabled = true;

  const data = {
    age: +document.getElementById('age').value,
    sleep_hours: +document.getElementById('sleep_hours').value,
    screen_time: +document.getElementById('screen_time').value,
    caffeine_cups: +document.getElementById('caffeine_cups').value,
    exercise_days: +document.getElementById('exercise_days').value,
    stress_level: +document.getElementById('stress_level').value,
    nap_during_day: +document.querySelector('input[name=nap]:checked').value,
    irregular_schedule: +document.querySelector('input[name=irreg]:checked').value,
    job_activity_score: +document.getElementById('job_activity_score').value
  };

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    showResult({ risk: result.risk, probabilities: result.probabilities });
  } catch (error) {
    console.error(error);
    alert('Prediction failed');
  }

  btn.textContent = 'Analyze My Sleep Risk →';
  btn.disabled = false;
}

function showResult(data) {
  const icons  = {0:'😴', 1:'😟', 2:'🚨'};
  const labels = {0:'Low Risk', 1:'Medium Risk', 2:'High Risk'};
  const colors = {0:'#4ade80', 1:'#fbbf24', 2:'#f87171'};
  const descs  = {
    0: 'Your lifestyle habits support healthy sleep. Keep it up!',
    1: 'Some habits may be affecting your sleep quality. Small changes can help.',
    2: 'Your lifestyle patterns strongly suggest insomnia risk. Please seek help.'
  };

  const r  = data.risk;
  const el = document.getElementById('result');
  el.style.display = 'block';
  el.innerHTML = `
    <span class="risk-icon">${icons[r]}</span>
    <div class="risk-label" style="color:${colors[r]}">${labels[r]}</div>
    <div class="risk-desc">${descs[r]}</div>
    <div class="prob-bars">
      <div class="prob-row">
        <div class="prob-top"><span style="color:#4ade80">🟢 Low Risk</span><span>${data.probabilities[0]}%</span></div>
        <div class="prob-track"><div class="prob-fill low-fill" id="low-bar"></div></div>
      </div>
      <div class="prob-row">
        <div class="prob-top"><span style="color:#fbbf24">🟡 Medium Risk</span><span>${data.probabilities[1]}%</span></div>
        <div class="prob-track"><div class="prob-fill mid-fill" id="mid-bar"></div></div>
      </div>
      <div class="prob-row">
        <div class="prob-top"><span style="color:#f87171">🔴 High Risk</span><span>${data.probabilities[2]}%</span></div>
        <div class="prob-track"><div class="prob-fill high-fill" id="high-bar"></div></div>
      </div>
    </div>
    <div class="advice">
      <div class="advice-title">Recommendations</div>
      <ul>${advice[r].map(a => `<li>${a}</li>`).join('')}</ul>
    </div>
    <button class="reset-btn" onclick="document.getElementById('result').style.display='none'">Reassess ↺</button>
  `;
  el.scrollIntoView({behavior:'smooth'});
  setTimeout(() => {
    document.getElementById('low-bar').style.width  = data.probabilities[0] + '%';
    document.getElementById('mid-bar').style.width  = data.probabilities[1] + '%';
    document.getElementById('high-bar').style.width = data.probabilities[2] + '%';
  }, 100);
}
</script>
</body>
</html>'''

@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def predict():
    d = request.json

    # ── Blend job activity with exercise days ──────────────────────────────
    # job_activity_score:  1=sedentary  2=light  3=moderate  4=heavy
    # job_bonus:           0            1         2            3  extra days
    # effective_exercise_days = exercise_days + job_bonus  (capped at 7)
    # This keeps full model-compatibility (same feature name, same range).
    # When you retrain, you can pass job_activity_score as its own feature.
    job_score  = int(d.pop('job_activity_score', 1))
    job_bonus  = job_score - 1                        # 0 / 1 / 2 / 3
    d['exercise_days'] = min(7, d['exercise_days'] + job_bonus)
    # ───────────────────────────────────────────────────────────────────────

    df   = pd.DataFrame([d])
    risk = int(model.predict(df)[0])
    probs = model.predict_proba(df)[0]
    return jsonify({
        'risk': risk,
        'probabilities': [round(p * 100, 1) for p in probs]
    })

# Works everywhere
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=5000)
