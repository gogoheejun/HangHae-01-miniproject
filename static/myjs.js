
show_video()
clear_page = setInterval(()=>{

    save_url()
    show_video()
    // delete_posts()
},10000)

function show_video() {
    $.ajax({
        type: "GET",
        url: "/show_video",
        data: {},
        success: function (response) {
            if(response["url"] == null) {
                console.log("null이라 다시함수 고")
                return }
            if (response["result"] == "success") {
                let url = response["url"]
                let temp_html = `
                <iframe src="${url}" frameborder="0"
                allow="accelerometer; autoplay=1; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                   allowfullscreen=""></iframe>
                `
                $("#video-place").append(temp_html)

                console.log(url);
            }else{
                console.log("유튜브 가져오는 과정에서 예외")
                console.log(response)
            }

        }
    })
}

function save_url() {
    $("#video-place").empty()
    $.ajax({
        type: "POST",
        url: "/save_url",
        data: {},
        success: function (response) {
            console.log(response["msg"])
        }
    })
}

function delete_posts(){
    $.ajax({
        type: "POST",
        url: "/delete_post",
        data: {},
        success: function (response) {
            console.log(response)
            //window.location.href = "/"
        }
    })
}

function delete_comment(comment){
    $.ajax({
        type: "POST",
        url: "/delete_comment",
        data: {
            comment_give: comment
        },
        success: function (response) {
            console.log(response)
            alert(response["msg"])
            window.location.href = "/"
        }
    })
}



//댓글 업로드(수정포함)
function post() {
    let comment = $("#textarea-post").val()
    let today = new Date().toISOString()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            comment_give: comment,
            date_give: today,
            postId_give: post_id,
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active")
            window.location.reload()
        }
    })
}
//댓글업데이트를 위해 전역으로 만들어줌
let post_id= null;

function update_post(id){
    post_id = id;
    let modal = document.getElementById('modal-post');
    modal.classList.add("is-active")
}



//댓글가져오기-index.html과 user.html에서 모두 사용됨
function get_posts(username) {
    if (username == undefined) {
        username = ""
    }
    $("#post-box").empty()
    $.ajax({
        type: "GET",
        url: `/get_posts?username_give=${username}`,
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"]
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i]
                    let time_post = new Date(post["date"])
                    let time_before = time2str(time_post)

                    let class_heart = post['heart_by_me'] ? "fa-heart" : "fa-heart-o"

                    let html_temp_true = `<div class="box" id="${post["_id"]}"> 
                                        <article class="media">
                                            <div class="media-left">
                                                <a class="image is-64x64" href="/user/${post['username']}">
                                                    <img class="is-rounded" src="/static/${post['profile_pic_real']}"
                                                         alt="Image">
                                                </a>
                                            </div>
                                            <div class="media-content">
                                                <div class="content">
                                                    <p>
                                                        <strong>${post['profile_name']}</strong> <small>@${post['username']}</small> <small>${time_before}</small>
                                                        <br>
                                                        ${post['comment']}
                                                    </p>
                                                </div>
                                                <nav class="level is-mobile">
                                                    <div class="level-left">
                                                        <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                            <span class="icon is-small"><i class="fa ${class_heart}"
                                                                                           aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post["count_heart"])}</span>
                                                        </a>
                                                    </div>
                                                    <div class="level-right">
                                                       <button id="btn-edit" class="btn btn-sparta btn-lg0" onclick="update_post('${post['comment']}')">
                                                            <i class="fa fa-pen-o" aria-hidden="true"></i>                                                        
                                                        <button id="btn-delete" class="btn btn-sparta btn-lg0" onclick="delete_comment('${post['comment']}')">
                                                            <i class="fa fa-trash-o" aria-hidden="true"></i>
                                                    </div>
               
                                                </nav>
                                            </div>
                                             <div class="media-right">
<!--                                             수정버튼 누르면 모달띄우고, js의 post_id에 id넣어줌-->                                               
                                            </div>
                                        </article>
                                    </div>`

                    let html_temp_false = `<div class="box" id="${post["_id"]}"> 
                                        <article class="media">
                                            <div class="media-left">
                                                <a class="image is-64x64" href="/user/${post['username']}">
                                                    <img class="is-rounded" src="/static/${post['profile_pic_real']}"
                                                         alt="Image">
                                                </a>
                                            </div>
                                            <div class="media-content">
                                                <div class="content">
                                                    <p>
                                                        <strong>${post['profile_name']}</strong> <small>@${post['username']}</small> <small>${time_before}</small>
                                                        <br>
                                                        ${post['comment']}
                                                    </p>
                                                </div>
                                                <nav class="level is-mobile">
                                                    <div class="level-left">
                                                        <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                            <span class="icon is-small"><i class="fa ${class_heart}"
                                                                                           aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(post["count_heart"])}</span>
                                                        </a>
                                                    </div>

                                                </nav>
                                            </div>
                     
                                        </article>
                                    </div>`
                    post['by_me']? $("#post-box").append(html_temp_true): $("#post-box").append(html_temp_false);
                }
            }
        }
    })
}

function time2str(date) {
    let today = new Date()
    let time = (today - date) / 1000 / 60  // 분

    if (time < 60) {
        return parseInt(time) + "분 전"
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전"
    }
    time = time / 24
    if (time < 7) {
        return parseInt(time) + "일 전"
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`
}

function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}

function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='${type}']`)
    let $i_like = $a_like.find("i")
    let class_s = {"heart": "fa-heart", "star": "fa-star", "like": "fa-thumbs-up"}
    let class_o = {"heart": "fa-heart-o", "star": "fa-star-o", "like": "fa-thumbs-o-up"}
    if ($i_like.hasClass(class_s[type])) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass(class_o[type]).removeClass(class_s[type])
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass(class_s[type]).removeClass(class_o[type])
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })

    }
}