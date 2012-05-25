import os
import sys
import tempfile
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

class Renderer(object):
    
    def __init__(self, template_dir=None):
        self.tmpdir = None
        #if template_dir == None:
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        #    print template_dir
        try:    
            self.template_lookup = TemplateLookup(directories=[template_dir])
        except:
            print exceptions.text_error_template().render()

    def get_temp_dir(self):
        if self.tmpdir == None:
            try:
                tmpdir = tempfile.mkdtemp(prefix='mako-')
                self.tmpdir = tmpdir
                return tmpdir
            except Exception as e:
                print "Error Detected: {0}".format(e)
        else:
            try:
                os.path.isdir(self.tmpdir)
                return self.tmpdir
            except Exception as e:
                print "Error Detected: {0}".format(e)


    def serve_template(self, template_name, **kwargs):
        try:
            render_template = self.template_lookup.get_template(template_name)
            return render_template.render(**kwargs)
        except:
            print exceptions.text_error_template().render()
    
    

if __name__ == '__main__':
    C = {'author': 'charles.sibbald@fsa.gov.uk',
 'email_recipients': ['andrew.boothroyd@fsa.gov.uk',
                      'ganesh.iyer@fsa.gov.uk',
                      'yasser.nabi@fsa.gov.uk',
                      'dave.barlow@fsa.gov.uk',
                      'Jayachandra.Vangara@fsa.gov.uk',
                      'charles.sibbald@fsa.gov.uk',
                      'dan.clark@fsa.gov.uk',
                      'stuart.thorn@fsa.gov.uk',
                      'michael.penrose@fsa.gov.uk',
                      'yahya.saeed@fsa.gov.uk',
                      'mark.wilson5@fsa.gov.uk',
                      'daniel.watkins@fsa.gov.uk'],
 'release_alphas': ['0.8.3.A6',
                    '0.8.4.A1',
                    '0.8.4.A2',
                    '0.8.4.A3',
                    '0.8.5.A1'],
 'release_betas': ['0.7.5.B2', '0.8.1.B1', '0.8.2.B1', '0.8.3.B1', '0.8.4.B1'],
 'release_candidates': [],
 'release_date': '05/Oct/2011',
 'release_day': 'Wed',
 'release_time': '10:57',
 'scenariomanager_csv_url': '',
 'scenariomanager_dbscripts_url': '',
 'scenariomanager_pl_url': '',
 'scenariomanager_war_url': '',
 'svn_location': 'trunk',
 'svn_revision': 405,
 'title': 'Scenario Manager',
 'version': '0.8.5.A1'}



    R = Renderer()
    print R.serve_template('release-email.html', C=C)