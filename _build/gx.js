function(el,e){
  var g=el._g,now=performance.now();
  if(!g){
    var row=el.firstElementChild,tx=0;
    try{tx=-(new DOMMatrixReadOnly(getComputedStyle(row).transform).m41)||0;}catch(_){}
    row.style.animation='none';row.style.transform='none';
    g=el._g={row:row,drag:null,hover:false,touch:false,last:0,t:now,pos:tx};
    el.scrollLeft=tx;
    var wrap=function(){var h=row.scrollWidth/2;if(h<50)return;if(g.pos>=h)g.pos-=h;else if(g.pos<=0)g.pos+=h;};
    g.wrap=wrap;
    var step=function(t){
      if(!el.isConnected)return;
      var dt=Math.min(t-g.t,64);g.t=t;var h=row.scrollWidth/2;
      if(h>=50&&!g.drag&&!g.hover&&!g.touch&&t-g.last>1500){g.pos+=h/45000*dt;wrap();el.scrollLeft=g.pos;}
      requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  var ty=e.type;
  if(ty==='pointerenter'){if(e.pointerType==='mouse')g.hover=true;}
  else if(ty==='pointerleave'){g.hover=false;if(g.drag){g.drag=null;el.classList.remove('drag');g.last=now;}}
  else if(ty==='pointerdown'){
    if(e.pointerType==='mouse'){g.drag={x:e.clientX,p:g.pos};el.classList.add('drag');try{el.setPointerCapture(e.pointerId);}catch(_){}if(e.preventDefault)e.preventDefault();}
    else{g.touch=true;g.last=now;}
  }
  else if(ty==='pointermove'){if(g.drag){g.pos=g.drag.p-(e.clientX-g.drag.x);g.wrap();el.scrollLeft=g.pos;}}
  else if(ty==='pointerup'||ty==='pointercancel'){g.drag=null;g.touch=false;g.last=now;el.classList.remove('drag');}
  else if(ty==='scroll'){if(Math.abs(el.scrollLeft-g.pos)>2){g.pos=el.scrollLeft;g.last=now;var h=g.row.scrollWidth/2;if(h>=50&&(g.pos>=h||g.pos<=0)){g.wrap();el.scrollLeft=g.pos;}}}
}
