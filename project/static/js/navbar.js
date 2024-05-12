window.addEventListener('load',function () {
    let nav = document.getElementById("nav-location");
    let links = document.querySelectorAll(".header > a")
    for (let link of links){
        link.addEventListener('mousemove', function(){
            nav.textContent = ">>>"+link.getAttribute("href").match(/\/.*/g)[0]
        });
        link.addEventListener('mouseleave', function() {
            nav.textContent = ">>>"
        })
    }
});