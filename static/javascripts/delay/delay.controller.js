(function() {
    'use strict';

    angular
        .module('TestSite.delay.controllers')
        .controller('DelayController', DelayController);

    DelayController.$inject = ['$scope', '$http', 'toastr', '$location'];
    /**
     * @namespace UploadController
     */
    function DelayController($scope, $http, toastr, $location) {

        $scope.Array = {'NOx':'Nitrogen_X_Dry','CH4':'Methane_Wet','THC':'Total_Hydrocarbons_Wet','CO':'Carbon_Monoxide_Dry','CO2':'Carbon_Dioxide_Dry','O2':'Oxygen_Dry','NO':'Nitrogen_Monoxide_Dry','MFRAIR':'Air_Flow_Rate'}
        read();

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

            $http.post('/1065/api/v1/data/delay/',{'delay':$scope.save})
                .success(function(response) {
                    toastr.success('Delay submitted!');
                    $location.path('/1065/evaluation/results');

                })
                .error(function(response) {
                    toastr.error(response.message, 'Delay submission failed!');                    
                });
        }


        function read() {
            $http.get('/1065/api/v1/data/delay/')
                .success(function(data) {
                    
                    $scope.spec = JSON.parse(data.DelaySpecies)
                    $scope.save = data.Array
                    $scope.options = {
                        pointDot: false,
                        showTooltips: false
                    };

                    $scope.series = ['NOx', 'Torque'];
                    $scope.currentDelay = $scope.save[$scope.series[0]];
                    $scope.labels = _.keys($scope.spec[$scope.Array['NOx']]).splice(50+data.Array['NOx'], 100);
                    $scope.data = [_.values($scope.spec[$scope.Array['NOx']]).splice(50+data.Array['NOx'], 100), _.values($scope.spec.Engine_Torque).splice(50, 100)];
                    $scope.currentSpec = $scope.spec[$scope.Array['NOx']];            
                    toastr.success('Prepartion for Delay finished!');            
                })
                .error(function(response) {
                    toastr.error(response.message, 'Prepartion for Delay failed!');
                });
        };

    }

})();
