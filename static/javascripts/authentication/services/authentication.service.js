/**
* Authentication
* @namespace TestSite.authentication.services
*/
(function () {
  'use strict';

  angular
    .module('TestSite.authentication.services')
    .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */
  function Authentication($cookies, $http) {
    /**
    * @name Authentication
    * @desc The Factory to be returned
    */
    var Authentication = {
	getAuthenticatedAccount: getAuthenticatedAccount,
	isAuthenticated: isAuthenticated,
	login:login,
	register: register,
	unauthenticate: unauthenticate
    };

    return Authentication;

    ////////////////////

    /**
    * @name register
    * @desc Try to register a new user
    * @param {string} username The username entered by the user
    * @param {string} password The password entered by the user
    * @param {string} email The email entered by the user
    * @returns {Promise}
    * @memberOf TestSite.authentication.services.Authentication
    */
      function register(email, password, username) {
	  return $http.post('/api/v1/accounts/', {
              username: username,
              password: password,
              email: email
	  });
      }
      
      
      
      /**
       * @name login
       * @desc Try to log in with email `email` and password `password`
       * @param {string} email The email entered by the user
       * @param {string} password The password entered by the user
       * @returns {Promise}
       * @memberOf TestSite.authentication.services.Authentication
       */
      
      function login(email, password) {
	  return $http.post('/api/v1/auth/login/', {
	      email: email, password: password
	  }).then(loginSuccessFn,loginErrorFn);
      
	  /**
	   * @name loginSuccessFn
	   * @desc Set the authenticated account and redirect to index
	   */
	  function loginSuccessFn(data, status, headers, config) {
	      Authentication.setAuthenticatedAccount(data.data);
	      
	      window.location = '/';
	  }
	  
	  /**
	   * @name loginErrorFn
	   * @desc Log "Epic failure!" to the console
	   */
	  function loginErrorFn(data, status, headers, config) {
	      console.error('Epic failure!');
	  }
	  
      }



      /**
       * @name getAuthenticatedAccount
       * @desc Return the currently authenticated account
       * @returns {object|undefined} Account if authenticated, else `undefined`
       * @memberOf testSite.authentication.services.Authentication
       */
      function getAuthenticatedAccount() {
	  if (!$cookies.authenticatedAccount){
	      return;
	  }
	  return JSON.parse($cookies.authenticatedAccount);
      }


      function isAuthenticated(){
	  return !!$cookies.authenticatedAccount;
      }

      
      function setAuthenticatedAccount(account){
	  $cookies.authernticateAccount = JSON.stringify(account);
      }
      

      function unauthenticate(){
	  delete $cookies.authenticatedAccount;
      }
      

      

 }
})();
