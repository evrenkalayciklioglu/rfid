let timeoutTimer = null;

async function fetchStatus() {
  try {
    const res = await fetch("/status");
    const data = await res.json();

    if (data.timeout) {
      showMessage();
    } else if (data.runner) {
      showRunner(data.runner);
    }
  } catch (err) {
    console.error("Status fetch error:", err);
  }
}

function showRunner(runner) {
  clearTimeout(timeoutTimer);
  timeoutTimer = setTimeout(showMessage, 60000);

  // Bilgi ekranını göster, mesajı gizle
  document.getElementById("info").classList.remove("hidden");
  document.getElementById("message").classList.add("hidden");

  // Alanlara veriyi yaz
  document.getElementById("name").textContent = runner.name || "";
  document.getElementById("bib").textContent = runner.bib_no || "";
  document.getElementById("category").textContent = runner.category || "";
  document.getElementById("team").textContent = runner.team || "";
  document.getElementById("gender").textContent = runner.gender || "";
  document.getElementById("course").textContent = runner.course || "";
  document.getElementById("country").textContent = runner.country || "";
  document.getElementById("date").textContent = new Date().toLocaleDateString();
}

function showMessage() {
  document.getElementById("info").classList.add("hidden");
  document.getElementById("message").classList.remove("hidden");
}

// 1 sn’de bir backend’den sorgula
setInterval(fetchStatus, 1000);
fetchStatus();

