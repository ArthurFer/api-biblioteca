// Cadastro de Usuário
document.getElementById("signupForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://localhost:8000/usuarios", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username: username, email: email, password: password })
    });

    if (response.ok) {
        document.querySelector(".success-message").textContent = "Cadastro realizado com sucesso!";
        document.querySelector(".success-message").style.display = "block";
        window.location.href = "/painel";
    } else {
        const errorMsg = await response.text();
        document.querySelector(".error-message").textContent = errorMsg;
        document.querySelector(".error-message").style.display = "block";
    }
});

// Login de Usuário
document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;

    const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email: email, password: password })
    });

    if (response.ok) {
        document.querySelector(".success-message").textContent = "Login bem-sucedido!";
        document.querySelector(".success-message").style.display = "block";
        window.location.href = "/painel";
    } else {
        const errorMsg = await response.text();
        document.querySelector(".error-message").textContent = errorMsg;
        document.querySelector(".error-message").style.display = "block";
    }
});
