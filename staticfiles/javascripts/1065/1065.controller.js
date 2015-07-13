/**
* NavbarController
* @namespace TestSite.import.controllers
*/
(function () {
  'use strict';

  angular
  .module('TestSite.1065.controllers' )
  .controller('MetaEvalController', MetaEvalController);

  MetaEvalController.$inject = ['$scope','$http','FileUploader','$timeout','toastr'];
    
    function MetaEvalController($scope, $http, FileUploader, $timeout, toastr) {

	var checkMetaData = function () {

	    // Simple GET request example :
	    $http.get('potatoes').
		success(function(data, status, headers, config) {
		    // this callback will be called asynchronously
		    // when the response is available
		    
		}).
		error(function(data, status, headers, config) {
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
		});

	};

	$timeout(checkMetaData());
    }
 

})();
