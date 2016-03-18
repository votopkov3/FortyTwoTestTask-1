// get 10 requests
$(document).ready(function() {
    var new_req = 0;
    var last_request_identify = 0;

    var old_request = 0;
    // load 10 last request ordering by pub_date
    load_requests = function () {
        if ($('span[last_request]').attr('last_request') == '') {
            var last_request = old_request;
        } else {
            var last_request = $('span[last_request]').attr('last_request'); // get id of the last request
            old_request = $('span[last_request]').attr('last_request'); // get id of the last request

        }
        $.ajax({
            type: 'GET',
            url: '/request_list/',
            context: {last_request: last_request},
            data:{'old_request': old_request},
            success: function (data) {
                // remove tr's
                var new_request = " ";
                // put new requests on the page
                $.each(data.requests_data, function(key, value){
                    new_request += '<tr>' +
                    '<td><span last_request="">' + value.pk + '</span></td>' +
                    '<td>' + value.fields.pub_date.slice(0, 19).replace("T"," ") + '</td>' +
                    '<td>' + value.fields.path + '</td>' +
                        '<td>' + value.fields.priority + '</td></tr>';
                });
                $('.result').html(new_request);
                // update title count of new requests

                new_req = parseInt(data.last_request_id) - parseInt(old_request);

                last_request_identify = data.last_request_id;

                if (new_req > 0) {
                    document.title = '(' + new_req + ')';
                }


                // load function every 3 seconds.
                setTimeout(load_requests, 3000);
            }
        });
    };

    load_requests();

    // when user see page, title become Request list
    $(window).on('focus click', function (){
        document.title = "Request list";
        ($('span[last_request]').attr('last_request', last_request_identify));
    });
});