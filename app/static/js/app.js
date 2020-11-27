$(function () {

    var $car_name = $('#car-name');
    var $status = $("input[name='status-option']:checked");
    var $source_image = $("input[name='source-option']:checked");
    var ctx = $("#line-chart");


    $('input[name="status-option"]').on('click change', function(e) {
        $status= $('input[name="status-option"]:checked');
    });

    $('input[name="source-option"]').on('click change', function(e) {
        $source_image = $('input[name="source-option"]:checked');
    });



    // $("input[name='source-option']").on('click', function () {
    //     var filter_params = {
    //         car_name: $car_name.val(),
    //         year: $year.val(),
    //         status: $status.val(),
    //         source: $source_image.val()
    //     };
    //     console.log('status', $status.val());
    //     console.log('year', $year.val());
    //     console.log('source', $source_image.val());
    //     $car_list.empty();
    //
    //     $.ajax({
    //         type: 'GET',
    //         url: 'http://localhost:5000/api/v1/resources/cars/search',
    //         data: filter_params,
    //         success: function(price_list) {
    //             console.log('success', price_list);
    //             if (price_list.price.length === 0) $car_list.append('<li><strong>Không tìm thấy nơi bán nào phù hợp với yêu cầu</strong></li>');
    //             else
    //                 $.each(price_list.price, function (i, priceit) {
    //                     $car_list.append(Mustache.render(itemTemplate_2, priceit));
    //             });
    //         },
    //         error: function () {
    //             $car_list.append('<li><strong>Không tìm thấy nơi bán nào phù hợp với yêu cầu</strong></li>');
    //         }
    //     });
    // });

    $(function() {
        var yearValue = localStorage.getItem("year-filter");
        var cityValue = localStorage.getItem("city-filter");

        if(yearValue != null) {
            $("select[name=year-filter]").val(yearValue);
        }
        if(cityValue != null) {
            $("select[name=city-filter]").val(cityValue);
        }

        $("select[name=year-filter]").on("change", function() {
            localStorage.setItem("year-filter", $(this).val());
        });
        $("select[name=city-filter]").on("change", function() {
            localStorage.setItem("city-filter", $(this).val());
        });
    })


    $(document).ready(function(){
        var radios = document.getElementsByName("status-option");
        var val = localStorage.getItem('statusValue');
        if (val == null){
            console.log("Nothing");
        }
        else {
            for(var i=0;i<radios.length;i++){
            if(radios[i].value == val){
                radios[i].checked = true;
                document.getElementById(radios[i].id).parentElement.className += " active";
            }
            else {
                document.getElementById(radios[i].id).parentElement.classList.remove("active");
            }

        }
        }
        $('input[name="status-option"]').on('change', function(){
            localStorage.setItem('statusValue', $(this).val())
        });
    });

    function loadChartData(){
        var params = {
            name: $car_name.val()
        }
        $.ajax({
            type: 'GET',
            url: '/api/v1/resources/cars/chart',
            data: params,
            success: function(chart_data) {
                console.log('success', chart_data);
                scatterChart.data.datasets[0].data = chart_data;
                scatterChart.update();
            },
            error: function () {
                console.log("Failed")
            }
        });
    }

    $(function() {
        $("button[id=chart-button]").on("click", function () {
            var x = document.getElementById("price-chart");
            if (x.style.display === "none") {
                x.style.display = "block";
                loadChartData();

            } else {
                x.style.display = "none";
            }
        })
    });



    // Draw chart
    var scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                backgroundColor:[
                    'rgba(153, 102, 255, 0.6)'
                ],
                data: [],
                borderWidth:1,
                borderColor:'#777',
                hoverBorderWidth:3,
                hoverBorderColor:'#000'
            }]
        },
        options: {
            title:{
                display:true,
                text:'Giá xe theo năm sản xuất',
                fontSize:25
            },
            scales: {
                xAxes: [{
                    type: 'linear',
                    position: 'bottom',
                    scaleLabel: {
                        display: true,
                        labelString: 'Năm'
                    },
                    ticks: {
                        stepSize: 1
                    }
                }],
                yAxes: [{
                    position: 'left',
                    gridLines: {
                      zeroLineColor: "rgba(0,255,0,1)"
                    },
                    scaleLabel: {
                      display: true,
                      labelString: 'Giá (triệu)'
                    }
                }]
            },
            legend: {
                display: false
            },
            tooltips: {
                callbacks: {
                   label: function(tooltipItem) {
                          return tooltipItem.yLabel;
                   }
                }
            },
            layout:{
                padding:{
                left:50,
                right:0,
                bottom:0,
                top:0
              }
            },
            xAxisID: "Năm",
            yAxisID: "Giá"
        }
    });


});

