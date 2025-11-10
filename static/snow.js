const snowContainer = document.getElementById('snow-container');

function createSnowflake() {
    const snowflake = document.createElement('div');
    snowflake.classList.add('snowflake');
    snowflake.style.left = Math.random() * window.innerWidth + 'px';
    snowflake.style.fontSize = (10 + Math.random() * 20) + 'px';
    snowflake.style.opacity = Math.random();
    snowflake.style.animationDuration = (5 + Math.random() * 5) + 's';
    snowflake.innerText = '❄';
    snowContainer.appendChild(snowflake);

    setTimeout(() => {
        snowflake.remove();
    }, 10000);
}

setInterval(createSnowflake, 200);