/**
 * infobox metadata service
 * @namespace TestSite.infobox.services
 */
(function() {
    'use strict';

    angular
        .module('TestSite.infobox.services')
        .service('infoboxService', infoboxService);

    function infoboxService() {

        var myList = ["some", "data"];

        function getList() {
            return myList;
        }

        function addItem(newObj) {
            myList.push(newObj);
        }

        return {
            addItem: addItem,
            getList: getList
        };



    }

})();
