/* HTML document is loaded. DOM is ready. 
-------------------------------------------*/
$(function(){
  /* FlexSlider */
  $('.flexslider').flexslider({
      animation: "fade",
      directionNav: false
  });

  $(".rotate").textrotator();

  new WOW().init();

});