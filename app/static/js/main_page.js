$(function(){

    if(performance.navigation.type == 2){
        location.reload(true);
    }

    var $brand_selector = $('#brand-selector');
    var $line_selector = $('#line-selector');

    $brand_selector.on('change',function (e) {
        $line_selector.empty();
        $line_selector.append('<option value="">Dòng xe</option>')
        var filter_params = {
            brand: $brand_selector.val()
        }
        $.ajax({
            type: 'GET',
            url: '/api/v1/resources/lines/search',
            data: filter_params,
            success: function(line_list) {
                console.log('success', line_list);
                if (line_list.length === 0) $line_selector.append();
                else
                    $.each(line_list, function (i, lineit) {
                        $line_selector.append('<option value="'+lineit+'">'+lineit+'</option>');
                });
            },
            error: function () {
            }
        });
    })
})