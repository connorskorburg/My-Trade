const currentPrice = parseFloat(document.getElementById('current').value);
const symbol = document.getElementById('symbol').value;
const toggleTotal = document.getElementById('toggleTotal');
const totalShares = document.getElementById('total-shares');
const totalPrice = document.getElementById('total-price');
const totalSection = document.getElementById('total-section');


toggleTotal.addEventListener('click', () => {
  totalSection.style.display = 'block';
  const shares = parseFloat(document.getElementById('shares').value);
  let total = shares * currentPrice;
  total = total.toFixed(2)
  totalShares.textContent = shares;
  totalPrice.textContent = total;
});