$(function () {
    var $volumeAddCard = $('#volume-create-card');

    // init TouchSpin
    $("input[name='number']").TouchSpin({
        min: 1,
        max: 100,
        step: 1,
        decimals: 0,
        boostat: 5,
        maxboostedstep: 10,
        buttondown_class: "btn btn-primary",
        buttonup_class: "btn btn-primary",
        postfix: ''
    });
    $("input[name='capacity']").TouchSpin({
        min: 1,
        max: 1024,
        step: 1,
        decimals: 0,
        boostat: 5,
        maxboostedstep: 10,
        buttondown_class: "btn btn-primary",
        buttonup_class: "btn btn-primary",
        postfix: 'GB'
    });
});

$(function () {
    $('#volume-create-card form').submit(function (event) {
        var $this = $(this);
        event.preventDefault();
        $.addLoadingCover();
        $.ajax({
            url: $this.attr('action'),
            data: $this.serialize(),
            type: $this.attr('method'),
            success: function (res) {
                res = $.handleResponse(res);
            },
            complete: function () {

                $.removeLoadingCover();
            },
            error: function () {
            }
        });
    });
});