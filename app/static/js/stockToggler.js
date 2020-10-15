const buyTrade = () => {
  document.getElementById('total-section').style.display = 'block';
  const shares = parseFloat(document.getElementById('shares').value);
  const currentPrice = parseFloat(document.getElementById('current').value);
  let total = shares * currentPrice;
  total = total.toFixed(2);
  document.getElementById('total-shares').textContent = shares;
  document.getElementById('hidden-shares').value = shares;
  document.getElementById('total-price').textContent = total;
  document.getElementById('hidden-total').value = total;
  if (parseFloat(document.getElementById('total-balance').value) < total || shares === 0) {
    document.getElementById('buy-btn').style.display = 'none';
    console.log(parseFloat(document.getElementById('total-balance').value))
  }
  else if (parseFloat(document.getElementById('total-balance').value) > total) {
    document.getElementById('buy-btn').style.display = 'block';
  }
}

const sellTrade = () => {
  document.getElementById('sell-section').style.display = 'block';
  const sellShares = parseFloat(document.getElementById('sell-shares').value);
  const boughtShares = parseFloat(document.getElementById('bought-shares').value);
  const currentSell = parseFloat(document.getElementById('current-sell').value);
  let totalGained = sellShares * currentSell;
  totalGained = totalGained.toFixed(2);
  document.getElementById('total-sell-shares').textContent = sellShares;
  document.getElementById('shares_sold').value = sellShares;
  document.getElementById('total-gained').textContent = totalGained;
  document.getElementById('total_price_gained').value = totalGained;
  document.getElementById('price_sold').value = parseFloat(currentSell);
  console.log("Bought",boughtShares);
  console.log("To Sell",parseFloat(document.getElementById('sell-shares').value));
  if (boughtShares < parseFloat(document.getElementById('sell-shares').value) || parseFloat(document.getElementById('sell-shares').value) <= 0) {
    console.log('too much')
    document.getElementById('sell-btn').style.display = 'none';
  } else if (boughtShares >= parseFloat(document.getElementById('sell-shares').value)) {
    console.log('less')
    document.getElementById('sell-btn').style.display = 'block';
  }
}