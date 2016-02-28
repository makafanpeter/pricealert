var ViewModel = function() {
  self = this;

  self.url = ko.observable();

  self.product = ko.observable();

  self.loading = ko.observable(false);

  self.error = ko.observable(false);

  self.alerts = ko.observableArray([]);

  self.targetPrice = ko.observable(0);

  self.tweetAt = ko.observable("");

  self.productLoaded = ko.observable(false);

  self.processingAlert = ko.observable(false);

  self.crawlUrl = function() {
    var jsonObj = JSON.stringify(ko.toJS({
      url: self.url
    }), null, 2);

    var jqxhr = $.ajax({
      type: 'POST',
      url: "/crawl",
      contentType: 'application/json; charset=utf-8',
      data: jsonObj,
      dataType: "json",
      beforeSend: function() {
        self.error(false);
        self.loading(true);
        self.product(null);
        self.productLoaded(false);
        self.targetPrice(0);
      },
      statusCode: {
        409: function(xhr) {

        },
        200: function(xhr) {
          var message = xhr.responseText;
          self.getProduct(message);
        },
        500: function(xhr) {
          self.error(true);
          self.loading(false);
        },
        400: function(xhr) {
          self.error(true);
          self.loading(false);
        },
        417: function(xhr) {
          self.error(true);
          self.loading(false);
        }
      },
      complete: function() {

      }
    });
  }

  self.getProduct = function(jobId) {
    var timeout = "";
    var poller = function() {
      var jqxhr = $.ajax({
        type: 'GET',
        url: "/results/" + jobId,
        beforeSend: function() {},
        success: function(data, statusCode, jqXHR) {

          if (jqXHR.status === 202) {
            console.log(data);
          } else if (jqXHR.status === 200) {
            self.product(data);
            self.url("");
            self.loading(false);
            self.error(false);
            self.targetPrice(data.price + 1)
            clearTimeout(timeout);
            return false;
          }
          timeout = setTimeout(poller, 2000);
        },
        error: function(error) {
          self.error(true);
          self.loading(false);
          console.log(error)
        }
      });
    }

    poller();
  };

  self.EnableAlert = function() {
    //alert("hello");
    console.log(self.product());
    self.productLoaded(true);
  };

  self.createAlert = function() {
      self.processingAlert(true);
      var jsonObj = JSON.stringify(ko.toJS({
        targetPrice: self.targetPrice,
        tweetAt: self.tweetAt,
      }), null, 2);
      productId = self.product().id;
      var jqxhr = $.ajax({
        type: 'POST',
        url: "/createalert/"+productId,
        contentType: 'application/json; charset=utf-8',
        data: jsonObj,
        dataType: "json",
        beforeSend: function() {
          self.processingAlert(true);
        },
        success: function(data, statusCode, jqXHR) {
          self.processingAlert(false);
          Materialize.toast('Alert Created.',5000);
          self.productLoaded(false);
          self.getAlerts();

        },
        error: function(error) {
          self.processingAlert(false);
          Materialize.toast('Unable to create Alert.',5000);

        }
      });
  };

  self.getAlerts = function() {
    $.getJSON("myalerts", function(data) {
      var alerts = data.alerts;
      self.alerts(alerts);
    });
  };
  self.getAlerts();
};

$(document).ready(function() {
  ko.applyBindings(new ViewModel());
  $(".button-collapse").sideNav();

  $('.dropdown-button').dropdown({
    inDuration: 300,
    outDuration: 225,
    constrain_width: false, // Does not change width of dropdown to that of the activator

    belowOrigin: true, // Displays dropdown below the button
    alignment: "right" // Displays dropdown with edge aligned to the left of button
  });
});
