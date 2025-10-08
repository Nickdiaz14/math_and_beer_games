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