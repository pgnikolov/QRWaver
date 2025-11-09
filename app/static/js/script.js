// Subtle hover ripple for CTA (cosmetic)
document.addEventListener('click', e => {
  const t = e.target.closest('.btn-primary');
  if(!t) return;
  t.style.transform = 'translateY(1px) scale(.995)';
  setTimeout(()=> (t.style.transform=''), 90);
});
