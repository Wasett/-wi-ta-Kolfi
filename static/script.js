// ---------------- Losowanie ----------------
const participants = ["Ania", "Bartek", "Cezary", "Dorota", "Ewa"];
let drawn = {};

const drawBtn = document.getElementById("draw-btn");
const participantSelect = document.getElementById("participant");
const resultEl = document.getElementById("result");

drawBtn.addEventListener("click", () => {
    const name = participantSelect.value;
    if (!name) {
        alert("Wybierz swoje imię!");
        return;
    }

    if (drawn[name]) {
        alert("Już wylosowałeś! Poczekaj na reset admina.");
        return;
    }

    const available = participants.filter(p => p !== name && !Object.values(drawn).includes(p));

    if (available.length === 0) {
        alert("Brak dostępnych osób do wylosowania!");
        return;
    }

    const random = available[Math.floor(Math.random() * available.length)];
    drawn[name] = random;
    resultEl.textContent = `Wylosowałeś: ${random}!`;
});

// ---------------- Śnieg ----------------
const snowContainer = document.getElementById("snow-container");

function createSnowflake() {
    const snowflake = document.createElement("div");
    snowflake.classList.add("snowflake");
    snowflake.style.left = Math.random() * window.innerWidth + "px";
    snowflake.style.fontSize = Math.random() * 24 + 12 + "px";
    snowflake.style.opacity = Math.random();
    snowflake.style.animationDuration = Math.random() * 3 + 2 + "s";
    snowflake.textContent = "❄";
    snowContainer.appendChild(snowflake);

    setTimeout(() => {
        snowflake.remove();
    }, 5000);
}

setInterval(createSnowflake, 200);
