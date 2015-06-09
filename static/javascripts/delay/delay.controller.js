(function() {
    'use strict';

    angular
    .module('TestSite.delay.controllers')
    .controller('DelayController', DelayController);

    DelayController.$inject = ['$scope', '$http'];
    /**
     * @namespace UploadController
     */
     function DelayController($scope, $http) {

        $scope.read = function() {

            $http.get('/api/v1/data/delay/')

            .success(function(data) {
                var spec = JSON.parse(data)
               $scope.options = { pointDot : false, showTooltips: false};
               $scope.labels = _.keys(spec.Oxygen_Dry);
               $scope.series = ['Species'];
               $scope.data = [_.values(spec.Oxygen_Dry)];

           })

            .error(function(data, status, headers, config) {

                throw new Error('Something went wrong with reading data');

            });

        };
        
        $scope.read();

        // $scope.labels = [12,123,123,123,123,123,123,123,123]//_.keys(spec.Oxygen_Dry)
        // $scope.series = ['Species'];
        // $scope.data = [123,123,123,123,123,1231,2312,3123,123]//_.values(spec.Oxygen_Dry)


        // $scope.onClick = function(points, evt) {
        //     console.log(points, evt);
        // };
        // var randomScalingFactor = function(scale) {
        //     return Math.round(Math.random() * scale)
        // };






    }

})();
