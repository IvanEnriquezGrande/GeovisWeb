// ---------Responsive-navbar-active-animation-----------
function test(){
	var tabsNewAnim = $('#navbarSupportedContent');
	var selectorNewAnim = $('#navbarSupportedContent').find('li').length;
	var activeItemNewAnim = tabsNewAnim.find('.active');
	var activeWidthNewAnimHeight = activeItemNewAnim.innerHeight();
	var activeWidthNewAnimWidth = activeItemNewAnim.innerWidth();
	var itemPosNewAnimTop = activeItemNewAnim.position();
	var itemPosNewAnimLeft = activeItemNewAnim.position();
	$(".hori-selector").css({
		"top":itemPosNewAnimTop.top + "px",
		"left":itemPosNewAnimLeft.left + "px",
		"height": activeWidthNewAnimHeight + "px",
		"width": activeWidthNewAnimWidth + "px"
	});

    $("#navbarSupportedContent").on("click", "li", function(e) {
        e.preventDefault();
        var linkHref = $(this).find('a').attr('href');
        $('#content').load(linkHref  + ' #content > *');
    });

	$("#navbarSupportedContent").on("click","li",function(e){
		$('#navbarSupportedContent ul li').removeClass("active");
		$(this).addClass('active');
		var activeWidthNewAnimHeight = $(this).innerHeight();
		var activeWidthNewAnimWidth = $(this).innerWidth();
		var itemPosNewAnimTop = $(this).position();
		var itemPosNewAnimLeft = $(this).position();
		$(".hori-selector").css({
			"top":itemPosNewAnimTop.top + "px",
			"left":itemPosNewAnimLeft.left + "px",
			"height": activeWidthNewAnimHeight + "px",
			"width": activeWidthNewAnimWidth + "px"
		});
	});
}
$(document).ready(function(){
	setTimeout(function(){ test(); });
});
$(window).on('resize', function(){
	setTimeout(function(){ test(); }, 500);
});
$(".navbar-toggler").click(function(){
	$(".navbar-collapse").slideToggle(300);
	setTimeout(function(){ test(); });
});



// --------------add active class-on another-page move----------
jQuery(document).ready(function($) {
    var path = window.location.pathname.split("/").pop();

    if (path == '') {
        path = 'index.html';
    }

    // Marcamos el enlace activo
    $('#navbarSupportedContent ul li a').each(function() {
        var href = $(this).attr('href');
        if (href === path) {
            $(this).parent().addClass('active');
        }
    });
});

$(document).ready(function() {
    // Obtiene la parte de la URL que identifica la página actual
    var path = window.location.pathname;

    // Marca la pestaña correspondiente como activa
    $('#navbarSupportedContent ul li').removeClass('active');
    $('#navbarSupportedContent ul li a[href="' + path + '"]').parent().addClass('active');
});