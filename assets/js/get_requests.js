// get 10 requests
$(document).ready(function() {

    // load 10 last request ordering by pub_date
    load_requests = function () {

        var last_request = $('span[last_request]').attr('last_request'); // get id of the last request
        $.ajax({
            type: 'GET',
            url: '/request_list/',
            context: {last_request: last_request},
            data: {last_request: last_request},
            success: function (data) {
                // count how much tr need to remove
                remove_tr = 10 - data.length;

                // remove tr's
                $('.result').find('tr:gt(' + remove_tr + ')').remove();

                // put new requests on the page
                $.each(data, function(key, value){
                    var new_request = '<tr>' +
                    '<td><span last_request="' + value.pk + '">' + value.pk + '</span></td>' +
                    '<td>' + value.fields.pub_date.slice(0, 19).replace("T"," ") + '</td>' +
                    '<td>' + value.fields.path + '</td></tr>';
                    $('.result').prepend(new_request);
                });

                // update title count of new requests
                if (data.length > 0) {
                    document.title = '(' + data.length + ')';
                }

                // load function every 3 seconds.
                setTimeout(load_requests, 3000);
            }
        });
    };

    load_requests();

    // when user see page, title become Request list
    $(window).on('blur focus', function (){
        document.title = "Request list";
    });
});