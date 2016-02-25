// get 10 requests
$(document).ready(function() {

    // load 10 last request ordering by pub_date
    load_requests = function () {

        var last_request = $('span[last_request]').attr('last_request'); // get id of the last request
        $.ajax({
            type: 'GET',
            url: '/request_list/',
            context: {last_request: last_request},
            success: function (msg) {
                var result = ""; // create variable for put there html with requests
                var i = 0; // create iterator with initial value 0

                // get json requests
                $.each(msg, function (key) {
                    if (msg[key]['pk']) {
                        // set number to span attribute for the first request that this is the last request(this is the last request added in db)
                        if (i==0) {

                            // verify that new request come in
                            if (msg[key]['pk'] != last_request && last_request != undefined){
                                // last id - last request id and get how many new requests
                                new_request = parseInt(msg[key]['pk']) - parseInt(last_request);
                                // if new request make doc. title "(count of new requests)"
                                    document.title = '(' + new_request + ')';
                            }
                            result += '<tr><td><span last_request=' + msg[key]['pk'] + '>' + msg[key]['pk'] + '</span></td>';
                        } else {
                            result += '<tr><td><span>' + msg[key]['pk'] + '</span></td>';
                        }
                    }
                    i++;
                    // create html table with requests
                    $.each(msg[key]['fields'], function (k, val) {
                        if (k !== 'request' && k !== 'title' && k !== 'pub_date') {
                            result += '<td>' + val + '</td>';
                        } else if (k == 'pub_date') {
                            result += '<td>' + val.slice(0, 19).replace("T"," ") + '</td>';
                        }

                    });
                    // replace last 10 request on new 10 requests
                    $('.result').replaceWith('<tbody class="result"><tr>' + result + '</tr></tbody>');
                });
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