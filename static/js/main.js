const themeButton = document.getElementById("themeButton");

const html = document.documentElement;

const savedTheme = localStorage.getItem("theme");

if(savedTheme){

    html.setAttribute("data-bs-theme", savedTheme);

    themeButton.innerHTML =
        savedTheme === "dark" ? "☀️" : "🌙";

}

themeButton.onclick = () => {

    let theme = html.getAttribute("data-bs-theme");

    if(theme==="light"){

        html.setAttribute("data-bs-theme","dark");

        localStorage.setItem("theme","dark");

        themeButton.innerHTML="☀️";

    }

    else{

        html.setAttribute("data-bs-theme","light");

        localStorage.setItem("theme","light");

        themeButton.innerHTML="🌙";

    }

};