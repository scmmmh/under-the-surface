$(document).foundation();

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
