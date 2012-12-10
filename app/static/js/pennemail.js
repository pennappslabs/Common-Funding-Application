// Generated by CoffeeScript 1.4.0
(function() {

  $(function() {
    $("label[for=id_email]").html("Penn Email Address:");
    $("#register-form").on("submit", function(e) {
      var email, pattern;
      email = $("#id_email").val();
      pattern = /@.*upenn\.edu$/;
      if (!pattern.test(email)) {
        $("#id_email").addClass("email-error");
        return e.preventDefault();
      }
    });
    return $("#id_email").on("keyup", function() {
      return $(this).removeClass("email-error");
    });
  });

}).call(this);
