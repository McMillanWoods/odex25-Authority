# -*- coding: utf-8 -*-
##############################################################################
#
#    Expert Co. Ltd.
#    Copyright (C) 2018 (<http://www.exp-sa.com/>).
#
##############################################################################
import base64

from odoo import models, fields, api, _

import datetime

from odoo.http import request
from itertools import groupby
import time
import sqlite3
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError

import json

sqllite_keys = ["ABORT",
                "ACTION",
                "ADD",
                "AFTER",
                "ALL",
                "ALTER",
                "ANALYZE",
                "AND",
                "AS",
                "ASC",
                "ATTACH",
                "AUTOINCREMENT",
                "BEFORE",
                "BEGIN",
                "BETWEEN",
                "BY",
                "CASCADE",
                "CASE",
                "CAST",
                "CHECK",
                "COLLATE",
                "COLUMN",
                "COMMIT",
                "CONFLICT",
                "CONSTRAINT",
                "CREATE",
                "CROSS",
                "CURRENT",
                "CURRENT_DATE",
                "CURRENT_TIME",
                "CURRENT_TIMESTAMP",
                "DATABASE",
                "DEFAULT",
                "DEFERRABLE",
                "DEFERRED",
                "DELETE",
                "DESC",
                "DETACH",
                "DISTINCT",
                "DO",
                "DROP",
                "EACH",
                "ELSE",
                "END",
                "ESCAPE",
                "EXCEPT",
                "EXCLUDE",
                "EXCLUSIVE",
                "EXISTS",
                "EXPLAIN",
                "FAIL",
                "FILTER",
                "FOLLOWING",
                "FOR",
                "FOREIGN",
                "FROM",
                "FULL",
                "GLOB",
                "GROUP",
                "GROUPS",
                "HAVING",
                "IF",
                "IGNORE",
                "IMMEDIATE",
                "IN",
                "INDEX",
                "INDEXED",
                "INITIALLY",
                "INNER",
                "INSERT",
                "INSTEAD",
                "INTERSECT",
                "INTO",
                "IS",
                "ISNULL",
                "JOIN",
                "KEY",
                "LEFT",
                "LIKE",
                "LIMIT",
                "MATCH",
                "NATURAL",
                "NO",
                "NOT",
                "NOTHING",
                "NOTNULL",
                "NULL",
                "OF",
                "OFFSET",
                "ON",
                "OR",
                "ORDER",
                "OTHERS",
                "OUTER",
                "OVER",
                "PARTITION",
                "PLAN",
                "PRAGMA",
                "PRECEDING",
                "PRIMARY",
                "QUERY",
                "RAISE",
                "RANGE",
                "RECURSIVE",
                "REFERENCES",
                "REGEXP",
                "REINDEX",
                "RELEASE",
                "RENAME",
                "REPLACE",
                "RESTRICT",
                "RIGHT",
                "ROLLBACK",
                "ROW",
                "ROWS",
                "SAVEPOINT",
                "SELECT",
                "SET",
                "TABLE",
                "TEMP",
                "TEMPORARY",
                "THEN",
                "TIES",
                "TO",
                "TRANSACTION",
                "TRIGGER",
                "UNBOUNDED",
                "UNION",
                "UNIQUE",
                "UPDATE",
                "USING",
                "VACUUM",
                "VALUES",
                "VIEW",
                "VIRTUAL",
                "WHEN",
                "WHERE",
                "WINDOW",
                "WITH",
                "WITHOUT"]


class data_chart_report(models.Model):
    _name = 'data.chart.report'
    _description = 'Data Chart Report'

    name = fields.Char(string='Name', copy=False)

    title = fields.Text(string='Title', copy=False)

    type = fields.Selection(
        selection=[('model', 'Model'),
                   ('query', 'Query')],
        string='Type', copy=True)

    header = fields.Html(string='Header')
    footer = fields.Html(string='Footer')

    seq = fields.Char(string='Sequence')

    menu_id = fields.Many2one(comodel_name='ir.ui.menu', string='Menu', copy=False)

    parent_menu_id = fields.Many2one(comodel_name='ir.ui.menu', string='Parent Menu')

    action_id = fields.Many2one(comodel_name='ir.actions.client', string='Action', copy=False)

    data_items_ids = fields.One2many(comodel_name='data_chart_data_item',
                                     inverse_name='report_id', string='Models', copy=True)

    report_names = fields.One2many(comodel_name='report_cols_names',
                                   inverse_name='report_id', string='Cols Names', copy=True)

    query = fields.Text(string='Query')

    model_id = fields.Many2one(comodel_name='ir.model', string='Model')

    groups_ids = fields.Many2many(comodel_name='res.groups', string='Groups', copy=True)

    def create_menu(self):
        self.ensure_one()
        if type == 'query':
            self.get_data()
        if self.menu_id:
            self.menu_id.unlink()
        if self.action_id:
            self.action_id.unlink()

        if self.type == 'query':
            action_id = self.env['ir.actions.client'].create({
                'name': self.name,
                'tag': 'data_view',
                'context': {
                    'model': 'data.chart.report',
                    'active_id': self.id,
                    'title': self.title,
                    'create': False,
                },
                'target': 'current',
            })
        else:
            action_id = self.env['ir.actions.client'].create({
                'name': self.name,
                'tag': 'data_view',
                'context': {
                    'model': self.model_id.model,
                    'active_id': self.id,
                    'title': self.title,
                    'create': False,
                },
                'target': 'current',
            })

        self.action_id = action_id.id

        menu_id = self.env['ir.ui.menu'].create({
            'name': self.name,
            'parent_id': self.parent_menu_id and self.parent_menu_id.id or False,
            'action': 'ir.actions.client,%d' % (action_id,),
            'groups_id': [[6, 0, [x.id for x in self.groups_ids]]]
        })

        self.menu_id = menu_id.id
    
    def show_data(self):
        if self.type == 'query':
            return {
                'name': self.name,
                'type': 'ir.actions.client',
                'tag': 'data_chart',
                'context': {
                    'model': 'data.chart.report',
                    'active_id': self.id,
                    'title': self.title,
                    'admin_view': True,
                },    
            }
        else:
            return {
                'name': self.name,
                'tag': 'data_view',
                'context': {
                    'model': self.model_id.model,
                    'active_id': self.id,
                    'title': self.title,
                    'admin_view': True,
                },
                'type': 'ir.actions.client',
                'target': 'new',
            }

    def get_data(self):
        self.ensure_one()
        # Create database connection to an in-memory database

        connectionObject = sqlite3.connect(":memory:")

        def display_name(model, field, value):
            try:
                # context = {'lang': user.lang}
                # self.env = self.env(context=context)
                data_items = self.data_items_ids.filtered(lambda x: x.name == model)
                if data_items:
                    data_item = data_items[0]

                    model_id = data_item.data_item

                    model = model_id.model
                    if self.env[model]._fields[field].type == 'selection':
                        value = dict(self.env[model]._fields[field]._description_selection(
                            self.env))[value]
            except:
                return value
            return value

        connectionObject.create_function("display_name", 3, display_name)

        connectionObject.row_factory = dict_factory
        # Obtain a cursor object

        cursorObject = connectionObject.cursor()

        # Create a table in the in-memory database

        for data_item in self.data_items_ids:
            model = table = False

            # if data_item.data_item.startswith('model_'):
            #     model = data_item.data_item.replace('model_', '', 1)

            #model_id = self.env['ir.model'].search([('model', '=', model)])
            model_id = data_item.data_item
            model = model_id.model
            fields = self.env['ir.model.fields'].search(
                [('model_id', 'in', model_id.ids)])
            fields = fields.read(['name', 'field_description', 'ttype'])

            fields_types = {x['name']: x['ttype'] for x in fields}
            cols = ""
            cols_names = ""
            for field in fields_types:
                if field.upper() in sqllite_keys:
                    continue
                if fields_types[field] in ['char', 'text', 'selection']:
                    cols += field + ' text , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['integer']:
                    cols += field + ' int , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['float', 'monetary']:
                    cols += field + ' REAL , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['date']:
                    cols += field + ' DATE , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['datetime']:
                    cols += field + ' datetime , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['many2one']:
                    cols += field + ' int , '
                    cols_names += field + ' , '
                elif fields_types[field] in ['boolean']:
                    cols += field + ' boolean , '
                    cols_names += field + ' , '
            createTable = "CREATE TABLE " + data_item.name + " (" + cols[0:-2] + " )"

            cursorObject.execute(createTable)
            # insert the data

            data = self.env[model].with_context({'data_chart_search': True}).search([])
            for rec in data:
                row = ""
                readed = rec.with_context({'data_chart_search': False}).read()[0]
                for item in cols_names[0:-3].split(' , '):
                    item_data = readed.get(item, False)
                    if item == 'name':
                        readed['name'] = rec.name_get()[0][1]
                        if item_data:
                            row += '"'+str(item_data)+'"' + " , "
                        if not item_data:
                            row += '" "' + " , "

                    elif fields_types[item] == 'many2one':
                        if item_data:
                            row += str(item_data[0]) + " , "
                        else:
                            row += 'null' + " , "
                    elif fields_types[item] in ['char', 'text', 'selection']:
                        if item_data:
                            item_data = str(item_data).replace('"', '\'')
                            row += '"'+str(item_data)+'"' + " , "
                        if not item_data:
                            row += '" "' + " , "

                    elif fields_types[item] in ['date', 'datetime']:
                        row += '"'+str(item_data)+'"' + " , "
                    elif fields_types[item] in ['boolean']:
                        if item_data:
                            row += str('1') + " , "
                        if not item_data:
                            row += str('0') + " , "
                    else:
                        if item_data:
                            row += str(item_data) + " , "
                        if not item_data:
                            row += 'null' + " , "

                insertValues = """INSERT INTO """ + data_item.name + \
                    """( """ + cols_names[0:-3] + """ )""" + """ values(""" + row[0:-3] + """ )"""
                cursorObject.execute(insertValues)

        queryTable = self.query

        queryResults = cursorObject.execute(queryTable)

        data = queryResults.fetchall()

        report_names = self.report_names

        #report_names = {x.d_name: x.t_name for x in report_names}

        report_names = {x.t_name: x.d_name for x in report_names}
        new_data = []
        for rec in data:
            new_rec = rec
            for item in list(filter(lambda x: x in report_names, rec.keys())):
                new_rec[report_names[item]] = rec[item]
                del new_rec[item]

            new_data.append(new_rec)

        connectionObject.close()
        return new_data


class data_chart_report_models(models.Model):
    _name = 'data_chart_data_item'
    _description = 'Data Chart Data Item'

    def _get_models_tables(self):
        ir_model_relation = self.env['ir.model.relation'].search([])
        ir_model_relation = ir_model_relation.read(['name'])
        ir_model_relation = [('rel'+'_'+x['name'], x['name']) for x in ir_model_relation]

        ir_model = self.env['ir.model'].search([])
        ir_model = ir_model.read(['model', 'name'])
        ir_model = [('model'+'_'+x['model'], x['name']+'_'+x['model']) for x in ir_model]

        return ir_model_relation + ir_model

    data_item = fields.Many2one('ir.model', string='Data node')

    name = fields.Char(string='Name')

    report_id = fields.Many2one(comodel_name='data.chart.report', string='Report')


class report_cols_names(models.Model):
    _name = 'report_cols_names'
    _description = 'Data Chart Data Cols Names'

    t_name = fields.Char(string='Technical Name')
    d_name = fields.Char(string='Display Name')
    report_id = fields.Many2one(comodel_name='data.chart.report', string='Report')


class data_chart_model(models.Model):
    _name = 'data_chart_model'

    model = fields.Char(string='Model')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    res_id = fields.Integer()

    options = fields.Text(string='Options')
    slice = fields.Text(string='slice')
    conditions = fields.Text(string='conditions')
    formats = fields.Text(string='formats')
    cols_types = fields.Text(string='Column Types')

    @api.model
    def data_chart_details(self, model, res_id=False, with_default=False):
        try:
            return self._data_chart_details(model, res_id, with_default)
        except:
            raise ValidationError(
                _('''ERROR IN REPORT CONFIGURATION ! '''))

    @api.model
    def _data_chart_details(self, model, res_id=False, with_default=False):
        """
        get the list of dicts in sorted oreder to fit in data view
        """
        uid = request.session.uid
        exist = self.search([('user_id', '=', uid), ('model', '=', model), ('res_id', '=', res_id)])

        if(with_default) or not exist:
            exist = self.search(
                [('user_id', '=', False),
                 ('model', '=', model),
                 ('res_id', '=', res_id)])

        company_image = False
        header = footer = False
        report_names = {}
        user = self.env['res.users'].search([('id', '=', uid)])
        if user:
            company_image = ""+str(user.company_id.logo, 'utf-8', 'ignore')+""
            context = {'lang': user.lang}
            self.env = self.env(context=context)

        if res_id and model == 'data.chart.report':
            data_object = self.env[model].search(
                [('id', '=', res_id)])
            data = data_object.get_data()
            cols_types = self.get_data_types(data)
            # for a dum reason
            cols_types = json.dumps(cols_types)
            header = data_object.header
            footer = data_object.footer

            if exist:
                return {'data': data, 'options': exist.options,
                        'slice': exist.slice, 'conditions': exist.conditions, 'formats': exist.formats,
                        'cols_types': exist.cols_types and exist.cols_types or cols_types,
                        'header': header, 'footer': footer, 'company_image': company_image}
            else:
                return {'data': data, 'header': header, 'footer': footer, 'cols_types': cols_types, 'company_image': company_image}

        if res_id and model != 'data.chart.report':
            data_object = self.env['data.chart.report'].search(
                [('id', '=', res_id)])

            data = self.env[model].search([])
            header = data_object.header
            footer = data_object.footer

            report_names = data_object.report_names

            report_names = {x.t_name: x.d_name for x in report_names}

        else:
            data = self.env[model].search([])

        model_id = self.env['ir.model'].search([('model', '=', model)])
        fields = self.env['ir.model.fields'].search(
            [('model_id', 'in', model_id.ids)])
        fields = fields.read(['name', 'field_description', 'ttype'])

        fields_names = {x['name']: x['field_description'] for x in fields}

        fields_types = {x['name']: x['ttype'] for x in fields}

        selectoin_fields = {}
        for fff in self.env[model]._fields:
            if self.env[model]._fields[fff].type == 'selection':
                selectoin_fields[fff] = dict(
                    self.env[model]._fields[fff]._description_selection(self.env))

        all_data = []
        cols_types = {}

        cols_in_report = []
        for field in fields_types:
            if fields_types[field] in ['char', 'text', 'selection']:
                cols_types[field in report_names and report_names[field]
                           or fields_names[field]] = {'type': 'string'}
                cols_in_report.append(field)
            elif fields_types[field] in ['integer', 'float', 'monetary']:
                cols_types[field in report_names and report_names[field]
                           or fields_names[field]] = {'type': 'number'}
                cols_in_report.append(field)
            elif fields_types[field] in ['date']:
                cols_types[field in report_names and report_names[field]
                           or fields_names[field]] = {'type': 'date string'}
                cols_in_report.append(field)
            elif fields_types[field] in ['datetime']:
                cols_types[field in report_names and report_names[field]
                           or fields_names[field]] = {'type': 'datetime'}
                cols_in_report.append(field)
            elif fields_types[field] in ['many2one']:
                cols_types[field in report_names and report_names[field]
                           or fields_names[field]] = {'type': 'string'}
                cols_in_report.append(field)

        # all_data.append(cols_types)
        # for a dum reason
        
        cols_types = json.dumps(cols_types)
        for rec in data:
            row = {}
            readed = rec.read()[0]
            for item in cols_in_report:
                if item == 'name':
                    readed['name'] = rec.name_get()[0][1]
                if fields_types[item] == 'many2one':
                    readed[item] = readed[item] and readed[item][1] or ""
                if fields_types[item] == 'selection':
                    readed[item] = selectoin_fields[item].get(readed[item], "")
                row[item in report_names and report_names[item] or fields_names[item]] = readed[item]

            all_data.append(row)

        if exist:
            return {'data': all_data, 'options': exist.options,
                    'slice': exist.slice, 'conditions': exist.conditions,
                    'cols_types': exist.cols_types and exist.cols_types or cols_types,
                    'formats': exist.formats,
                    'header': header, 'footer': footer,
                    'company_image': company_image}
        else:
            return {'data': all_data, 'company_image': company_image,
                    'header': header, 'footer': footer, 'cols_types': cols_types}

    def get_key_type(self, key, data, index):

        if not data[index][key]:
            if index + 1 < len(data):
                return self.get_key_type(key, data, index + 1)
            else:
                return {}
        # check if the data type is not string
        if type(data[index][key]) in [int, float]:
            return {'type': 'number'}

        # check date
        try:
            datetime.datetime.strptime(data[index][key], DEFAULT_SERVER_DATE_FORMAT)
            return {'type': 'date string'}
        except:
            pass

        # check datetime
        try:
            datetime.datetime.strptime(data[index][key], DEFAULT_SERVER_DATETIME_FORMAT)
            return {'type': 'datetime'}
        except:
            pass

        if data[index][key].isdigit():
            return {'type': 'number'}

        elif data[index][key] != 'null':
            return {'type': 'string'}
        else:
            if index + 1 < len(data):
                return self.get_key_type(key, data, index + 1)
            else:
                return {}

    def get_data_types(self, data):
        types_dict = {}
        for key in data[0]:
            types_dict[key] = self.get_key_type(key, data, 0)
        return types_dict

    @api.model
    def save_options(self, model, res_id, options, slice, conditions, formats, cols_types):
        uid = request.session.uid
        exist = self.search([('user_id', '=', uid), ('model', '=', model), ('res_id', '=', res_id)])

        if exist:
            exist.options = options
            exist.slice = slice
            exist.conditions = conditions
            exist.formats = formats
            exist.cols_types = cols_types
        else:
            self.create({
                'user_id': uid,
                'model': model,
                'res_id': res_id,
                'options': options,
                'slice': slice,
                'conditions': conditions,
                'formats': formats,
                'cols_types': cols_types,
            })

    @api.model
    def set_default(self, model, res_id, options, slice, conditions, formats, cols_types):
        exist = self.search(
            [('user_id', '=', False),
             ('model', '=', model),
             ('res_id', '=', res_id)])
        if exist:
            exist.options = options
            exist.slice = slice
            exist.conditions = conditions
            exist.formats = formats
            exist.cols_types = cols_types
        else:
            self.create({
                'user_id': False,
                'model': model,
                'res_id': res_id,
                'options': options,
                'slice': slice,
                'conditions': conditions,
                'formats': formats,
                'cols_types': cols_types,
            })


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
