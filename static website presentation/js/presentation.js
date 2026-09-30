
let current=0;
const sections=document.querySelectorAll('section');

function show(i){
sections.forEach(s=>s.classList.remove('active'));
sections[i].classList.add('active');
}

function next(){
current=(current+1)%sections.length;
show(current);
}

function prev(){
current=(current-1+sections.length)%sections.length;
show(current);
}
