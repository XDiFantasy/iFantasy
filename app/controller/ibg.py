from flask import render_template
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView, MasterDetailView
from app import appbuilder, db
from app.model import Equip, AttrCh, Strategy, FundType, Theme
"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""
class FundTypeModelView(ModelView):
    datamodel = SQLAInterface(FundType)
    list_columns = [
        'price', 'rate'
    ]
class ThemeModelView(ModelView):
    datamodel = SQLAInterface(Theme)
    list_columns = [
        'title', 'price'
    ]
    show_fieldsets = [
        ('Base',{'fields':[
            'title', 'detail', 'price'
        ]}),
        ('Players',{'fields':[
            'player_one','player_two','player_three'
        ]})
    ]
    add_fieldsets = [
        ('Base',{'fields':[
            'title', 'detail', 'price'
        ]}),
        ('Players',{'fields':[
            'player_one','player_two','player_three'
        ]})
    ]
class AttrChModelView(ModelView):
    datamodel = SQLAInterface(AttrCh)
    
    

class EquipModelView(ModelView):
    datamodel = SQLAInterface(Equip)
    list_columns = [
        'name', 'attr_ch.comment'
    ]
    #related_views = [AttrChModelView]
    show_fieldsets = [
        ('Base',{'fields':['name','attr_ch'],'expanded':True}),
        ('Detail',{'fields':[
            'attr_ch.order',
            'attr_ch.fg_pct','attr_ch.three_pt_pct','attr_ch.fta_pct',
            'attr_ch.oreb_pct','attr_ch.dreb_pct','attr_ch.ast_pct',
            'attr_ch.tov_pct','attr_ch.stl_pct','attr_ch.blk_pct',
            'attr_ch.pf_pct',
            ]})
    ]
    edit_fieldsets = [
        ('Base',{'fields':['name','attr_ch'],'expanded':True})
    ]

class StrategyModelView(ModelView):
    datamodel = SQLAInterface(Strategy)
    list_columns = [
        'intro'
    ]
    show_fieldsets = [
        ('Base',{'fields':['intro'],'expanded':True}),
        ('Detail',{'fields':[
            'sg.order',
            'sg','sg.fg_pct','sg.three_pt_pct','sg.fta_pct',
             'sg.oreb_pct','sg.dreb_pct','sg.ast_pct',
            'sg.tov_pct','sg.stl_pct','sg.blk_pct',
             'sg.pf_pct',
             'sf','sg.fg_pct','sf.three_pt_pct','sf.fta_pct',
             'sf.oreb_pct','sf.dreb_pct','sf.ast_pct',
            'sf.tov_pct','sf.stl_pct','sf.blk_pct',
             'sf.pf_pct',
             'pg','pg.fg_pct','pg.three_pt_pct','pg.fta_pct',
             'pg.oreb_pct','pg.dreb_pct','pg.ast_pct',
            'pg.tov_pct','pg.stl_pct','pg.blk_pct',
             'pg.pf_pct',
             'pf','pf.fg_pct','pf.three_pt_pct','pf.fta_pct',
             'pf.oreb_pct','pf.dreb_pct','pf.ast_pct',
            'pf.tov_pct','pf.stl_pct','pf.blk_pct',
             'pf.pf_pct',
             'c','c.fg_pct','c.three_pt_pct','c.fta_pct',
             'c.oreb_pct','c.dreb_pct','c.ast_pct',
            'c.tov_pct','c.stl_pct','c.blk_pct',
             'c.pf_pct',
             'v_sg','v_sg.fg_pct','v_sg.three_pt_pct','v_sg.fta_pct',
             'v_sg.oreb_pct','v_sg.dreb_pct','v_sg.ast_pct',
            'v_sg.tov_pct','v_sg.stl_pct','v_sg.blk_pct',
             'v_sg.pf_pct',
             'v_sf','v_sf.fg_pct','v_sf.three_pt_pct','v_sf.fta_pct',
             'v_sf.oreb_pct','v_sf.dreb_pct','v_sf.ast_pct',
            'v_sf.tov_pct','v_sf.stl_pct','v_sf.blk_pct',
             'v_sf.pf_pct',
             'v_pg','v_pg.fg_pct','v_pg.three_pt_pct','v_pg.fta_pct',
             'v_pg.oreb_pct','v_pg.dreb_pct','v_pg.ast_pct',
            'v_pg.tov_pct','v_pg.stl_pct','v_pg.blk_pct',
             'v_pg.pf_pct',
              'v_pf','v_pf.fg_pct','v_pf.three_pt_pct','v_pf.fta_pct',
             'v_pf.oreb_pct','v_pf.dreb_pct','v_pf.ast_pct',
            'v_pf.tov_pct','v_pf.stl_pct','v_pf.blk_pct',
             'v_pf.pf_pct',
             'v_c','v_c.fg_pct','v_c.three_pt_pct','v_c.fta_pct',
             'v_c.oreb_pct','v_c.dreb_pct','v_c.ast_pct',
            'v_c.tov_pct','v_c.stl_pct','v_c.blk_pct',
             'v_c.pf_pct',
            ]})
    ]
    add_fieldsets = [
        ('Base',{'fields':[
            'intro', 'sg','sf','pg','pf','c',
            'v_sg','v_sf','v_pg','v_pf','v_c'
        ]})
    ]
    edit_fieldsets = [
        ('Base',{'fields':[
            'intro', 'sg','sf','pg','pf','c',
            'v_sg','v_sf','v_pg','v_pf','v_c'
        ]})
    ]




