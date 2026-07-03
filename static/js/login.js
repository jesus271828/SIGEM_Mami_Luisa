// ================================
// SIGEM - Login
// Archivo: login.js
// ================================

// Mostrar u ocultar contraseña
function togglePassword() {

    const password = document.getElementById("password");
    const icon = document.getElementById("togglePassword");

    if (password.type === "password") {
        password.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        password.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}


// Animación al cargar la página
window.addEventListener("load", () => {

    const login = document.querySelector(".login-container");

    login.classList.add("show");

});


// Efecto al enviar el formulario
const form = document.querySelector("form");

if (form) {

    form.addEventListener("submit", () => {

        const boton = document.querySelector(".btn-login");

        boton.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Ingresando...';

        boton.disabled = true;

    });

}