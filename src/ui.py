from tkinter import ttk
import tkinter as tk
from tkinter.filedialog import askopenfilename
from os.path import expanduser
import json
from ssh import Ssh


class Ui(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        # Define FIELD Properties
        self.config_path_filename = tk.StringVar()
        self.dev_branch_name = tk.StringVar()
        self.stage_branch_name = tk.StringVar()
        self.prod_branch_name = tk.StringVar()
        self.need_checkout_branch = tk.IntVar()
        self.need_git_pull = tk.IntVar()
        self.need_npm_install = tk.IntVar()
        self.need_npm_update = tk.IntVar()
        self.need_npm_prod = tk.IntVar()
        self.status_field = tk.StringVar()
        self.set_default_field_values()

        # DEFINE Configuration Values / These should be strings
        self.config_path = None
        self.config_json = None

        # DEFINE SERVER ADDRESSES / These should be arrays
        self.dev_server = None
        self.stage_server = None
        self.prod_server = None

        # DEFINE SERVER PATHS / These should be strings
        self.dev_path = None
        self.stage_path = None
        self.prod_path = None

        # Start creating widget parts ---
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def set_default_field_values(self):
        self.dev_branch_name.set('')
        self.stage_branch_name.set('')
        self.prod_branch_name.set('')
        self.need_checkout_branch.set(0)
        self.need_git_pull.set(1)
        self.need_npm_install.set(0)
        self.need_npm_update.set(0)
        self.need_npm_prod.set(0)
        self.status_field.set('Nothing Happened Yet...')

    def create_spacer(self, pad):
        ttk.Frame(self, relief='flat', borderwidth=1).pack(pady=pad)

    def create_label(self, content):
        ttk.Label(self, text=content).pack(pady=2)

    def create_text_field(self, vbind):
        ttk.Entry(self, textvariable=vbind).pack(pady=2)

    def create_checkbox(self, vbind, lbl=''):
        ttk.Checkbutton(self, text=lbl, onvalue=1, offvalue=0, variable=vbind).pack(pady=2)

    def create_button(self, title, callback):
        ttk.Button(self, text='  ' + title + '  ', command=callback).pack(pady=2)

    def create_widgets(self):
        # Create field for Config picker
        ttk.Entry(self, textvariable=self.config_path_filename, state="readonly").pack(pady=2)
        self.create_button('Select Config', self.handle_click_select_config)
        self.create_spacer(5)

        # Create field for DEV Branch
        self.create_label('DEV Branch')
        self.create_text_field(self.dev_branch_name)
        self.create_spacer(5)

        # Create field for STAGE Branch
        self.create_label('STAGE Branch')
        self.create_text_field(self.stage_branch_name)
        self.create_spacer(5)

        # Create field for PROD Branch
        self.create_label('PROD Branch')
        self.create_text_field(self.prod_branch_name)

        self.create_spacer(10)

        # Create checkbox to know if check out branch is needed
        self.create_checkbox(self.need_checkout_branch, 'Do checkout to branch?')

        # Create checkbox to know if git pull origin {branch} is needed
        self.create_checkbox(self.need_git_pull, 'Do git pull from origin?')

        # Create checkbox to know if NPM install is needed
        self.create_checkbox(self.need_npm_install, 'Do npm install?')

        # Create checkbox to know if NPM update is needed
        self.create_checkbox(self.need_npm_update, 'Do npm update?')

        # Create checkbox to know if NPM should run as prod
        self.create_checkbox(self.need_npm_prod, 'Do npm run prod?')

        # Create the Buttons
        self.create_spacer(10)
        self.create_button('Deploy to DEV', self.deploy_to_dev)
        self.create_button('Deploy to STAGE', self.deploy_to_stage)
        self.create_button('Deploy to PROD', self.deploy_to_prod)
        self.create_button('Default', self.set_default_field_values)
        self.create_button('Close', self.parent.destroy)

    def deploy_to_dev(self):
        if self.is_config_valid(self.config_json, 'dev'):
            print('===== Preparing deploy to DEV Server =====')
            ssh = Ssh(self.get_ssh_opts('dev'))
            ssh.deploy()

    def deploy_to_stage(self):
        if self.is_config_valid(self.config_json, 'stage'):
            print('===== Preparing deploy to STAGE Server =====')
            ssh = Ssh(self.get_ssh_opts('stage'))
            ssh.deploy()

    def deploy_to_prod(self):
        if self.is_config_valid(self.config_json, 'prod'):
            print('===== Preparing deploy to PROD Server =====')
            ssh = Ssh(self.get_ssh_opts('prod'))
            ssh.deploy()

    # noinspection PyUnusedLocal
    def is_config_valid(self, j, target):

        if j:
            print(f'Current used config is : {self.config_path_filename.get()}')
            print('Checking for missing values...')

            # Layer 1
            if target not in self.config_json:
                print(f'Missing Target Environment!')
                return False

            # Layer 2
            elif 'server' not in self.config_json[target]:
                print(f'Missing value for {target}.server')
                return False
            elif not self.config_json[target]['server']:
                print(f'Value for {target}.server should not be empty!')
                return False

            # Layer 3
            elif 'branch' not in self.config_json[target]:
                print(f'Missing value for {target}.branch')
                return False
            elif not self.config_json[target]['branch']:
                print(f'Value for {target}.branch should not be empty!')
                return False

            # Layer 4
            elif 'path' not in self.config_json[target]:
                print(f'Missing value for {target}.path')
                return False
            elif not self.config_json[target]['path']:
                print(f'Value for {target}.path should not be empty!')
                return False

            # If all conditions passed, return True
            else:
                return True

        else:
            print('There are no config values. Please select a config file.')
            return False

    def get_ssh_opts(self, target):
        return {
            'target': target,
            'server': getattr(self, target + '_server'),
            'branch_name': getattr(self, target + '_branch_name').get(),
            'path': getattr(self, target + '_path'),
            'is_checkout_branch': bool(self.need_checkout_branch.get()),
            'is_git_pull': bool(self.need_git_pull.get()),
            'is_npm_install': bool(self.need_npm_install.get()),
            'is_npm_update': bool(self.need_npm_update.get()),
            'is_npm_prod': bool(self.need_npm_prod.get())
        }

    def handle_click_select_config(self):
        path = askopenfilename(initialdir=expanduser('../config'),
                               filetypes=(("Text File", "*.json"), ("All Files", "*.*")),
                               title="Choose a file."
                               )

        self.config_path = path
        self.config_path_filename.set(path.split('/')[-1])

        # Load the json file base on given path.
        if self.config_path:
            with open(self.config_path) as f:
                try:
                    d = json.load(f)
                except ValueError:
                    print('Invalid JSON Format')
                    self.set_default_field_values()
                    return False

                self.config_json = d

                # Set Branch Names
                self.dev_branch_name.set(self.gjv(d, 'dev.branch', ''))
                self.stage_branch_name.set(self.gjv(d, 'stage.branch', ''))
                self.prod_branch_name.set(self.gjv(d, 'prod.branch', ''))

                # Set Server IPs
                self.dev_server = self.gjv(d, 'dev.server', None)
                self.stage_server = self.gjv(d, 'stage.server', None)
                self.prod_server = self.gjv(d, 'prod.server', None)

                # Set Server Paths
                self.dev_path = self.gjv(d, 'dev.path', None)
                self.stage_path = self.gjv(d, 'stage.path', None)
                self.prod_path = self.gjv(d, 'prod.path', None)

    # Get JSON Value Helper method
    # @param j - Json Object
    # @param k - key to find in Json Object
    # @param d - default value if Json member is invalid
    @staticmethod
    def gjv(j, k, d):
        k = k.split('.')
        return j[k[0]][k[1]] if k[0] in j and k[1] in j[k[0]] else d
