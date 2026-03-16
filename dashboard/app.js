import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import {
  getDatabase,
  ref,
  onChildAdded,
  query,
  limitToLast
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyBjAIUwhdPBTN-Ho7BwQh3Z6xCKvS6F-Nw",
  authDomain: "vital-sensor-fusion.firebaseapp.com",
  databaseURL: "https://vital-sensor-fusion-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "vital-sensor-fusion",
  storageBucket: "vital-sensor-fusion.firebasestorage.app",
  messagingSenderId: "1041043318317",
  appId: "1:1041043318317:web:a5792e221dbef350ed7aa4",
  measurementId: "G-XX6MT38MWM"
};

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

const spo2El = document.getElementById("spo2Value");
const prEl = document.getElementById("prValue");
const motionEl = document.getElementById("motionValue");
const reliabilityEl = document.getElementById("reliabilityValue");
const ppgBpmEl = document.getElementById("ppgBpmValue");
const statusEl = document.getElementById("statusValue");
const statusTextEl = document.getElementById("statusText");

const chartTextColor = "#334155";
const chartGridColor = "rgba(51, 65, 85, 0.10)";
const MAX_POINTS = 50;

const labels = [];
const ppgData = [];
const spo2Data = [];
const prData = [];
const motionData = [];
const reliabilityData = [];

// Risk hafızası
let riskHoldCounter = 0;
const WARNING_HOLD_SAMPLES = 5;
const SUPPRESS_HOLD_SAMPLES = 8;

function makeChart(ctx, label, color) {
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label,
        data: [],
        borderColor: color,
        backgroundColor: color,
        borderWidth: 3,
        tension: 0.30,
        pointRadius: 0,
        fill: false
      }]
    },
    options: {
      responsive: true,
      animation: false,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: chartTextColor,
            usePointStyle: true,
            pointStyle: "line"
          }
        }
      },
      scales: {
        x: {
          ticks: { color: chartTextColor },
          grid: { color: chartGridColor }
        },
        y: {
          ticks: { color: chartTextColor },
          grid: { color: chartGridColor }
        }
      }
    }
  });
}

const ppgChart = makeChart(document.getElementById("ppgChart"), "Raw PPG", "#4f83ff");
const reliabilityChart = makeChart(document.getElementById("reliabilityChart"), "Reliability", "#30b46c");
const spo2Chart = makeChart(document.getElementById("spo2Chart"), "SpO₂", "#7acb78");
const prChart = makeChart(document.getElementById("prChart"), "Pulse Rate", "#6aa0f8");
const motionChart = makeChart(document.getElementById("motionChart"), "Motion", "#c88433");

function pushLimited(arr, value) {
  arr.push(value);
  if (arr.length > MAX_POINTS) arr.shift();
}

function movingAverage(arr, windowSize = 5) {
  const out = [];
  for (let i = 0; i < arr.length; i++) {
    const start = Math.max(0, i - windowSize + 1);
    const slice = arr.slice(start, i + 1);
    const mean = slice.reduce((a, b) => a + b, 0) / slice.length;
    out.push(mean);
  }
  return out;
}

function detectPeaks(signal, minDistance = 3) {
  const peaks = [];
  let lastPeak = -minDistance;

  for (let i = 1; i < signal.length - 1; i++) {
    const isPeak = signal[i] > signal[i - 1] && signal[i] > signal[i + 1];
    if (isPeak && i - lastPeak >= minDistance) {
      peaks.push(i);
      lastPeak = i;
    }
  }
  return peaks;
}

function estimateBpmFromPpg(signal, sampleRateApprox = 5) {
  if (signal.length < 8) return null;

  const minVal = Math.min(...signal);
  const centered = signal.map(v => v - minVal);

  const peaks = detectPeaks(centered, 3);
  if (peaks.length < 2) return null;

  const intervals = [];
  for (let i = 1; i < peaks.length; i++) {
    intervals.push((peaks[i] - peaks[i - 1]) / sampleRateApprox);
  }

  const meanInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
  if (!meanInterval || meanInterval <= 0) return null;

  return 60 / meanInterval;
}

function applyDecisionHold(rawDecision) {
  if (rawDecision === "SUPPRESS") {
    riskHoldCounter = SUPPRESS_HOLD_SAMPLES;
    return {
      decision: "SUPPRESS",
      desc: "Signal confidence is too low. Measurement should be hidden."
    };
  }

  if (rawDecision === "WARNING") {
    riskHoldCounter = Math.max(riskHoldCounter, WARNING_HOLD_SAMPLES);
    return {
      decision: "WARNING",
      desc: "Measurement is available but low-confidence warning is active."
    };
  }

  // Eğer sistem tekrar DISPLAY dese bile, yakın geçmişte risk varsa
  // hemen yeşile dönmeyelim
  if (riskHoldCounter > 0) {
    riskHoldCounter -= 1;
    return {
      decision: "WARNING",
      desc: "Recent risk event detected. Waiting for stable recovery."
    };
  }

  return {
    decision: "DISPLAY",
    desc: "Signal quality is reliable. Measurement can be displayed."
  };
}

function refreshCharts() {
  const smoothPpg = movingAverage(ppgData, 3);
  const smoothReliability = movingAverage(reliabilityData, 5);

  ppgChart.data.labels = [...labels];
  ppgChart.data.datasets[0].data = [...smoothPpg];
  ppgChart.update();

  reliabilityChart.data.labels = [...labels];
  reliabilityChart.data.datasets[0].data = [...smoothReliability];
  reliabilityChart.update();

  spo2Chart.data.labels = [...labels];
  spo2Chart.data.datasets[0].data = [...spo2Data];
  spo2Chart.update();

  prChart.data.labels = [...labels];
  prChart.data.datasets[0].data = [...prData];
  prChart.update();

  motionChart.data.labels = [...labels];
  motionChart.data.datasets[0].data = [...motionData];
  motionChart.update();
}

function updateDashboard(sample, indexLabel) {
  const spo2 = Number(sample.spo2 ?? 0);
  const pr = Number(sample.pulse_rate ?? 0);
  const ppg = Number(sample.ppg_raw ?? 0);
  const motion = Number(sample.motion ?? 0);
  const reliability = Number(sample.reliability ?? 0);
  const rawDecision = sample.decision ?? "WARNING";

  const heldDecision = applyDecisionHold(rawDecision);

  spo2El.textContent = `${spo2} %`;
  prEl.textContent = `${pr} BPM`;
  motionEl.textContent = `${Math.round(motion)}`;
  reliabilityEl.textContent = reliability.toFixed(2);

  statusEl.textContent = heldDecision.decision;
  statusEl.className = `status-box ${heldDecision.decision.toLowerCase()}`;
  statusTextEl.textContent = heldDecision.desc;

  pushLimited(labels, indexLabel);
  pushLimited(ppgData, ppg);
  pushLimited(spo2Data, spo2);
  pushLimited(prData, pr);
  pushLimited(motionData, motion);
  pushLimited(reliabilityData, reliability);

  const estimatedBpm = estimateBpmFromPpg(ppgData, 5);
  ppgBpmEl.textContent = estimatedBpm ? `${estimatedBpm.toFixed(1)} BPM` : "--";

  refreshCharts();
}

const vitalsRef = query(ref(database, "vitals"), limitToLast(MAX_POINTS));

let counter = 0;
onChildAdded(vitalsRef, (snapshot) => {
  const data = snapshot.val();
  if (!data) return;

  counter += 1;
  updateDashboard(data, counter);
});