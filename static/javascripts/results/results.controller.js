(function() {
    'use strict';

    angular
        .module('TestSite.results.controllers')
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = ['$scope', '$http', 'toastr', 'infoboxService'];



    function ResultsController($scope, $http, toastr, cgBusy, infoboxService) {

        var ListSpecies = ['CO2','CO','NOX','THC','NMHC'];
        var ListFields = ['Name','Result','Unit','Total'];
        Start();

        $scope.Calculation = function() {

            $scope.delay = 0;
            $scope.minDuration = 0;
            $scope.message = 'Calculation Running...';
            $scope.backdrop = true;
            $scope.promise = null;

            toastr.info('Calculations started!');

            $scope.promise = $http.post('/1065/api/v1/data/calculations/')
                .success(function(response) {
                    toastr.success('Calculations finished!');
                    var jsonLog = JSON.parse(response)
                    var report = JSON.parse(jsonLog.Report)
                    var Species = report.Species
                    var Result = report.Test
                    var Units = report.Units
                    var Total = report.Total

                    // Write Names of Species
                    for (var i = 0; i < ListSpecies.length; i++) {
                        $scope[ListSpecies[i]+'_Name'] = Species[i];
                        $scope[ListSpecies[i]+'_Result'] = Math.round(Result[i]*100)/100;
                        $scope[ListSpecies[i]+'_Unit'] = Units[i]
                        $scope[ListSpecies[i]+'_Total'] = (Math.round(Total[i]*100)/100).toString() + ' mg';                        
                    }; 
                })
            .error(function(response) {
                toastr.error(response.message, 'Calculations failed!');                    
            });

        };

        $scope.Report = function(){            

            $http.get('/1065/api/v1/data/calculations/')
                .success(function(response){
                    toastr.success(response.message, 'Report finished!');
		            location.href =('/1065/api/v1/data/calculations/');                    
                })
                .error(function(response){
                    toastr.error(response.message, 'Report failed!');
                });
        }

        $scope.$on('ResetAll',function(){
            Start();
        });

        function Start() {
            for (var i = 0; i < ListSpecies.length; i++) {
                for (var j = 0; j < ListFields.length; j++) {
                    $scope[ListSpecies[i]+'_'+ListFields[j]] = 'Undefined';
                };
                
            }; 
        }
    }

})();
