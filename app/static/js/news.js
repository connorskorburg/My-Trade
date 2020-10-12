const next = document.getElementById('next');
const prev = document.getElementById('prev');
const results = document.getElementById('results').value;

let img = document.querySelector('.news-img');
let headline = document.getElementById('headline');
let newsLink = document.querySelector('.news-link');
let source = document.querySelector('.source');
let newsContent = document.querySelector('.news-content');


const parsedResults = JSON.parse(results);
console.log(parsedResults)

next.addEventListener('click', () => {
  for(let i = 0; i < parsedResults.length; i++) {
    if (i === parsedResults.length - 1) {
      newsContent.setAttribute('id', 0)
      img.src = parsedResults[0]['image']
      headline.innerHTML = parsedResults[0]['headline'];
      newsLink.setAttribute('href', parsedResults[0]['url']);
      source.textContent = parsedResults[0]['source'];
    }
    else if(parseInt(newsContent.getAttribute('id', i)) === i) {
      img.src = parsedResults[i + 1]['image']
      headline.innerHTML = parsedResults[i + 1]['headline'];
      newsLink.setAttribute('href',parsedResults[i + 1]['url']);
      source.textContent = parsedResults[i + 1]['source'];
      if (parseInt(newsContent.getAttribute('id', i + 1)) === parsedResults.length) {
        newsContent.setAttribute('id', parsedResults.length - 1);
      } else {
        newsContent.setAttribute('id', i + 1)
      }
      break;
    }
  }
});




