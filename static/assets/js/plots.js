$('#change_data').on('change',function(){

    $.ajax({
        url: "/data_ts",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('change_data').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
        }
    });
})

$('#change_type').on('change',function(){

    $.ajax({
        url: "/type_ts",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('change_type').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
        }
    });
})

$('#change_scale').on('change',function(){

    $.ajax({
        url: "/scale_ts",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('change_scale').value

        },
        dataType:"json",
        success: function (data) {
            Plotly.newPlot('bargraph', data );
        }
    });
})

$('#change_grp').on('change', function () {

    $.ajax({
        url: "/agegrp",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('change_grp').value

        },
        dataType: "json",
        success: function (data) {
            Plotly.newPlot('agegrpplt', data);
        }
    });
})

$('#change_country').on('change', function () {

    $.ajax({
        url: "/policycountry",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: {
            'selected': document.getElementById('change_country').value

        },
        dataType: "json",
        success: function (data) {
            Plotly.newPlot('bar_graph', data);
        }
    });
})