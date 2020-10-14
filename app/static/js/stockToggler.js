const buyTrade = () => {
  document.getElementById('total-section').style.display = 'block';
  const shares = parseFloat(document.getElementById('shares').value);
  const currentPrice = parseFloat(document.getElementById('current').value);
  let total = shares * currentPrice;
  total = total.toFixed(2);
  document.getElementById('total-shares').textContent = shares;
  document.getElementById('total-price').textContent = total;
}

const sellTrade = () => {
  document.getElementById('sell-section').style.display = 'block';
  const sellShares = parseFloat(document.getElementById('sell-shares').value);
  const currentSell = parseFloat(document.getElementById('current-sell').value);
  let totalGained = sellShares * currentSell;
  totalGained = totalGained.toFixed(2);
  document.getElementById('total-sell-shares').textContent = sellShares;
  document.getElementById('total-gained').textContent = totalGained;
}