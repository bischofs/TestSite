/**
* Authentication
* @namespace TestSite.authentication.services
*/
(function () {
  'use strict';

  angular
  .module('TestSite.authentication.services')
  .factory('Authentication', Authentication);

  Authentication.$inject = ['$cookies', '$http','toastr'];

  /**
  * @namespace Authentication
  * @returns {Factory}
  */
  function Authentication($cookies, $http, toastr) {
    /**
    * @name Authentication
    * @desc The Factory to be returned
    */
      var Authentication = {
	  getAuthenticatedAccount: getAuthenticatedAccount,
	  setAuthenticatedAccount: setAuthenticatedAccount,
	  isAuthenticated: isAuthenticated,
	  login:login,
	  logout:logout,
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
	  return $http.post('/1065/api/v1/accounts/', {
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
          return $http.post('/1065/api/v1/auth/login/', {
              email: email, password: password
          }).then(loginSuccessFn,loginErrorFn);

	  /**
	   * @name loginSuccessFn
	   * @desc Set the authenticated account and redirect to index
	   */
	  function loginSuccessFn(data, status, headers, config) {
	      Authentication.setAuthenticatedAccount(data.data);

	      window.location = '/1065/evaluation/import';
	  }

	  /**
	   * @name loginErrorFn
	   * @desc Log "Epic failure!" to the console
	   */
	  function loginErrorFn(data, status, headers, config) {
	      toastr.error("Username or password is incorrect", 'Error')
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

      /**
       * @name isAuthenticated
       * @desc Check if the current user is authenticated
       * @returns {boolean} True is user is authenticated, else false.
       * @memberOf thinkster.authentication.services.Authentication
       */
       function isAuthenticated(){
         return !!$cookies.authenticatedAccount;
       }

      /**
       * @name setAuthenticatedAccount
       * @desc Stringify the account object and store it in a cookie
       * @param {Object} user The account object to be stored
       * @returns {undefined}
       * @memberOf thinkster.authentication.services.Authentication
       */
       function setAuthenticatedAccount(account){
         $cookies.authenticatedAccount = JSON.stringify(account);
       }


      /**
       * @name unauthenticate
       * @desc Delete the cookie where the user object is stored
       * @returns {undefined}
       * @memberOf thinkster.authentication.services.Authentication
       */
       function unauthenticate(){
         delete $cookies.authenticatedAccount;
       }


/**
 * @name logout
 * @desc Try to log the user out
 * @returns {Promise}
 * @memberOf thinkster.authentication.services.Authentication
 */
 function logout() {
  return $http.post('/1065/api/v1/auth/logout/')
  .then(logoutSuccessFn, logoutErrorFn);

  /**
   * @name logoutSuccessFn
   * @desc Unauthenticate and redirect to index with page reload
   */
   function logoutSuccessFn(data, status, headers, config) {
    Authentication.unauthenticate();

    window.location = '/';
  }

  /**
   * @name logoutErrorFn
   * @desc Log "Epic failure!" to the console
   */
   function logoutErrorFn(data, status, headers, config) {


    console.error(data);
  }
}



}





})();
