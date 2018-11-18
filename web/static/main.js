function btnClick(x, index) {
	btn = $(x);
	$.ajax({
		'url': '/btn_click',
		'data': {
			'voo_index': index
		}
	});
}