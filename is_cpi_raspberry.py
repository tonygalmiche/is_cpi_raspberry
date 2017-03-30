# -*- coding: utf-8 -*-

from openerp import pooler
from openerp import models,fields,api
from openerp.tools.translate import _
import time
import datetime
import os


couleurs=[
    ('blanc','Blanc'),
    ('bleu','Bleu'),
    ('orange','Orange'),
    ('rouge','Rouge'),
    ('vert','Vert')
]

colors=[
    ("blanc"  , "white"),
    ("bleu"   , "#5BC0DE"),
    ("orange" , "#F0AD4E"),
    ("rouge"  , "#D9534F"),
    ("vert"   , "#5CB85C"),
]


class is_ilot(models.Model):
    _name = 'is.ilot'
    _description = u"Ilot"
    _order='name'    #Ordre de tri par defaut des listes

    name = fields.Char('Nom' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le nom de l'ilot doit être unique !"),
    ]
    _defaults = {}


class is_etat_presse(models.Model):
    _name = 'is.etat.presse'
    _description = u"État Presse"
    _order='name'    #Ordre de tri par defaut des listes

    name             = fields.Char('Intitulé' , required=True)
    production_serie = fields.Boolean('Production série',help='Cocher cette case si cet état correspond à la production série')
    couleur          = fields.Selection(couleurs, 'Couleur', required=False, help="Couleur affichée dans l'interface à la presse")
    ligne            = fields.Integer('Ligne', required=False)
    colonne          = fields.Char('Colonne', required=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"L'intulé doit être unique !"),
    ]
    _defaults = {}






class is_presse(models.Model):


    def arret_raspberry(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.raspberry_id:
                IP=obj.raspberry_id.name
                cmd="ssh root@"+IP+" halt"
                os.system(cmd)
        return

    def reboot_raspberry(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.raspberry_id:
                IP=obj.raspberry_id.name
                cmd="ssh root@"+IP+" reboot"
                os.system(cmd)
        return

    def rafraichir_raspberry(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.raspberry_id:
                IP=obj.raspberry_id.name
                cmd="ssh root@"+IP+" killall midori"
                os.system(cmd)
        return

    def interface_presse(self, cr, uid, ids, context=None):
        presse=""
        for obj in self.browse(cr, uid, ids, context=context):
            presse=obj.name
        url = "http://raspberry-cpi/presse.php?presse="+presse
        return {
            'name'     : 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'current',
            'url'      : url
        }


    @api.depends('name')
    def _couleur(self):
        for obj in self:
            couleur=""
            for color in colors:
                if obj.etat_presse_id.couleur==color[0]:
                    couleur=color[1]
            obj.couleur=couleur


    @api.depends('name')
    def _nb_cycles(self):
        cr, uid, context = self.env.args
        context = context or {}
        for obj in self:
            cr.execute("""
                select count(*) 
                from is_presse_cycle 
                where presse_id="""+str(obj.id))
            nb_cycles = cr.fetchone()[0] or 0.0
            obj.nb_cycles = nb_cycles


    _name = 'is.presse'
    _description = u"Presse"
    _order='name'    #Ordre de tri par defaut des listes

    name           = fields.Char('Code' , required=True)
    intitule       = fields.Char('Intitulé', required=True)
    ordre          = fields.Integer('Ordre', required=False)
    ilot_id        = fields.Many2one('is.ilot', u"Ilot", required=False)
    raspberry_id   = fields.Many2one('is.raspberry', u"Raspberry", required=False)
    etat_presse_id = fields.Many2one('is.etat.presse', u"État Presse", required=False)
    couleur        = fields.Char('Couleur'            , compute='_couleur')
    nb_cycles      = fields.Integer('Nombre de cycles', compute='_nb_cycles')


    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le code de la presse doit être unique !"),
    ]
    _defaults = {}



class is_raspberry(models.Model):
    _name = 'is.raspberry'
    _description = u"raspberry"
    _order='name'    #Ordre de tri par defaut des listes
    
    name      = fields.Char('Adresse IP' , required=True)
    presse_id = fields.Many2one('is.presse', u"Presse", required=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"L'adresse IP doit être unique !"),
    ]
    
    _defaults = {}





class is_of(models.Model):
    _name = 'is.of'
    _description = u"Ordre de fabrication"
    _rec_name = "name"
    _order='name desc'

    name          = fields.Char('N°OF' , required=True)
    moule         = fields.Char('Moule' , required=False)
    nb_empreintes = fields.Integer("Nombre d'empreintes", required=False)
    coef_cpi      = fields.Integer("Coefficient Theia", required=False)
    code_article  = fields.Char('Code article' , required=True)
    designation   = fields.Char('Désignation' , required=False)
    uc            = fields.Integer('Qt par UC', required=False)
    cout          = fields.Float('Coût article', digits=(12,4), required=False)
    presse_id     = fields.Many2one('is.presse', u"Presse", required=False)
    affecte       = fields.Boolean('OF affecté à la presse',help="Cocher cette case si l'OF est affecté à la presse")
    ordre         = fields.Integer('Ordre', required=False)
    qt            = fields.Integer('Qt à produire', required=False)
    nb_cycles     = fields.Integer('Nombre de cycles')
    qt_theorique  = fields.Integer('Qt réalisée théorique', required=False)
    qt_declaree   = fields.Integer('Qt déclarée', required=False)
    qt_restante   = fields.Integer('Qt restante', required=False)
    qt_rebut      = fields.Integer('Qt rebuts', required=False)
    cycle_gamme   = fields.Float('Temps cycle gamme', digits=(12,1), required=False)
    cycle_moyen   = fields.Float('Temps cycle moyen', digits=(12,1), required=False)
    tps_restant   = fields.Float('Temps de production restant', required=False)
    heure_debut   = fields.Datetime('Heure de début de production', required=False)
    heure_fin     = fields.Datetime('Heure de fin de production', required=False)

    tps_ids       = fields.One2many('is.of.tps'  , 'of_id', u"Répartition des temps d'arrêt")
    rebut_ids     = fields.One2many('is.of.rebut', 'of_id', u"Répartition des rebuts")
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le numéro d'OF doit être unique !"),
    ]
    _defaults = {}


    def run_bilan_fin_of_scheduler_action(self, cr, uid, use_new_cursor=False, company_id = False, context=None):
        self.run_bilan_fin_of(cr, uid, context)


    @api.multi
    def run_bilan_fin_of(self):
        #** OF terminés depuis moins de 2 jours ********************************
        now  = datetime.date.today()                  # Date du jour
        heure_fin = now + datetime.timedelta(days=-2) # Date -2 jour
        heure_fin = heure_fin.strftime('%Y-%m-%d')    # Formatage
        ofs=self.env['is.of'].search([
            ('heure_fin' ,'>=',heure_fin),
        ])
        ofs.bilan_fin_of()
        #***********************************************************************

        #** OF en cours ********************************************************
        ofs=self.env['is.of'].search([
            ('heure_debut' ,'!=', False),
            ('heure_fin'   ,'=' , False),
        ])
        ofs.bilan_fin_of()
        #***********************************************************************
        return []

    @api.multi
    def bilan_fin_of(self):
        cr = self._cr
        nb=len(self)
        ct=0
        for obj in self:
            ct=ct+1
            print str(ct)+u"/"+str(nb)+u" - "+obj.name

            #** Répartition des temps d'arrêt **********************************
            SQL="""
                select
                    ipa.type_arret_id,
                    sum(ipa.tps_arret)
                from is_presse_arret ipa inner join is_presse_arret_of_rel ipaof on ipa.id=ipaof.is_of_id
                                         inner join is_of                     io on ipaof.is_presse_arret_id=io.id
                where ipaof.is_presse_arret_id="""+str(obj.id)+""" and io.presse_id=ipa.presse_id
                group by ipa.type_arret_id
            """
            cr.execute(SQL)
            result = cr.fetchall()
            obj.tps_ids.unlink()
            for row in result:
                vals={
                    'of_id'         : obj.id,
                    'etat_presse_id': row[0],
                    'tps_arret'     : row[1],
                }
                self.env['is.of.tps'].create(vals)
            #*******************************************************************

            #** Répartition des rebuts *****************************************
            SQL="""
                select defaut_id,sum(qt_rebut)::int
                from is_of_declaration 
                where of_id="""+str(obj.id)+""" and qt_rebut is not null and defaut_id is not null
                group by defaut_id;
            """
            cr.execute(SQL)
            result = cr.fetchall()
            obj.rebut_ids.unlink()
            for row in result:
                vals={
                    'of_id'    : obj.id,
                    'defaut_id': row[0],
                    'qt_rebut' : row[1],
                }
                id=self.env['is.of.rebut'].create(vals)
            #*******************************************************************

            #** Quantité déclarée bonne ****************************************
            SQL="""
                select sum(qt_bonne)::int
                from is_of_declaration 
                where of_id="""+str(obj.id)+""" and qt_bonne is not null
            """
            cr.execute(SQL)
            result = cr.fetchall()
            for row in result:
                obj.qt_declaree=row[0]
            #*******************************************************************


            #** Nombre de cycles ***********************************************
            SQL="""
                SELECT count(*) as nb
                FROM is_presse_cycle a inner join is_presse_cycle_of_rel b on id=b.is_of_id
                WHERE is_presse_cycle_id="""+str(obj.id)+"""
                GROUP BY b.is_presse_cycle_id
            """
            cr.execute(SQL)
            result = cr.fetchall()
            for row in result:
                obj.nb_cycles=row[0]
            #*******************************************************************
        return []


class is_of_tps(models.Model):
    _name='is.of.tps'
    _order='of_id,tps_arret desc,etat_presse_id'

    @api.depends('etat_presse_id')
    def _couleur(self):
        for obj in self:
            couleur=""
            for color in colors:
                if obj.etat_presse_id.couleur==color[0]:
                    couleur=color[1]
            obj.couleur=couleur

    of_id          = fields.Many2one('is.of', 'N°OF', required=True, ondelete='cascade', readonly=True)
    etat_presse_id = fields.Many2one('is.etat.presse', u"État Presse", required=True)
    couleur        = fields.Char('Couleur', compute='_couleur')
    tps_arret      = fields.Float('Durée dans cet état (H)', digits=(12,4))


class is_of_rebut(models.Model):
    _name='is.of.rebut'
    _order='of_id,qt_rebut desc,defaut_id'

    of_id      = fields.Many2one('is.of', 'N°OF', required=True, ondelete='cascade', readonly=True)
    defaut_id  = fields.Many2one('is.type.defaut', u"Type de défaut", required=True)
    qt_rebut   = fields.Integer('Qt rebut')


class is_of_declaration(models.Model):
    _name = 'is.of.declaration'
    _description = u"Déclaration des fabrications et des rebuts sur les OF"
    _rec_name = "name"
    _order='name desc'

    name       = fields.Datetime("Date Heure",required=True)
    of_id      = fields.Many2one('is.of', u"OF", required=True)
    num_carton = fields.Integer('N°Carton', required=False)
    qt_bonne   = fields.Integer('Qt bonne', required=False)
    qt_rebut   = fields.Integer('Qt rebut', required=False)
    defaut_id  = fields.Many2one('is.type.defaut', u"Type de défaut", required=False)

    _defaults = {}


class is_presse_cycle(models.Model):
    _name = 'is.presse.cycle'
    _description = u"Cycles des presses"
    _rec_name = "date_heure"
    _order='date_heure desc'

    date_heure = fields.Datetime("Date Heure",required=True, select=True)
    presse_id  = fields.Many2one('is.presse', u"Presse", required=False, select=True)
    of_ids     = fields.Many2many('is.of', 'is_presse_cycle_of_rel', 'is_of_id', 'is_presse_cycle_id', 'OF', readonly=False, required=False)
    
    _sql_constraints = []
    _defaults = {}


class is_presse_arret(models.Model):
    _name = 'is.presse.arret'
    _description = u"Arrêts des presses"
    _rec_name = "date_heure"
    _order='date_heure desc'

    @api.depends('date_heure')
    def _couleur(self):
        for obj in self:
            couleur=""
            for color in colors:
                if obj.type_arret_id.couleur==color[0]:
                    couleur=color[1]
            obj.couleur=couleur

    date_heure    = fields.Datetime("Date Heure",required=True)
    presse_id     = fields.Many2one('is.presse', u"Presse", required=True)
    type_arret_id = fields.Many2one('is.etat.presse', u"État de la presse", required=True)
    couleur       = fields.Char('Couleur'            , compute='_couleur')
    origine       = fields.Char("Origine du changement d'état")
    tps_arret     = fields.Float("Durée dans cet état", required=False)
    of_ids        = fields.Many2many('is.of', 'is_presse_arret_of_rel', 'is_of_id', 'is_presse_arret_id', 'OF', readonly=False, required=False)

    _sql_constraints = []
    _defaults = {}


class is_type_defaut(models.Model):
    _name = 'is.type.defaut'
    _description = u"Type de défaut des rebuts"
    _order='name'

    name = fields.Char('Type de défaut' , required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u"Le type de défaut doit être unique !"),
    ]
    _defaults = {}




