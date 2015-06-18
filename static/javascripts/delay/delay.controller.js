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


        $scope.delay = 0;

        $scope.nox = function() {
            $scope.labels = _.keys($scope.spec.Nitrogen_X_Dry);
            $scope.series = ['NOx', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_X_Dry), _.values($scope.spec.Engine_Torque)];
        };
        $scope.ch4 = function() {
            $scope.labels = _.keys($scope.spec.Methane_Wet).splice(50, 100);
            $scope.series = ['CH4', 'Torque'];
            $scope.data = [_.values($scope.spec.Methane_Wet).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
        };
        $scope.co = function() {
            $scope.labels = _.keys($scope.spec.Carbon_Monoxide_High_Dry);
            $scope.series = ['CO', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Monoxide_High_Dry), _.values($scope.spec.Engine_Torque)];
        };
        $scope.co2 = function() {
            $scope.labels = _.keys($scope.spec.Carbon_Dioxide_Dry);
            $scope.series = ['CO2', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Dioxide_Dry), _.values($scope.spec.Engine_Torque)];
        };
        $scope.o2 = function() {
            $scope.labels = _.keys($scope.spec.Oxygen_Dry);
            $scope.series = ['O2', 'Torque'];
            $scope.data = [_.values($scope.spec.Oxygen_Dry), _.values($scope.spec.Engine_Torque)];
        };
        $scope.no = function() {
            $scope.labels = _.keys($scope.spec.Nitrogen_Monoxide_Dry);
            $scope.series = ['NO', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_Monoxide_Dry), _.values($scope.spec.Engine_Torque)];
        };
        $scope.maf = function() {
            $scope.labels = _.keys($scope.spec.Air_Flow_Rate);
            $scope.series = ['MFRAIR', 'Torque'];
            $scope.data = [_.values($scope.spec.Air_Flow_Rate), _.values($scope.spec.Engine_Torque)];
        };
        $scope.thc = function() {
            $scope.labels = _.keys($scope.spec.Total_Hydrocarbons_Wet);
            $scope.series = ['THC', 'Torque'];
            $scope.data = [_.values($scope.spec.Total_Hydrocarbons_Wet), _.values($scope.spec.Engine_Torque)];
        };

        $scope.left = function() {


            var right = _.values($scope.spec.Methane_Wet).splice((150 + $scope.delay), 50);
            var left = _.values($scope.spec.Methane_Wet).splice(0, (50 + $scope.delay));
            var data = _.values($scope.spec.Methane_Wet).splice((50 + $scope.delay), 100);

            $scope.delay++;

            var item = data.shift();
            left.push(item)
            var item = right.shift();
            data.push(item);

            $scope.series = ['Species', 'Torque'];
            $scope.data = [data, _.values($scope.spec.Engine_Torque).splice(50, 100)];
            console.log($scope.delay);

        };
        $scope.right = function() {

            var right = _.values($scope.spec.Methane_Wet).splice((150 + $scope.delay), 50);
            var left = _.values($scope.spec.Methane_Wet).splice(0, (50 + $scope.delay));
            var data = _.values($scope.spec.Methane_Wet).splice((50 + $scope.delay), 100);

            $scope.delay--;

            var item = data.pop();
            right.unshift(item);
            var item = left.pop();
            data.unshift(item);

            $scope.series = ['Species', 'Torque'];
            $scope.data = [data, _.values($scope.spec.Engine_Torque).splice(50, 100)];
            console.log($scope.delay);

        };



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


        var createWindow = function() {









        };



        read();


    }

})();
