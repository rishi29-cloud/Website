/* Rishi Keshan — portfolio behaviour.

   Deliberately small. The hero chart animates in pure CSS, so nothing
   visual depends on this file loading or running. All that is left is the
   mobile menu and the footer year, each isolated so one cannot break the
   other. */

(function () {
  "use strict";

  function job(fn) {
    try {
      fn();
    } catch (error) {
      if (window.console && console.warn) {
        console.warn("portfolio: a non-critical step failed", error);
      }
    }
  }

  /* ── mobile menu ─────────────────────────────────────────── */
  job(function () {
    var toggle = document.querySelector(".menu-toggle");
    var nav = document.getElementById("main-nav");
    if (!toggle || !nav) return;

    function close() {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest && event.target.closest("a")) close();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        close();
        toggle.focus();
      }
    });
  });

  /* ── footer year ─────────────────────────────────────────── */
  job(function () {
    var year = document.getElementById("year");
    if (year) year.textContent = String(new Date().getFullYear());
  });
})();
