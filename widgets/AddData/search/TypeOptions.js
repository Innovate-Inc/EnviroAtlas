///////////////////////////////////////////////////////////////////////////
// Copyright © 2016 Esri. All Rights Reserved.
//
// Licensed under the Apache License Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
///////////////////////////////////////////////////////////////////////////
define(["dojo/_base/declare",
    "dojo/_base/array",
    "dojo/_base/lang",
    "dojo/on",
    "./SearchComponent",
    "dojo/text!./templates/TypeOptions.html",
    "dojo/i18n!../nls/strings",
    // "esri/layers/vector-tile",// This module shouldn't be loaded using a static dependency.
    "dojo/Deferred",
    "dijit/TooltipDialog",
    "dijit/form/DropDownButton",
    "dijit/form/CheckBox"
  ],
  function(declare, array, lang, on, SearchComponent, template, i18n, Deferred/*,
    vectorTile*/) {

    return declare([SearchComponent], {

      i18n: i18n,
      templateString: template,

      supportsVectorTile: false,

      postCreate: function() {
        this.inherited(arguments);

        this.own(on(this.tooltipDialog, "open", lang.hitch(this, function() {
          this.tooltipDialog.domNode.className += " " + this.searchPane.wabWidget.appConfig.theme.name;
        })));

        this._checkVTSupport().then(lang.hitch(this, function(supported) {
          this.supportsVectorTile = supported;
          if (!this.supportsVectorTile) {
            console.warn("AddData: Vector Tile is not supported.");
            this.vectorTileNode.style.display = "none";
          }
        }));
      },

      _checkVTSupport: function() {
        var def = new Deferred();
        require(["esri/layers/vector-tile"], function(vectorTileModule) {
          var supported = vectorTileModule.supported();
          def.resolve(supported);
        });
        return def;
      },

      getOptionWidgets: function() {
        return [
          this.mapServiceToggle,
          this.featureServiceToggle,
          this.imageServiceToggle,
          this.vectorTileServiceToggle,
          this.kmlToggle,
          this.wmsToggle
        ];
      },

      optionClicked: function() {
        this.search();
      },

      /* SearchComponent API ============================================= */

      appendQueryParams: function(params) {
        var appendQ = function(q, qToAppend) {
          if (q.length > 0) {
            q += " OR ";
          }
          return q + qToAppend;
        };

        var q = "",
          qAll = "",
          hasCheck = false;
        array.forEach(this.getOptionWidgets(), function(widget) {
          var dq = widget.focusNode.getAttribute("data-option-q");
          qAll = appendQ(qAll, dq);
          if (widget.get("checked")) {
            q = appendQ(q, dq);
            hasCheck = true;
          }
        });
        if (!hasCheck) {
          q = qAll;
        }
        if (q !== null && q.length > 0) {
          q = "(" + q + ")";
          if (params.q !== null && params.q.length > 0) {
            params.q += " AND " + q;
          } else {
            params.q = q;
          }
        }
      }

    });
  });