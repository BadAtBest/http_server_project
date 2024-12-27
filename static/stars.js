const canvas = document.getElementById("star-canvas");
const ctx = canvas.getContext("2d");

let stars = [];
const numStars = 100;

// Resize canvas to fill the window
function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

// Create star objects
function createStars() {
    stars = [];
    for (let i = 0; i < numStars; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2,
            speedX: Math.random() * 0.5 - 0.25,
            speedY: Math.random() * 0.5 - 0.25,
        });
    }
}

// Draw stars
function drawStars() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    stars.forEach((star) => {
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
        ctx.fill();
    });
}

// Update star positions
function updateStars() {
    stars.forEach((star) => {
        star.x += star.speedX;
        star.y += star.speedY;

        // Wrap stars around the screen
        if (star.x < 0) star.x = canvas.width;
        if (star.x > canvas.width) star.x = 0;
        if (star.y < 0) star.y = canvas.height;
        if (star.y > canvas.height) star.y = 0;
    });
}

// Move stars when the mouse moves
canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    stars.forEach((star) => {
        const dx = star.x - mouseX;
        const dy = star.y - mouseY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 100) {
            star.speedX += dx * -0.01;
            star.speedY += dy * -0.01;
        }
    });
});

// Animation loop
function animate() {
    drawStars();
    updateStars();
    requestAnimationFrame(animate);
}

// Initialize
resizeCanvas();
createStars();
animate();
window.addEventListener("resize", () => {
    resizeCanvas();
    createStars();
});
