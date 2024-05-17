window.addEventListener('load',function () {
    let nav = document.getElementById("nav-location");
    let links = document.querySelectorAll("#nav-links a")
    console.log(nav);
    for (let link of links){
        link.addEventListener('mousemove', function(){
            let path = new URL(link.href).pathname;
            nav.textContent = ">>>"+path;
            nav.dataset.hovered = true;
        });
        link.addEventListener('mouseleave', function() {
            nav.textContent = ">>>";
            nav.dataset.hovered = false;
        })
    }
});