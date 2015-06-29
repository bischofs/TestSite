(function() {
    'use strict';

    angular
        .module('TestSite.results.controllers')
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = ['$scope', '$http', 'toastr'];



    function ResultsController($scope, $http, toastr) {

                // Write Names of Species
        $scope.CO2_Name = 'Undefined'
        $scope.CO_Name = 'Undefined'                  
        $scope.NOX_Name = 'Undefined'
        $scope.THC_Name = 'Undefined'
        $scope.NMHC_Name = 'Undefined' 

        // Write Values of Species
        $scope.CO2_Result = 'Undefined'
        $scope.CO_Result = 'Undefined'                  
        $scope.NOX_Result = 'Undefined'
        $scope.THC_Result = 'Undefined'
        $scope.NMHC_Result = 'Undefined'         

        // Write Units of Species
        $scope.CO2_Unit = 'Undefined'
        $scope.CO_Unit = 'Undefined'                  
        $scope.NOX_Unit = 'Undefined'
        $scope.THC_Unit = 'Undefined'
        $scope.NMHC_Unit = 'Undefined'            

        // Write Total of Species
        $scope.CO2_Total = 'Undefined'
        $scope.CO_Total = 'Undefined'                  
        $scope.NOX_Total = 'Undefined'
        $scope.THC_Total = 'Undefined'
        $scope.NMHC_Total = 'Undefined'    

        $scope.Calculation = function() {

            $scope.delay = 0;
            $scope.minDuration = 0;
            $scope.message = 'Calculation Running...';
            $scope.backdrop = true;
            $scope.promise = null;

            toastr.info('Calculations started!');
            $scope.promise = $http.post('/api/v1/data/calculations/')
                .success(function(response) {
                    toastr.success('Calculations finished!');
                    var jsonLog = JSON.parse(response)
                    var report = JSON.parse(jsonLog.Report.Results[2])
                    var Species = report.Species
                    var Result = report.Test
                    var Units = report.Units
                    var Total = report.Total

                    // Write Names of Species
                    $scope.CO2_Name = Species[0]
                    $scope.CO_Name = Species[1]                    
                    $scope.NOX_Name = Species[2]
                    $scope.THC_Name = Species[3]
                    $scope.NMHC_Name = Species[4]  

                    // Write Values of Species
                    $scope.CO2_Result = Math.round(Result[0]*100)/100
                    $scope.CO_Result = Math.round(Result[1]*100)/100                   
                    $scope.NOX_Result = Math.round(Result[2]*100)/100
                    $scope.THC_Result = Math.round(Result[3]*100)/100
                    $scope.NMHC_Result = Math.round(Result[4]*100)/100          

                    // Write Units of Species
                    $scope.CO2_Unit = Units[0]
                    $scope.CO_Unit = Units[1]                    
                    $scope.NOX_Unit = Units[2]
                    $scope.THC_Unit = Units[3]
                    $scope.NMHC_Unit = Units[4]            

                    // Write Total of Species
                    $scope.CO2_Total = (Math.round(Total[0]*100)/100).toString() + ' mg'
                    $scope.CO_Total = (Math.round(Total[1]*100)/100).toString() + ' mg'                 
                    $scope.NOX_Total = (Math.round(Total[2]*100)/100).toString() + ' mg'
                    $scope.THC_Total = (Math.round(Total[3]*100)/100).toString() + ' mg'
                    $scope.NMHC_Total = (Math.round(Total[4]*100)/100).toString() + ' mg'                                                             

                    //document.getElementById("ResultTable").style.visibility = "visible";

                })
                .error(function(response) {
                    toastr.error(response.message, 'Calculations failed!');                    
                });

        };

        $scope.Report = function(){            

            $http.get('/api/v1/data/calculations/')
                .success(function(response){
                    toastr.success(response.message, 'Report finished!');
		            location.href =('/api/v1/data/calculations/');                    
                })
                .error(function(response){
                    toastr.error(response.message, 'Report failed!');
                });
        }
    }

})();
