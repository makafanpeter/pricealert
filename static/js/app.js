var ViewModel = function () {
   self = this;

   self.url = ko.observable();

   self.product = ko.observable();

   self.loading = ko.observable(false);

   self.error = ko.observable(false);

   self.crawlUrl = function () {
          var jsonObj = JSON.stringify(ko.toJS({ url: self.url }), null, 2);

          var jqxhr = $.ajax({
              type: 'POST',
              url: "/crawl",
              contentType: 'application/json; charset=utf-8',
              data: jsonObj,
              dataType: "json",
              beforeSend: function () {
                self.error(false);
                self.loading(true);
                self.product(null);
              },
              statusCode: {
                  409: function (xhr) {

                  },
                  200: function (xhr) {
                      var message = xhr.responseText;
                      self.getProduct(message);
                  },
                  500: function (xhr) {
                    self.error(true);
                    self.loading(false);
                  },
                  400: function (xhr) {
                    self.error(true);
                    self.loading(false);
                  },
                  417: function (xhr) {
                    self.error(true);
                    self.loading(false);
                  }
              },
              complete: function () {

              }
          });
        }

        self.getProduct = function (jobId) {
              var timeout = "";
              var poller = function(){
                var jqxhr = $.ajax({
                    type: 'GET',
                    url: "/results/"+jobId,
                    beforeSend: function () {
                    },
                    success: function (data, statusCode,jqXHR) {

                        if (jqXHR.status === 202) {
                           console.log(data);
                        }
                        else if (jqXHR.status === 200) {
                             self.product(data);
                             self.url("");
                             self.loading(false);
                             self.error(false);
                             clearTimeout(timeout);
                             return false;
                        }
                        timeout = setTimeout(poller, 2000);
                    },
                    error: function (error) {
                       self.error(true);
                       self.loading(false);
                       console.log(error)
                    }
                });
              }

                poller();
        }
};

$(document).ready(function () {
    ko.applyBindings(new ViewModel());
    $(".button-collapse").sideNav();
});
