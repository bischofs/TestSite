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

            $scope.promise = $http.post('/1065/api/v1/data/calculations/')
                .success(function(response) {
                    $scope.TbodyVis = 'inline'
                    toastr.success('Calculations finished!');
                    var jsonLog = JSON.parse(response)
                    var report = JSON.parse(jsonLog.Report)

                    if (5 in report.Name){
                        ListSpecies.push(report.Name[5])
                    } else{
                        $scope[report.Name[5] + '_display'] = 'None';
                    }
                    if (6 in report.Name){
                        ListSpecies.push(report.Name[6])
                    } else{
                        $scope[report.Name[6] + '_display'] = 'None';
                    }
                    if (7 in report.Name){
                        ListSpecies.push(report.Name[7])
                    } else{
                        $scope[report.Name[7] + '_display'] = 'None';
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

            $http.get('/1065/api/v1/data/calculations/')
                .success(function(response){
                    toastr.success(response.message, 'Report finished!');
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
