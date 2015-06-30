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
        $scope.CH4Delay = $scope.NOxDelay = $scope.CODelay  = $scope.CO2Delay = $scope.O2Delay = $scope.NODelay = $scope.MAFDelay = $scope.THCDelay = 0;
        $scope.currentSpec = "Nitrogen_X_Dry";

        $scope.nox = function() {
            $scope.labels = _.keys($scope.spec.Nitrogen_X_Dry).splice(50, 100);
            $scope.series = ['NOx', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_X_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Nitrogen_X_Dry;
            $scope.currentDelay = $scope.NOxDelay;
        };
        $scope.ch4 = function() {
            $scope.labels = _.keys($scope.spec.Methane_Wet).splice(50, 100);
            $scope.series = ['CH4', 'Torque'];
            $scope.data = [_.values($scope.spec.Methane_Wet).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Methane_Wet;
            $scope.currentDelay = $scope.CH4Delay;
        };
        $scope.co = function() {
            $scope.labels = _.keys($scope.spec.Carbon_Monoxide_High_Dry).splice(50, 100);
            $scope.series = ['CO', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Monoxide_High_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Carbon_Monoxide_High_Dry;
            $scope.currentDelay = $scope.CODelay;

        };
        $scope.co2 = function() {
            $scope.labels = _.keys($scope.spec.Carbon_Dioxide_Dry).splice(50, 100);
            $scope.series = ['CO2', 'Torque'];
            $scope.data = [_.values($scope.spec.Carbon_Dioxide_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Carbon_Dioxide_Dry;
            $scope.currentDelay = $scope.CO2Delay;

        };
        $scope.o2 = function() {
            $scope.labels = _.keys($scope.spec.Oxygen_Dry).splice(50, 100);
            $scope.series = ['O2', 'Torque'];
            $scope.data = [_.values($scope.spec.Oxygen_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Oxygen_Dry;
            $scope.currentDelay = $scope.O2Delay;

        };
        $scope.no = function() {
            $scope.labels = _.keys($scope.spec.Nitrogen_Monoxide_Dry).splice(50, 100);
            $scope.series = ['NO', 'Torque'];
            $scope.data = [_.values($scope.spec.Nitrogen_Monoxide_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Nitrogen_Monoxide_Dry;
            $scope.currentDelay = $scope.NODelay;

        };
        $scope.maf = function() {
            $scope.labels = _.keys($scope.spec.Air_Flow_Rate).splice(50, 100);
            $scope.series = ['MFRAIR', 'Torque'];
            $scope.data = [_.values($scope.spec.Air_Flow_Rate).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Air_Flow_Rate;
            $scope.currentDelay = $scope.MAFDelay;

        };
        $scope.thc = function() {
            $scope.labels = _.keys($scope.spec.Total_Hydrocarbons_Wet).splice(50, 100);
            $scope.series = ['THC', 'Torque'];
            $scope.data = [_.values($scope.spec.Total_Hydrocarbons_Wet).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Total_Hydrocarbons_Wet
            $scope.currentDelay = $scope.THCDelay;
        };

        $scope.left = function() {


            var right = _.values($scope.currentSpec).splice((150 + $scope.currentDelay), 50);
            var left = _.values($scope.currentSpec).splice(0, (50 + $scope.currentDelay));
            var data = _.values($scope.currentSpec).splice((50 + $scope.currentDelay), 100);

            $scope.currentDelay++;

            var item = data.shift();
            left.push(item);
            var item = right.shift();
            data.push(item);

            $scope.data = [data, _.values($scope.spec.Engine_Torque).splice(50, 100)];

        };
        $scope.right = function() {

            var right = _.values($scope.currentSpec).splice((150 + $scope.currentDelay), 50);
            var left = _.values($scope.currentSpec).splice(0, (50 + $scope.currentDelay));
            var data = _.values($scope.currentSpec).splice((50 + $scope.currentDelay), 100);

            $scope.currentDelay--;

            var item = data.pop();
            right.unshift(item);
            var item = left.pop();
            data.unshift(item);

            $scope.data = [data, _.values($scope.spec.Engine_Torque).splice(50, 100)];

        };



        var read = function() {
            $http.get('/1065/api/v1/data/delay/')
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
