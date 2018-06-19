//Javascript for the dashboard

function showFriendSuccess(result){
    $('#friend-success').text(result);
}

function addFriend(evt){

var formInput = {
  'friend' : $("#friend").val()
}

$.post('/add-friend',
      formInput, 
      showFriendSuccess);
}


$("#add-friend").on("click", addFriend);

// Javascript for the site details page


function showFavoriteSuccess(result){
  $('#success-message').text(result)
}

function favoriteSite(evt){

var formInput = {
  'path' : window.location.pathname.slice(7)
}

$.post('/favorite',
      formInput, 
      showFavoriteSuccess);

}

function showTripSuccess(result){
$('#trip-success').text(result)
}

 function scheduleTrip(evt){
    var email_list = getAttendeeEmails();
    console.log(email_list);
    var formInputs = {
        "date": $("#datepicker").val(),
        "path" : window.location.pathname.slice(7),
        "email_list": email_list, 
        'message': $("#message").val()
    };
    console.log(formInputs);
    $.post("/trip", 
         formInputs,
         showTripSuccess);
    
    }

$('#trip-submit').on("click", scheduleTrip);
$('#favorite-site').on("click", favoriteSite);

//get emails from list

function getAttendeeEmails(){
  var emailList = [];
  attendees = $('.mdb-select option');
  for (i=0; i<attendees.length; i++){
    if (attendees[i].selected){
      emailList.push(attendees[i].value);
    }
  }
  return emailList;
}


//Commenting functionality

function showCommentSuccess(result){
  console.log(result);
  var div = $('<div class="media mb-4 yessir"> </div>');
  var img = $('<img class="d-flex mr-3 rounded-circle" src="data:image/png;base64,'+ result.profile_photo + '" alt="">');
  var div2 = $('<div class="media-body"> </div>');
  var comment_names = $('<h5 class="mt-0">' + result.commenter_fname + ' ' + result.commenter_lname +'</h5>');
  var comment_string = $('<div>' + result.comment+ '</div>');
  $(div).append(img);
  $(div2).append(comment_names);
  $(div2).append(comment_string);
  $(div).append(div2);

  $('#comment-section').append(div);


}


function postComment(evt){
  console.log("1");
  var formInputs = {
      "comment": $("#comment").val(),
      "site_id" : window.location.pathname.slice(7)

  };

  $.post("/post-comment", 
       formInputs,
       showCommentSuccess);

}

$('#comment-submit').on("click", postComment);



// Javascript for the trip details page

function showCancelSuccess(result){
    $('#success-message').text(result);
}


function cancelTrip(evt){
    evt.preventDefault(); 
    window.alert("Are you sure you want to cancel this trip?"); 

    var formInput = {
      'path' : window.location.pathname.slice(14)
    }

    $.post('/cancel-trip',
          formInput, 
          showCancelSuccess);

}


$("#cancel-trip").on("click", cancelTrip);

//submit photo


function submitForm(){
    $('#image-form').submit();
 }


function filePicker(evt){
  $('#image').click();
}

$('.fa-upload').on("click", filePicker);
