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

var formInputs = {
    "date": $("#datepicker").val(),
    "email": $("#attendee-email").val(),
    'path' : window.location.pathname.slice(7)
};

$.post("/trip", 
     formInputs,
     showTripSuccess);

}

$('#trip-submit').on("click", scheduleTrip);
$('#favorite-site').on("click", favoriteSite);



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