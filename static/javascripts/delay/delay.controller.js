(function() {
    'use strict';

    angular
        .module('TestSite.delay.controllers')
        .controller('DelayController', DelayController);

    DelayController.$inject = ['$scope', '$http', 'toastr'];
    /**
     * @namespace UploadController
     */
    function DelayController($scope, $http, toastr) {


        $scope.delay = 0;
        $scope.CH4Delay = $scope.NOxDelay = $scope.CODelay  = $scope.CO2Delay = $scope.O2Delay = $scope.NODelay = $scope.MAFDelay = $scope.THCDelay = 0;
        $scope.currentSpec = "Nitrogen_X_Dry";
        $scope.save = {'NOx':0,'CH4':0,'CO':0,'CO2':0,'O2':0,'NO':0,'MFRAIR':0,'THC':0}

        $scope.nox = function() {            
            $scope.series = ['NOx', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.labels = _.keys($scope.spec.Nitrogen_X_Dry).splice(50+$scope.currentDelay, 100);
            $scope.data = [_.values($scope.spec.Nitrogen_X_Dry).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Nitrogen_X_Dry;            
            $scope.apply
        };
        $scope.ch4 = function() {
            $scope.series = ['CH4', 'Torque'];            
            $scope.currentDelay = $scope.save[$scope.series[0]];            
            $scope.labels = _.keys($scope.spec.Methane_Wet).splice(50+$scope.currentDelay, 100);
            $scope.data = [_.values($scope.spec.Methane_Wet).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Methane_Wet;

            $scope.apply
        };
        $scope.co = function() {
            $scope.series = ['CO', 'Torque'];            
            $scope.currentDelay = $scope.save[$scope.series[0]];            
            $scope.labels = _.keys($scope.spec.Carbon_Monoxide_High_Dry).splice(50+$scope.currentDelay, 100);
            $scope.data = [_.values($scope.spec.Carbon_Monoxide_High_Dry).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Carbon_Monoxide_High_Dry;
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply

        };
        $scope.co2 = function() {
            $scope.series = ['CO2', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];              
            $scope.labels = _.keys($scope.spec.Carbon_Dioxide_Dry).splice(50+$scope.currentDelay, 100);          
            $scope.data = [_.values($scope.spec.Carbon_Dioxide_Dry).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Carbon_Dioxide_Dry;
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply

        };
        $scope.o2 = function() {
            $scope.series = ['O2', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];             
            $scope.labels = _.keys($scope.spec.Oxygen_Dry).splice(50+$scope.currentDelay, 100);           
            $scope.data = [_.values($scope.spec.Oxygen_Dry).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Oxygen_Dry;
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply

        };
        $scope.no = function() {
            $scope.series = ['NO', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];              
            $scope.labels = _.keys($scope.spec.Nitrogen_Monoxide_Dry).splice(50+$scope.currentDelay, 100);          
            $scope.data = [_.values($scope.spec.Nitrogen_Monoxide_Dry).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Nitrogen_Monoxide_Dry;
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply

        };
        $scope.maf = function() {
            $scope.series = ['MFRAIR', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];                  
            $scope.labels = _.keys($scope.spec.Air_Flow_Rate).splice(50+$scope.currentDelay, 100);      
            $scope.data = [_.values($scope.spec.Air_Flow_Rate).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Air_Flow_Rate;
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply

        };
        $scope.thc = function() {
            $scope.series = ['THC', 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];             
            $scope.labels = _.keys($scope.spec.Total_Hydrocarbons_Wet).splice(50+$scope.currentDelay, 100);           
            $scope.data = [_.values($scope.spec.Total_Hydrocarbons_Wet).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec.Total_Hydrocarbons_Wet
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.apply
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
            $scope.save[$scope.series[0]] = $scope.currentDelay

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
            $scope.save[$scope.series[0]] = $scope.currentDelay

        };

        $scope.Submit = function(){

            $http.post('/api/v1/data/delay/',{'delay':$scope.save})
                .success(function(response) {
                    toastr.success('Delay submitted!');
                    location.href = '/1065/results'

                })
                .error(function(response) {
                    toastr.error(response.message, 'Delay submission failed!');                    
                });
        }

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

                    //$scope.series = ['NOx', 'Torque'];
                    //$scope.labels = _.keys($scope.spec.Nitrogen_X_Dry).splice(50, 100);
                    //$scope.data = [_.values($scope.spec.Nitrogen_X_Dry).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
                    //$scope.currentSpec = $scope.spec.Nitrogen_X_Dry;            
                    //$scope.apply

                })
                .error(function(response) {
                    toastr.error(response.message, 'Prepartion for Delay failed!');
                });
        };

        read();

    }

})();
