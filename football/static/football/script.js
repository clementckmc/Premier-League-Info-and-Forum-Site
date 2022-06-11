document.addEventListener('DOMContentLoaded', function() {

    // add class to selected team
    team = document.querySelector('#team-name')
    if (team != null) {
        team_id = team.getAttribute('team-id');
        document.querySelector('#' + team_id).classList.add("active");
    }

    // upvote/downvote
    document.querySelectorAll('.votebtn').forEach((element) => {
        // check upvote/downvote
        load_vote(element);

        // vote
        vote_post(element);

    })

    // quote
    document.querySelectorAll('.quotebtn').forEach((element) => {
        quote(element);
    })

});

function load_vote(element) {
    var post_id = element.getAttribute('vote-id');
    var tr = element.getAttribute('tr'); // thread or reply?
    if (document.querySelector('#' + tr + post_id).getAttribute('vote') == 'up') {
        document.querySelector('#' + "i" + tr + post_id + "up").setAttribute("class", "bi bi-caret-up-square-fill");
    } else if (document.querySelector('#' + tr + post_id).getAttribute('vote') == 'down') {
        document.querySelector('#' + "i" + tr + post_id + "down").setAttribute("class", "bi bi-caret-down-square-fill");
    } else {
        return false;
    }
}

// vote
function vote_post(element) {
    element.addEventListener('click', () => {
        var vote_id = element.getAttribute('vote-id');
        var tr = element.getAttribute('tr'); // thread or reply?
        var ud = element.getAttribute('ud'); // up or down vote?
        fetch("/vote_post/", {
            method: "POST",
            body: JSON.stringify({
                vote_id: vote_id,
                tr: tr,
                ud: ud
            })
        })
        .then(response => response.json())
        .then(response => {
            if (response.status == 201) {
                if (response.vote === 'u') {
                    document.querySelector('#' + tr + vote_id).setAttribute('vote', 'up');
                    document.querySelector('#' + "i" + tr + vote_id +'up').innerHTML = response.vote_count;
                } else if (response.vote === 'd') {
                    document.querySelector('#' + tr + vote_id).setAttribute('vote', 'down');
                    document.querySelector('#' + "i" + tr + vote_id +'down').innerHTML = response.vote_count;
                } else {
                    element.setAttribute('vote', 'None');
                }
                load_vote(element);
                document.getElementById(tr + vote_id + 'up').disabled = true;
                document.getElementById(tr + vote_id + 'down').disabled = true;
            }
        })
        .catch(e => console.log(e));
        return false;
    })
}

function quote(element) {
    element.addEventListener('click', () => {
        var quote_id = element.getAttribute('quote-id');
        var tr = element.getAttribute('tr');
        var poster = element.getAttribute('poster');
        var content = document.getElementById(tr + 'content' + quote_id).innerHTML;
        document.querySelector('.replyBox').focus();
        if (content.charAt(content.length - 1) === '>' && content.charAt(content.length - 2) === 'r' && content.charAt(content.length - 3) === 'b') {
            content = content.replace(/<br><br>$/, '');
        };
        console.log(content);
        document.querySelector('.replyBox').innerHTML = '<blockquote>' + poster + " said: " + "<br>" + content + '</blockquote>';
    })
    return false;
}