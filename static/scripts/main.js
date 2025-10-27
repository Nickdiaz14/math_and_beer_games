// Toggle contact icons
const contact = document.querySelector('.contact');
const instagram = document.querySelector('.instagram');
const whatsapp = document.querySelector('.whatsapp');
const mail = document.querySelector('.mail');
const menuToggle = document.querySelector('.menu-toggle');
contact.addEventListener('click', () => {
  contact.classList.toggle('active');
  instagram.classList.toggle('active');
  mail.classList.toggle('active');
  whatsapp.classList.toggle('active');
  menuToggle.classList.toggle('active');
});

// Smooth scroll for internal links
document.addEventListener("DOMContentLoaded", () => {
  const navbar = document.querySelector(".navbar");
  const buttons = document.querySelectorAll(".navbar-nav button");

  buttons.forEach(btn => {
    btn.addEventListener("click", e => {
      const href = btn.getAttribute("onclick").match(/#\w+/);
      if (!href) return;
      const target = document.querySelector(href[0]);
      if (!target) return;

      e.preventDefault();
      const navbarHeight = navbar.offsetHeight;
      const elementPosition = target.getBoundingClientRect().top + window.scrollY;
      const offsetPosition = elementPosition - navbarHeight;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth"
      });

      // Cierra el menú hamburguesa si está abierto
      const collapse = document.querySelector(".navbar-collapse");
      const bsCollapse = bootstrap.Collapse.getInstance(collapse);
      if (bsCollapse) bsCollapse.hide();
    });
  });
});