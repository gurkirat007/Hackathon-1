

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var today = new Date();
    var date = today.getFullYear()+"-"+today.getMonth()+"-"+today.getDate()+"-->"+today.getHours()+":"+today.getMinutes()
    socket.on("connect" , function() {
        var form = $("form").on("submit", function(e){
            e.preventDefault()
            let user_input = $("input#user_message").val()
            const queryString = window.location.search;
            const urlParams = new URLSearchParams(queryString);
            let user_id = urlParams.get('userid')

            socket.emit("message",{
                username: user_id,
                message: user_input
            })
            $("input#user_message").val("").focus()

        })

    })
    socket.on("message", function(msg){

        console.log(msg);
        username = msg['username']
        $("div.input-area").append(`
        <a href="/profile/${username}">${username}</a>
        <div class="darker container">
          <p>${msg['message']}</p>
          <span class="time-right">${date}</span>
        </div>
        `)
    })





