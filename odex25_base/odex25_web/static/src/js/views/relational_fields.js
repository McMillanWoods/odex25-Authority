odoo.define('odex25_web.relational_fields', function (require) {
"use strict";

var config = require('web.config');
if (!config.device.isMobile) {
    return;
}

/**
 * In this file, we override some relational fields to improve the UX in mobile.
 */

var core = require('web.core');
var relational_fields = require('web.relational_fields');

var FieldStatus = relational_fields.FieldStatus;
var FieldMany2One = relational_fields.FieldMany2One;
var FieldX2Many = relational_fields.FieldX2Many;

var qweb = core.qweb;

var _t = core._t;

FieldStatus.include({
    /**
     * Override the custom behavior of FieldStatus to hide it if it is not set,
     * in mobile (which is the default behavior for fields).
     *
     * @returns {boolean}
     */
    isEmpty: function () {
        return !this.isSet();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _render: function () {
        this.$el.html(qweb.render("FieldStatus.content.mobile", {
            selection: this.status_information,
            status: _.findWhere(this.status_information, {selected: true}),
            clickable: this.isClickable,
        }));
    },
});

/**
 * Override the Many2One to prevent autocomplete and open kanban view in mobile for search.
 */

FieldMany2One.include({

    start: function () {
        var superRes = this._super.apply(this, arguments);
        this.$input.prop('readonly', true);
        return superRes;
    },
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Don't bind autocomplete in the mobile as it uses a different mechanism
     * On clicking Many2One will directly open popup with kanban view
     *
     * @private
     * @override
     */
    _bindAutoComplete: function () {},

    /**
     * override to add selectionMode option to search create popup option
     *
     * @private
     * @override
     */
    _getSearchCreatePopupOptions: function () {
        var self = this;
        var searchCreatePopupOptions = this._super.apply(this, arguments);
        _.extend(searchCreatePopupOptions, {
            selectionMode: true,
            on_clear: function () {
                self.reinitialize(false);
            },
        });
        return searchCreatePopupOptions;
    },

    /**
     * Override to call name_search and directly open Search Create Popup
     *
     * @override
     * @private
     * @param {string} search_val
     * @returns {Deferred}
     */
    _search: function (search_val) {
        var self = this;
        var def = new Promise(function (resolve, reject) {
            var context = self.record.getContext(self.recordParams);
            var domain = self.record.getDomain(self.recordParams);

            // Add the additionalContext
            _.extend(context, self.additionalContext);

            var blacklisted_ids = self._getSearchBlacklist();
            if (blacklisted_ids.length > 0) {
                domain.push(['id', 'not in', blacklisted_ids]);
            }

            var prom;

            if (search_val) {
                prom = self._rpc({
                    model: self.field.relation,
                    method: 'name_search',
                    kwargs: {
                        name: search_val,
                        args: domain,
                        operator: "ilike",
                        limit: self.SEARCH_MORE_LIMIT,
                        context: context,
                    },
                });
            }

            Promise.resolve(prom).then(function (results) {
                var dynamicFilters;
                if (results) {
                    var ids = _.map(results, function (x) {
                        return x[0];
                    });
                    dynamicFilters = [{
                        description: _.str.sprintf(_t('Quick search: %s'), search_val),
                        domain: [['id', 'in', ids]],
                    }];
                }
                self._searchCreatePopup("search", false, {}, dynamicFilters);
            });
        });
        this.orderer.add(def);
        return def;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * We always open Many2One search dialog for select/update field value on click of Many2One element
     *
     * @override
     * @private
     */
    _onInputClick: function () {
        return this._search();
    },
});

FieldX2Many.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _renderButtons: function () {
        var result = this._super.apply(this, arguments);
        if (this.$buttons) {
            this.$buttons
                .find('.btn-secondary')
                .removeClass('btn-secondary')
                .addClass('btn-primary btn-add-record');
        }
        return result;
    }
});

});
