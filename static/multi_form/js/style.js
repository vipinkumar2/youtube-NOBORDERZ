// Script for multi step form start
user_id = $("#user_id").val()
if (user_id=="None"){
var response;
$.validator.addMethod(
    "validName",
    function(value, element) {
        $.ajax({
          type: "GET",
          url: check_account,
          data: "username="+$("#userName").val(),
          async:false,
          dataType: 'json',
          success: function(data)
          {
            response = data.status

           }
       });
       return this.optional(element) || (response===false);
    },
    "Username is Already Taken"
);
$.validator.addMethod(
    "validEmail",
    function(value, element) {
        $.ajax({
          type: "GET",
          url: check_account,
          data: "email="+$("#userEmail").val(),
          dataType: 'json',
          async:false,
          success: function(data)
          {
            response = data.status
            if (!response){
                $("#verify_email").prop('disabled', false);
            }
           }
       });
       return this.optional(element) || (response===false);
    },
    "Email is Already Taken or Invalid"
);
}else{
var response;
$.validator.addMethod(
    "validName",
    function(value, element) {
        return true;
    },
    "Username is Already Taken"
);
$.validator.addMethod(
    "validEmail",
    function(value, element) {
        return true;
    },
    "Email is Already Taken or Invalid"
);
}
$.validator.addMethod(
    "validInstaAccount",
    function(value, element) {
        $.ajax({
          type: "GET",
          url: check_account,
          data: "account="+$("#instaAccount").val(),
          dataType: 'json',
          async:false,
          success: function(data)
          {
            response = data.status
           }
       });
       return this.optional(element) || (response===false);
    },
    "Instagram Account is Already Used by Other User"
);


var is_async_step = false;
$(document).ready(function ()
{

    var response = false;
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function show_messages(data){

    }

    // initilized form
    var form = $("#multistep-form")
    form.validate({



        errorPlacement: function errorPlacement(error, element) { element.before(error); },
        rules: {
            user_cpassword: {
                equalTo: "#userPassword"
            },
            user_name: {
                validName: true
            },
            user_email: {
                validEmail: true
            },
            insta_account: {
                validInstaAccount: true
            }
        },
        messages: {
            user_name: {
                required: "Name is a required field.",
            },
            user_email: {
                required: "Email is a required field.",
            },
            timezone:{
                required: "Timezone is a required field,",
            },
            user_password: {
                required: "Password is a required field.",
            },
            user_cpassword: {
                required: "Confirm Password is a required field.",
            },

        }
    });

    form.children("div").steps({
        headerTag: "h3",
        bodyTag: "section",
        transitionEffect: "slideLeft",
        onStepChanging: function(event, currentIndex, newIndex){
         // Used to skip the "Warning" step if the user is old enough.
         form.validate().settings.ignore = ":disabled,:hidden";
         var is_valid = form.valid();
         var response = false
        // $("#loading-overplay").show();
        if (currentIndex > newIndex){
            return false;
        }

        if (is_valid){
            $(".section-description").removeClass("success")
            $(".section-description").removeClass("error")
            $(".section-description").html("Please wait we are processing your details.");
        }


            if (currentIndex === 0 && is_valid)
            {
              user_id = $("#user_id").val()
              verified = $("#verify_email").html();
              if(verified==="Verified"){
                var data = {
                "username": $('#userName').val(),
                "email": $('#userEmail').val(),
                "password": $('#userPassword').val(),
                "cpassword": $('#confirmPassword').val(),
                "timezone": $("#timezone").val(),
                "language":$("#user_language").val()
                }
                if(user_id=="None"){
              $("#loading-overplay").show();
                  $.ajax({
                      type: "POST",
                      headers: { "X-CSRFToken": csrftoken },
                      url: create_user,
                      data: data,
                      dataType: 'json',
                      async: false,
                      cache: false,
                      beforeSend: function () { $('#loading-overplay').show(); },
                      success: function(data, status, xhr){
                          $("#loading-overplay").hide();
                          // $("#loading-overplay").css("display", "none")
                          if (data.status){
                              $(".section-description").removeClass("error")
                              $(".section-description").addClass("success")
                          }else{
                              $(".section-description").removeClass("success")
                              $(".section-description").addClass("error")
                          }
                          $(".section-description").html(data.message);
           
                          if (data.status){
                              $('#user_id').val(data.user_id);
                                $("#loading-overplay").show();
                                
                                setTimeout(function () {
                                  $("#loading-overplay").hide();
                            }, 2000); 

                              is_async_step = true;
                              response = true
                              console.log(true)
                             
                              return true
                          }
                      },
                      error: function (jqXhr, textStatus, errorMessage) {
                          $("#loading-overplay").hide();
                          return false;
                      },
                  });
                  }else{
                    $(".section-description").html("Please fill instagram details.");
                    $(".section-description").removeClass("error")
                    return true;
                  }
                }else{
                  $(".section-description").addClass("error")
                  $(".section-description").html("Please verify your email.");
                }
            } else if (currentIndex === 1 && is_valid)
            {
                $("#loading-overplay").show();

                var data = {
                "user_id": $('#user_id').val(),
                "insta_account": $('#instaAccount').val(),
                "insta_password": $('#instaPassword').val(),
                "insta_account_about": $('#instaAccountAbout').val(),
                "insta_country": $('#instaCountry').val(),
                }
                $.ajax({
                    type: "POST",
                    url: add_instagram_account,
                    data: data,
                    dataType: 'json',
                    async: false,
                    cache: false,
                    beforeSend: function () { setTimeout($('#loading-overplay').show(), 100) },
                    success: function(data, status, xhr){
                        $("#loading-overplay").hide();
                        // $("#loading-overplay").css("display", "none")
                        if (data.status){
                            $(".section-description").removeClass("error")
                            $(".section-description").addClass("success")
                        }else{
                            $(".section-description").removeClass("success")
                            $(".section-description").addClass("error")
                        }
                        $(".section-description").html(data.message);
                        if (data.status){
                            $('#useraccount_id').val(data.useraccount_id);
                            is_async_step = true;
                            //trigger navigation event
                            response = true
                            response_data = data

                            return true
                        }
                    },
                    error: function (jqXhr, textStatus, errorMessage) {
                        $("#loading-overplay").hide();
                        return false;
                    },
                    complete:function(data){
                    $("#oading-overplay").hide();
                   }
                });
            }
            if (is_valid && response){
                return true
            }
            else{
                return false
            }
        },
        onStepChanged: function (event, currentIndex, priorIndex)
        {
            if (currentIndex > priorIndex){
                form.steps("previous");
            }else{
                
                form.steps("next")
            }
        },
        onFinished: function (event, currentIndex)
        {
//            $("#loading-overplay").show();
            var data = {
                    "useraccount_id": $('#useraccount_id').val(),
//                    "targetAudience": $('#targetAudience').val(),
//                    "targetArea": $('#targetArea').val(),
//                    "targetGender": $('#targetGender').val(),
                    "yourCompetitors": $('#yourCompetitors').val(),
                }
                // $("#loading-overplay").css("display", "block")
                $.ajax({
                    beforeSend: function () { $('#loading-overplay').show(); },
                    type: "POST",
                    headers: { "X-CSRFToken": csrftoken },
                    url: add_user_target,
                    data: data,
                    dataType: 'json',
                    async: false,
                    cache: false,
                    success: function(data, status, xhr){
                        // $("#loading-overplay").css("display", "none")
                        $("#loading-overplay").hide();
                        if (data.status){
                            $(".section-description").removeClass("error")
                            $(".section-description").addClass("success")
                        }else{
                            $(".section-description").removeClass("success")
                            $(".section-description").addClass("error")
                        }
                        $(".section-description").html(data.message);
                        if (data.status){
                            is_async_step = true;
                            //trigger navigation event

                            setTimeout(function(){
                                window.location.href = "/quick/";
                            }, 5000)
                            return true
                        }
                    },
                    error: function (jqXhr, textStatus, errorMessage) {
                        $("#loading-overplay").hide();
                        return false;
                    },
                });
        }
    });

});

jQuery('document').ready(function() {

    // Five Item Slider
    jQuery('.slickFiveItems').slick({
        infinite: true,
        speed: 300,
        slidesToShow: 4,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
      responsive: [
        {
          breakpoint: 1366,
          settings: {
            slidesToShow: 5,
            slidesToScroll: 1,
          }
        },
         {
          breakpoint: 1000,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 1,
          }
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 480,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
      ]
    });

    // Three Item Slider
    jQuery('.slickThreeItems').slick({
        dots:true,
        infinite: true,
        speed: 300,
        slidesToShow: 3,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 2000,
      responsive: [
         {
          breakpoint: 1000,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 1,
          }
        },
        {
          breakpoint: 600,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2
          }
        },
        {
          breakpoint: 480,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1
          }
        }
      ]
    });
});
// store data post and session onclick next
  $("#multistep-form ul li").on( 'click', function(){
    var nextInfo = $(this).find('a').attr('href');
    if(nextInfo == '#finish'){
        step_form_submit('next');
        $("#multistep-form").submit()
    }
  });

jQuery('document').ready(function() {
    $("#verify_email").prop('disabled', true);
    user_id = $("#user_id").val()
    if (user_id!="None"){
      $("a").click()
    }
    $('#multistep-form input[type=text]').on('keypress', function(e) {
        if (e.which == 32)
            return false;
    });

    $(".lung-dropdown .dropdown-menu li a").click(function(){
      $(this).parents(".dropdown").find('.btn').html($(this).html());
      $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    });


})

$(document).on('click', "#verify_email", function(e){
  e.preventDefault();
  email = $('#userEmail').val()
  if (email){
    $("#loading-overplay").show();
  $.ajax({
      type: "GET",
      url: send_verification_email,
      data: "email="+email,
      async:false,
      dataType: 'json',
      success: function(data)
      {
        if (data.status){
          $("#initModal").modal('show');
          $("#wrong_otp").addClass('hide');
          $("#send_otp").addClass('hide');
        }
       }
   });
   $("#loading-overplay").hide();
  }
})

$(document).on('click', "#resend_otp", function(e){
  e.preventDefault();
  $("#send_otp").addClass('hide');
  email = $('#userEmail').val()
  otp = $("#verify_otp").val()
  if (email){
    $("#loading-overplay").show();
  $.ajax({
      type: "GET",
      url: send_verification_email,
      data: "email="+email,
      async:false,
      dataType: 'json',
      success: function(data)
      {
        if (data.status){
          $("#wrong_otp").addClass('hide');
          $("#send_otp").removeClass('hide');
          $("#resend_otp_msg").show();
        }else{
          $("#wrong_otp").removeClass('hide');
        }
      setTimeout(function(){ $("#resend_otp_msg").hide(); }, 10000);
    $("#loading-overplay").hide();
 
       }

   });
   $("#loading-overplay").hide();
  }
})
$(document).on("change", "#userEmail", function(){
    $("#verify_email").html("Verify");
})
// $(document).on('click', "#resend_otp", function(e){
//   var popup1 = document.getElementById("popup-1")
//   var openPopup1 = document.getElementById("open-popup-1")
//   $("#wrong_otp").addClass('hide');
//   $("#send_otp").addClass('hide');
  
//   email = $('#userEmail').val()
//   otp = $("#verify_otp").val()
  
//   if (email) {
//     $("#loading-overplay").show();
//   $.ajax({
//       type: "GET",
//       url: send_verification_email,
//       data: "email="+email,
//       async:false,
//       dataType: 'json',
//       success: function(data)
//       {
//         if (data.status){
//           $("#wrong_otp").addClass('hide');
//           $("#send_otp").removeClass('hide');
//           $("#resend_otp_msg").show();
//             }
//         else{
//           $("#wrong_otp").removeClass('hide');
//         }
//        }
//    });
//    setTimeout(function(){ $("#resend_otp_msg").hide(); }, 10000);
//     $("#loading-overplay").hide();
//   }
// })
// $('.cancel-icon').click(function () {
//   $('#popup-1').fadeOut('slow');
//     //Close the popup  
// });

$(document).on('click', "#verify_otp_btn", function(e){
  e.preventDefault();
  $("#send_otp").addClass('hide');
  email = $('#userEmail').val()
  otp = $("#verify_otp").val()
  if (email && otp){
    $("#loading-overplay").show();
  $.ajax({
      type: "GET",
      url: verify_otp,
      data: "email="+email+"&otp="+otp,
      async:false,
      dataType: 'json',
      success: function(data)
      {
        if (data.status){
          $("#wrong_otp").addClass('hide');
          $("#verify_email").html("Verified");
          $("#verify_otp").val("");
          $("#verify_email").prop('disabled', true);
          $("#initModal").modal('hide');
        }else{
          $("#wrong_otp").removeClass('hide');
        }
       }
   });
   $("#loading-overplay").hide();
  }
})
$(document).on("change", "#userEmail", function(){
    $("#verify_email").html("Verify");
})
$(document).on("change", "#instaAbout", function(){
  if(this.value==="Other"){
    $('#instaAccountAbout').removeClass("hide")
    $('#instaAccountAbout').val("")
  }else{
    $('#instaAccountAbout').addClass("hide")
    $('#instaAccountAbout').val(this.value)
  }
})