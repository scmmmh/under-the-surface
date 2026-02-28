(function() {
  window.addEventListener('DOMContentLoaded', () => {
    for (const elem of document.querySelectorAll('#metadata dd')) {
        if (elem.innerHTML.startsWith("textgrid:")) {
            elem.innerHTML='<a href="https://textgridrep.org/browse/' + elem.innerHTML.substring(9) + '" target="_blank">TextGrid</a>';
        }
    }
  });
})()
