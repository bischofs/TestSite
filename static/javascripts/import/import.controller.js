(function() {
    'use strict';

    angular
    .module('TestSite.import.controllers')
    .controller('ImportController', ImportController);

    ImportController.$inject = ['$scope', 'FileUploader', 'toastr', 'infoboxService', '$http'];

function ImportController($scope, FileUploader, toastr, infoboxService) {

    $scope.uploader = new FileUploader();
    $scope.uploader.url = '/1065/api/v1/data/import/'
    $scope.uploader.method = 'POST'
    $scope.uploader.autoUpload = true;
    $scope.uploader.onSuccessItem = onSuccessItem;
    $scope.uploader.onErrorItem = onErrorItem;

    // Load default Values for Regression Panel
    var List_reg = ['powerI','powerr','powers','powerse','speedI','speedr','speeds','speedse','torqueI','torquer','torques','torquese']
    FirstLoad()

    $scope.$on('ResetAll',function(){
         FirstLoad()
         $scope.uploader.progress = 0
         $scope.uploader.clearQueue()
    }) 

    function FirstLoad() {
        for (var i = 0; i < List_reg.length; i++) {
            $scope[List_reg[i]] = 'Unknown'
            $scope['label_' + List_reg[i]] = 'label-default'
        };
    }

    function onSuccessItem(item, response, status, headers) {

        toastr.success('File Uploaded and Verified', 'Success');
        $scope.uploadSuccess = true;


	var arr = $("strong");
	for(var i = 0; i < arr.length; i++){
	
	    if(arr[i].innerHTML.length > 20){
		var front = arr[i].innerHTML.slice(0, 6);
		var back = arr[i].innerHTML.slice(-8);
		var mid = "...";
		var res = front.concat(mid, back);
		
		arr[i].innerHTML = res;
	    }
	}
	

        var jsonObj = JSON.parse(response);
        if (jsonObj.File == 'FULL') {
            infoboxService.updateFull();
        } else if(jsonObj.File == 'PRE'){
            infoboxService.updatePre();
        } else if(jsonObj.File == 'MAIN'){
            infoboxService.updateTest(jsonObj.CycleAttr);
        } else if(jsonObj.File == 'POST'){
            infoboxService.updatePost();
        }
        if (jsonObj['FilesLoaded'] == true){
            infoboxService.finishUpload();
        }
    }

    function onErrorItem(item, response, status, headers) {

        toastr.error(response.message, 'Error');
        $scope.uploadSuccess = false;
    }

    $scope.Regression = function() {

        // Fill in Regression Data
        $.get("/1065/api/v1/data/import/",{choice:document.getElementById("sel1").value}) 
            .done(function(response){
                var jsonObj = JSON.parse(response);
                var List_channel = ['Power','Speed','Torque'];
                var List_regType = ['Intercept','Rsquared','Slope','Standard Error'];
                var result = "";
                var List_reg = [['powerI','powerr','powers','powerse'],['speedI','speedr','speeds','speedse'],['torqueI','torquer','torques','torquese']]
                
                for (var i = 0; i < List_channel.length; i++) {
                    var channel = List_channel[i];
                    var List_label = List_reg[i];

                    for (var j = 0; j < List_regType.length; j++) {

                        if (jsonObj.Regression_bool[channel][List_regType[j]]) {
                                result = "label-success";
                        }             
                        else {
                                result = "label-danger";                            
                        }
                        $scope['label_' + List_label[j]] = result;
                        $scope[List_label[j]] = jsonObj.Regression[channel][List_regType[j]].toFixed(2);
                    };
                };
                $scope.$apply();
            })

            .error(function(response) {
                toastr.error(response.responseJSON.message, 'Regression data is not available');
        });
    }    
}

})()
