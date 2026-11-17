// Menu button for the shared site navigation on small screens.
(function () {
  var header = document.querySelector(".site-nav");
  if (!header) return;
  var button = header.querySelector(".sn-toggle");
  var nav = header.querySelector("nav");
  if (!button || !nav) return;

  header.classList.add("sn-js");

  function setOpen(open) {
    header.classList.toggle("sn-open", open);
    button.setAttribute("aria-expanded", open ? "true" : "false");
    button.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  button.addEventListener("click", function () {
    setOpen(!header.classList.contains("sn-open"));
  });

  // Close after choosing a link, tapping elsewhere, or pressing Escape.
  nav.addEventListener("click", function (event) {
    if (event.target.closest("a")) setOpen(false);
  });
  document.addEventListener("click", function (event) {
    if (!header.contains(event.target)) setOpen(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && header.classList.contains("sn-open")) {
      setOpen(false);
      button.focus();
    }
  });
})();
