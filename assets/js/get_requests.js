// get 10 requests
$(document).ready(function() {
    $('body').attr('new_request', 0);
    load_requests = function () {
        if ($('body').attr('new_request') == '0' || $('body').attr('new_request') == undefined) {
            var new_request = 0;
        } else {
            var new_request = $('body').attr('new_request')
        }
        var last_request = $('a[last_request]').attr('last_request');
        $.ajax({
            type: 'GET',
            url: '/request_list_ajax/',
            context: {last_request: last_request, new_request: new_request},
            success: function (msg) {
                var result = "";
                var i = 0;
                $.each(msg, function (key) {
                    if (msg[key]['pk']) {
                        if (i==0) {
                        if (msg[key]['pk'] != last_request && last_request != undefined){
                            new_request = parseInt(new_request) + parseInt(msg[key]['pk']) - parseInt(last_request);
                            if (new_request > 1){
                                document.title = new_request + " new requests";
                            } else {
                                document.title = new_request + " new request";
                            }
                            $('body').attr('new_request', new_request)
                        }
                            result += '<tr><td><a last_request=' + msg[key]['pk'] + ' href=\'/request_detail/' + msg[key]['pk'] + '/\'>' + msg[key]['pk'] + '</a></td>';
                        } else {
                            result += '<tr><td><a href=\'/request_detail/' + msg[key]['pk'] + '/\'>' + msg[key]['pk'] + '</a></td>';
                        }

                    }i++;
                    $.each(msg[key]['fields'], function (k, val) {
                       if (k !== 'request' && k !== 'title' && k !== 'pub_date') {
                           result += '<td>' + val + '</td>';
                       } else if (k == 'pub_date') {
                           result += '<td>' + val.slice(0, 19).replace("T"," ") + '</td>';
                       }

                    });
                    $('.result').replaceWith('<div class="col-xs-12 result"><table class="table table-bordered text-center"><tr><th>ID</th><th>Date</th><th>Path</th></tr><tr>' + result + '</tr></table></div>');
                });
                setTimeout(load_requests, 3000);
            }
        });
    };
    load_requests();
    $(document).hover(function (){
        document.title = "Request list";
        $('body').attr('new_request', 0)
    });
});