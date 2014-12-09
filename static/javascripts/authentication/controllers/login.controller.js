/**
* LoginController
* @namespace TestSite.authentication.controllers
*/
(function () {
  'use static';

  angular
    .module('TestSite.authentication.controllers')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$location', '$scope', 'Authentication'];

  /**
  * @namespace LoginController
  */
  function LoginController($location, $scope, Authentication) {
    var vm = this;

    vm.login = login;

    activate();

    /**
    * @name activate
    * @desc Actions to be performed when this controller is instantiated
    * @memberOf TestSite.authentication.controllers.LoginController
    */
    function activate() {
      // If the user is authenticated, they should not be here.
      if (Authentication.isAuthenticated()) {
        $location.url('/');
      }
    }

    /**
    * @name login
    * @desc Log the user in
    * @memberOf TestSite.authentication.controllers.LoginController
    */
    function login() {
      Authentication.login(vm.email, vm.password);
    }
  }
})();
