(function() {
    'use strict';

    angular
        .module('TestSite.results.controllers')
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = ['$scope', '$http', 'toastr'];
    /**
     * @namespace UploadController
     */
    function ResultsController($scope, $http, toastr) {

        var read = function() {
            $http.get('/api/v1/data/delay/')
                .success(function(data) {
                    var spec = JSON.parse(data)
                    $scope.spec = spec
                    $scope.options = {
                        pointDot: false,
                        showTooltips: false
                    };
                    $scope.series = ['Species', 'Torque'];
                    createWindow();

                })
                .error(function(data, status, headers, config) {
                    throw new Error('Something went wrong with reading data');
                });

        };


        read();


    }

})();
