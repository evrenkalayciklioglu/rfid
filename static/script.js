let timeoutTimer = null;

async function fetchStatus() {
  try {
    const res = await fetch("/status");
    const data = await res.json();

    if (data.timeout) {
      showMessage();
    } else if (data.runner) {
      showRunner(data.runner);
    } else {
      showMessage();
    }
  } catch (err) {
    console.error("Status fetch error:", err);
    showMessage();
  }
}

function showRunner(runner) {
  clearTimeout(timeoutTimer);
  timeoutTimer = setTimeout(showMessage, 60000);

  document.getElementById("info").classList.remove("hidden");
  document.getElementById("message").classList.add("hidden");

  document.getElementById("name").textContent     = runner.name || "";
  document.getElementById("bib").textContent      = runner.bib_no || "";
  document.getElementById("category").textContent = runner.category || "";
  document.getElementById("team").textContent     = runner.team || "";
  document.getElementById("gender").textContent   = runner.gender || "";
  document.getElementById("course").textContent   = runner.course || "";
  document.getElementById("country").textContent  = runner.country || "";
  document.getElementById("birthyear").textContent = runner.birthyear || "";

  const resultBox = document.getElementById("result-box");

  if (runner.time_total) {
    // Süre biçimi: 13h29'55 → 13:29:55
    const formattedTime = runner.time_total.replace("h", ":").replace("'", ":");

    // Bitiş zamanı biçimi: 20250405D20h30'38,650 → 05/04/2025 20:30:38
    // Ekrana yazdır
    //resultBox.innerHTML = `<b>${formattedTime}</b>  -  <b>${formattedFinish}</b>`;
    resultBox.innerHTML = `<b>${formattedTime}</b>`;
  } else {
    resultBox.textContent = "Yarışınız tamamlanmadı. / Your race is not complete.";
  }
}

function showMessage() {
  document.getElementById("info").classList.add("hidden");
  document.getElementById("message").classList.remove("hidden");

  const ids = ["name","bib","category","team","gender","course","country","date","result-box"];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = "";
  });
}

setInterval(fetchStatus, 1000);
fetchStatus();

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch("/ip", { cache: "no-store" });
    const data = await res.json();
    document.getElementById("ip-line").textContent = `IP: ${data.ip}`;
    document.getElementById("clax-line").textContent = `${data.clax}`;
  } catch (e) {
    const host = (location.host || "").split(":")[0];
    document.getElementById("ip-line").textContent = `IP: ${host || "-"}`;
    document.getElementById("clax-line").textContent = " -";
  }
});
