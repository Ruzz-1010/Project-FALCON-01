
let index=0;
let timer=null;
const scenes=document.querySelectorAll('.scene');

function show(){
 scenes.forEach(s=>s.classList.remove('active'));
 scenes[index].classList.add('active');
}
function nextScene(){
 index=(index+1)%scenes.length;
 show();
}
function previousScene(){
 index=(index-1+scenes.length)%scenes.length;
 show();
}
function toggleAuto(){
 if(timer){clearInterval(timer);timer=null;}
 else{timer=setInterval(nextScene,5000);}
}
