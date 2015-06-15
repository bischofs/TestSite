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

        $scope.nox = function() {

            $scope.labels = _.keys($scope.spec.Nitrogen_X_Dry);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_X_Dry), _.values($scope.spec.Engine_Torque)];

        };
        $scope.ch4 = function() {

            $scope.labels = _.keys($scope.spec.Methane_Wet);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Methane_Wet), _.values($scope.spec.Engine_Torque)];

        };
        $scope.co = function() {

            $scope.labels = _.keys($scope.spec.Carbon_Monoxide_High_Dry);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Monoxide_High_Dry), _.values($scope.spec.Engine_Torque)];

        };
        $scope.co2 = function() {

            $scope.labels = _.keys($scope.spec.Carbon_Dioxide_Dry);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Dioxide_Dry), _.values($scope.spec.Engine_Torque)];

        };
        $scope.o2 = function() {

            $scope.labels = _.keys($scope.spec.Oxygen_Dry);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Oxygen_Dry), _.values($scope.spec.Engine_Torque)];

        };
        $scope.no = function() {

            $scope.labels = _.keys($scope.spec.Nitrogen_Monoxide_Dry);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_Monoxide_Dry), _.values($scope.spec.Engine_Torque)];

        };

        $scope.maf = function() {

            $scope.labels = _.keys($scope.spec.Air_Flow_Rate);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Air_Flow_Rate), _.values($scope.spec.Engine_Torque)];

        };
        $scope.thc = function() {

            $scope.labels = _.keys($scope.spec.Total_Hydrocarbons_Wet);
            $scope.series = ['Species', 'Torque'];
            $scope.data = [_.values($scope.spec.Total_Hydrocarbons_Wet), _.values($scope.spec.Engine_Torque)];

        };

     $scope.forward = function() {


            $scope.series = ['Species', 'Torque'];


        };
     $scope.back = function() {


            $scope.series = ['Species', 'Torque'];


        };




        $scope.read = function() {

            $http.get('/api/v1/data/delay/')

            .success(function(data) {
                var spec = JSON.parse(data)
                $scope.spec = spec
                $scope.options = {
                    pointDot: false,
                    showTooltips: false
                };
                $scope.labels = _.keys(spec.Methane_Wet);
                $scope.series = ['Species', 'Torque'];
                $scope.data = [_.values(spec.Methane_Wet), _.values(spec.Engine_Torque)];

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
