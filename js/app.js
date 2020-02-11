$(document).foundation();
tippy('[data-tippy-content]');

(function() {
    function setup_anchor(anchor) {
        if (!anchor.getAttribute('data-action-toggle-display')) {
            anchor.addEventListener('click', function(ev) {
                ev.preventDefault();
                let element = document.querySelector(anchor.getAttribute('data-toggle-display'));
                element.classList.toggle('hidden');
            });
            anchor.setAttribute('data-action-toggle-display', 'true');
        }
    }

    let anchors = document.querySelectorAll('a[data-action="toggle-display"]');
    for(let idx = 0; idx < anchors.length; idx++) {
        setup_anchor(anchors[idx]);
    }
})();


(function() {
    function setup_anchor(anchor) {
        if (!anchor.getAttribute('data-action-read-more')) {
            let container = anchor.parentElement.parentElement;
            let paragraphs = container.querySelectorAll('p');
            if (paragraphs.length > 1) {
                for(let idx = 1; idx < paragraphs.length; idx++) {
                    paragraphs[idx].classList.add('hidden');
                }
                anchor.addEventListener('click', function(ev) {
                    ev.preventDefault();
                    let paragraphs = container.querySelectorAll('p');
                    for(let idx = 1; idx < paragraphs.length; idx++) {
                        paragraphs[idx].classList.toggle('hidden');
                    }
                    anchor.parentElement.classList.add('hidden');
                });
            } else {
                anchor.parentElement.classList.add('hidden');
            }
            anchor.setAttribute('data-action-read-more', 'true');
        }
    }

    let anchors = document.querySelectorAll('a[data-action="read-more"]');
    for(let idx = 0; idx < anchors.length; idx++) {
        setup_anchor(anchors[idx]);
    }
})();
