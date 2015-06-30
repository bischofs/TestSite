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
        $scope.save = {'NOx':0,'CH4':0,'THC':0,'CO':0,'CO2':0,'O2':0,'NO':0,'MFRAIR':0}
        $scope.Array = {'NOx':'Nitrogen_X_Dry','CH4':'Methane_Wet','THC':'Total_Hydrocarbons_Wet','CO':'Carbon_Monoxide_High_Dry','CO2':'Carbon_Dioxide_Dry','O2':'Oxygen_Dry','NO':'Nitrogen_Monoxide_Dry','MFRAIR':'Air_Flow_Rate'}

        $scope.species = function() {

            $scope.series = [$scope.ChosenSpecies, 'Torque'];
            $scope.currentDelay = $scope.save[$scope.series[0]];
            $scope.labels = _.keys($scope.spec[$scope.Array[$scope.ChosenSpecies]]).splice(50+$scope.currentDelay, 100);
            $scope.data = [_.values($scope.spec[$scope.Array[$scope.ChosenSpecies]]).splice(50+$scope.currentDelay, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
            $scope.currentSpec = $scope.spec[$scope.Array[$scope.ChosenSpecies]];            
            $scope.apply;
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
            $scope.save[$scope.series[0]] = $scope.currentDelay;

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
            $scope.save[$scope.series[0]] = $scope.currentDelay;

        };

        $scope.submit = function(){

            $http.post('/api/v1/data/delay/',{'delay':$scope.save})
                .success(function(response) {
                    toastr.success('Delay submitted!');
                    location.href = '/1065/results';

                })
                .error(function(response) {
                    toastr.error(response.message, 'Delay submission failed!');                    
                });
        }

        $scope.read = function() {
            $http.get('/api/v1/data/delay/')
                .success(function(data) {
                    var spec = JSON.parse(data)
                    $scope.spec = spec
                    $scope.options = {
                        pointDot: false,
                        showTooltips: false
                    };

                    $scope.ChosenSpecies = 'NOx'
                    $scope.currentDelay = 0
                    $scope.series = ['NOx', 'Torque'];
                    $scope.labels = _.keys($scope.spec[$scope.Array[$scope.ChosenSpecies]]).splice(50, 100);
                    $scope.data = [_.values($scope.spec[$scope.Array[$scope.ChosenSpecies]]).splice(50, 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
                    $scope.currentSpec = $scope.spec[$scope.Array[$scope.ChosenSpecies]];            
                    $scope.apply;        
                    toastr.success('Prepartion for Delay finished!');            

                })
                .error(function(response) {
                    toastr.error(response.message, 'Prepartion for Delay failed!');
                });
        };

    }

})();
