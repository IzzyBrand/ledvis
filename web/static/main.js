// $(document).ready(function(){

// 	console.log("adding slider");
// 	var slider = document.getElementById("brightnessSlider");

// 	slider.addEventListener('mouseup', function() {
// 		console.log(slider.value);
// 		$.ajax({
// 			'url': '/brightness_slider',
// 			'data': {
// 				'brightness': slider.value
// 			}
// 		});
// 	});
// });

function btnClick(x, index) {
	btn = $(x);
	$.ajax({
		'url': '/btn_click',
		'data': {
			'vis_index': index
		}
	});
}