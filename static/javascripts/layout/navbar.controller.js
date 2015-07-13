/**
* NavbarController
* @namespace thinkster.layout.controllers
*/
(function () {
  'use strict';

  angular
    .module('TestSite.layout.controllers')
    .controller('NavbarController', NavbarController);

  NavbarController.$inject = ['$scope', 'Authentication', 'infoboxService'];

  /**
  * @namespace NavbarController
  */
  function NavbarController($scope, Authentication, infoboxService) {
    var vm = this;
    $scope.DelayButton = 'None';

    vm.logout = logout;

    /**
    * @name logout
    * @desc Log the user out
    * @memberOf thinkster.layout.controllers.NavbarController
    */
    $scope.$on('TestUploaded',function(){

      if (infoboxService.CycleType == 'Transient'){
        $scope.DelayButton = 'inline'
      } 
      
    })

    function logout() {
      Authentication.logout();
    }
  }
})();
