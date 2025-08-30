let checker = document.getElementById('prompt-checker')

checker.addEventListener('click', function() {
    iseven = false
    value = Math.floor(Math.random() * 100)
    if (value % 2 == 0) {
        iseven = true
    }

    results(iseven)
})

let searchBar = document.querySelector('.search-bar')
let iconQuestion = document.getElementById('icon-question')
let iconCheck = document.getElementById('icon-check')
let iconCross = document.getElementById('icon-cross')

function results(bool) {
    if (bool == true) {
        searchBar.style.boxShadow = '0 0 30px #0f0';
        iconQuestion.classList.add('d-none');
        iconCheck.classList.remove('d-none');
        iconCross.classList.add('d-none');
    }
    else {
        searchBar.style.boxShadow = '0 0 30px #f00';
        iconQuestion.classList.add('d-none');
        iconCheck.classList.add('d-none');
        iconCross.classList.remove('d-none')
    }
}