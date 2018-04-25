$(function() {
    $("#query-form").submit(function(e) {
        $("#error-message").hide();
        $("#loader").addClass("active");
        $.ajax({
            type: "POST",
            url: "parse",
            data: JSON.stringify($("#query").val()),
            contentType: "application/json",
            success: function(data)
            {
                var html = "<div class='ui list'>";
                for(var i in data)
                {
                    var group = data[i];
                    html += "<div class='item'><img src='" + group.icon + "'/><div class='content' style='display:inline;'><div class='header' style='display:inline;'>" + group.title + "</div><div class='ui bulleted list'>";
                    for(var j in group.items)
                    {
                        html += "<div class='item'>" + group.items[j] + "</div>";
                    }
                    html += "</div></div></div>";
                }
                html += "</div>";
                $("#result").html(html);
                $("#loader").removeClass("active");
            },
            error: function(xhr)
            {
                $("#loader").removeClass("active");
                if(typeof xhr.responseJSON === 'undefined')
                    $("#error-message-text").text("Unknown error");
                else
                    $("#error-message-text").text(xhr.responseJSON.message);
                $("#error-message").show();
            }
        });
        e.preventDefault();
    });
});
