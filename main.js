const menuCnt = document.getElementById("menu-container");
const navCnt = document.getElementById("nav-content");
const navCont = document.getElementById("nav-container");
const box = document.getElementById("black-box");
const scrollBtn = document.getElementById("scrollTopBtn");

const logoImg = document.getElementById("logo-img");
const logoBox = document.getElementById("logo-box");

const signUp = document.getElementById("signUp");
const signBtn = document.getElementById("sign-btn");
const log = document.getElementById("login");

const nav = document.getElementById("nav-bar");

const targets = document.querySelectorAll(
  "header .main-navigation .nav-list .tar"
);

const show = document.getElementById("show");
const blurBtn = document.getElementById("blur");
const over = document.getElementById("overview");

var num = 1;

let isMobile = window.matchMedia("(max-width: 1024px)").matches;
let hide = false;
let control = false;
let isLimit = false;
let clamp = false;
let canChange;
let canClose = false;
let isOnce = false;

// Add to main.js
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    const currentPage = window.location.pathname;
    
    // If on protected pages and not authenticated, redirect to login
    if (currentPage.includes('dashboard.html') && !token) {
        window.location.href = 'login.html';
    }
    
    // If on auth pages and already authenticated, redirect to dashboard
    if ((currentPage.includes('login.html') || currentPage.includes('signup.html')) && token) {
        window.location.href = 'dashboard.html';
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', checkAuth);

// Logout functionality
function logout() {
    localStorage.removeItem('auth_token');
    window.location.href = 'index.html';
}
window.addEventListener("resize", function () {
  checkMobile();

  if (canClose == false) {
    courseDropAll();
    canClose = true;
  }
});

function checkMobile() {
  isMobile = window.matchMedia("(max-width: 1024px)").matches;

  if (isMobile == true && hide == false) {
    hide = true;
    menuCollapse();
  }

  if (isMobile == false && hide == true) {
    hide = false;
    menuCollapse();
  }
}

function showMenu() {
  const isShowing = !menuCnt.classList.contains("active");

  if (isShowing) {
    menuExpand();
  } else {
    menuCollapse();
  }
}

function menuExpand() {
  menuCnt.classList.add("active");
  navCont.classList.add("active");
  box.classList.add("active");
}

function menuCollapse() {
  menuCnt.classList.remove("active");
  navCont.classList.remove("active");
  box.classList.remove("active");
  const btn1 = document.querySelector(".account-dropdown");
  const btn2 = document.querySelector(".prog");
  progCollapse(btn1);
  progCollapse(btn2);
}

function showProg(button) {
  const arr = button.querySelector("i");
  const isExpanding = !arr.classList.contains("active");

  if (isExpanding) {
    progExpand(button);
  } else {
    progCollapse(button);
  }
}

function progExpand(button) {
  const arr = button.querySelector("i");
  arr.classList.add("active");
  const cont = button.closest("li");
  const dropCnt = cont.querySelector(".container");

  if (isMobile == true) {
    dropCnt.style.height = "auto";
    const fullHeight = dropCnt.offsetHeight + "px";
    dropCnt.style.height = "0px";
    dropCnt.offsetHeight;
    dropCnt.style.height = fullHeight;
    dropCnt.classList.add("drop");
  } else {
    dropCnt.style.height = "auto";
    dropCnt.classList.add("drop2");
  }
}

function progCollapse(button) {
  const arr = button.querySelector("i");
  arr.classList.remove("active");
  const cont = button.closest("li");
  const dropCnt = cont.querySelector(".container");

  if (isMobile == true) {
    dropCnt.style.height = dropCnt.offsetHeight + "px";
    dropCnt.offsetHeight;
    dropCnt.style.height = "0px";
    dropCnt.classList.remove("drop");
    dropCnt.classList.remove("drop2");
  } else {
    dropCnt.style.height = "auto";
    dropCnt.classList.remove("drop");
    dropCnt.classList.remove("drop2");
  }
}

document.addEventListener("touchstart", () => {}, true);
