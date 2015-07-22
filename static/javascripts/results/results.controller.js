(function() {
    'use strict';

    angular
        .module('TestSite.results.controllers')
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = ['$scope', '$http', 'toastr', 'infoboxService'];



    function ResultsController($scope, $http, toastr, cgBusy, infoboxService) {

        var ListSpecies = ['CO2','CO','NOx','THC','NMHC'];
        var ListFields = ['Name','Result','Units','Total'];
        var ListAdds = ['','','',' mg']
        //FirstLoad();

        $scope.Calculation = function() {

            toastr.info('Calculations started!');

            $scope.promiseCalc = $http.post('/1065/api/v1/data/calculations/')
                .success(function(response) {
                    $scope.TbodyVis = 'inline'
                    toastr.success('Calculations finished!');
                    var jsonLog = JSON.parse(response)
                    var report = JSON.parse(jsonLog.Report)
                    var SpeciesList = []

                    for (var key in report.Name) {
                        SpeciesList.push(report.Name[key]);
                    }

                    if (SpeciesList.indexOf("N2O")>-1){
                        ListSpecies.push("N2O");
                    } else{
                        $scope.N2O_display = 'None';
                    }
                    if (SpeciesList.indexOf("CH2O")>-1){
                        ListSpecies.push('CH2O');
                    } else{
                        $scope.CH2O_display = 'None';
                    }
                    if (SpeciesList.indexOf("NH3")>-1){
                        ListSpecies.push('NH3');
                    } else{
                        $scope.NH3_display = 'None';
                    }                                      

                    // Write Results in Table
                    for (var i = 0; i < Object.keys(report.Name).length; i++) {
                        for (var j = 0; j < ListFields.length; j++) {
                            $scope[report.Name[i]+'_'+ListFields[j]] = report[ListFields[j]][i] + ListAdds[j];
                        };
                        $scope[report.Name[i]+'_visibility'] = 'inline';
                    };
                })
                .error(function(response) {
                    toastr.error(response.message, 'Calculations failed!');                    
            });
        };

        $scope.Report = function(){            

            $scope.promiseReport = $http.get('/1065/api/v1/data/calculations/')
                .success(function(response){
                    toastr.success('Report finished!');
		            location.href =('/1065/api/v1/data/calculations/');                    
                })
                .error(function(response){
                    toastr.error(response.message, 'Report failed!');
                });
        }

        function FirstLoad() {
            $scope.TbodyVis = 'hidden'
            for (var i = 0; i < ListSpecies.length; i++) {
                for (var j = 0; j < ListFields.length; j++) {
                    $scope[ListSpecies[i]+'_'+ListFields[j]] = 'Undefined';
                };
                
            }; 
        }

        $scope.$on('ResetAll',function(){
            FirstLoad();
        });        
    }

})();
