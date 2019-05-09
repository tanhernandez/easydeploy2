from tkinter import ttk
import tkinter as tk
import paramiko
from src import settings


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # Define ENV Properties
        self.DEV_BRANCH = settings.DEV_BRANCH
        self.DEV_IP = settings.DEV_IP
        self.DEV_PATH = settings.DEV_PATH

        self.STAGE_BRANCH = settings.STAGE_BRANCH
        self.STAGE_IP = settings.STAGE_IP
        self.STAGE_PATH = settings.STAGE_PATH

        self.PROD_BRANCH = settings.PROD_BRANCH
        self.PROD_IP = settings.PROD_IP
        self.PROD_PATH = settings.PROD_PATH

        self.PUBLIC_SSH_KEY = settings.PUBLIC_SSH_KEY

        # Define SELF Properties
        self.dev_branch_name = tk.StringVar()
        self.stage_branch_name = tk.StringVar()
        self.prod_branch_name = tk.StringVar()
        self.need_checkout_branch = tk.IntVar()
        self.need_git_pull = tk.IntVar()
        self.need_npm_install = tk.IntVar()
        self.need_npm_update = tk.IntVar()
        self.need_npm_prod = tk.IntVar()
        self.set_default_props()

        # Start create widget parts ---
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def set_default_props(self):
        self.dev_branch_name.set(self.DEV_BRANCH)
        self.stage_branch_name.set(self.STAGE_BRANCH)
        self.prod_branch_name.set(self.PROD_BRANCH)
        self.need_checkout_branch.set(0)
        self.need_git_pull.set(1)
        self.need_npm_install.set(0)
        self.need_npm_update.set(0)
        self.need_npm_prod.set(0)

    def create_spacer(self, pad):
        ttk.Frame(self, relief='flat', borderwidth=1).pack(pady=pad)

    def create_label(self, content):
        ttk.Label(self, text=content).pack(pady=5)

    def create_text_field(self, vbind):
        ttk.Entry(self, textvariable=vbind).pack(pady=5)

    def create_checkbox(self, vbind, lbl=''):
        ttk.Checkbutton(self, text=lbl, onvalue=1, offvalue=0, variable=vbind).pack(pady=5)

    def create_button(self, title, callback):
        ttk.Button(self, text='  ' + title + '  ', command=callback).pack(pady=5)

    def create_widgets(self):
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
        self.create_button('Deploy to PROD', self.deploy_to_stage)
        self.create_button('Default', self.set_default_props)
        self.create_button('Close', root.destroy)

    @staticmethod
    def print_y_or_n(content, v):
        r = 'No'
        if v:
            r = 'Yes'
        print(content, r)

    def gather_values(self):
        print('----------------------------------------')
        print('Printing out defined values...')
        print('----------------------------------------')
        print('DEV Branch Name:', self.dev_branch_name.get())
        print('STAGE Branch Name:', self.stage_branch_name.get())
        print('PROD Branch Name:', self.prod_branch_name.get())
        self.print_y_or_n('Is checkout to branch needed?', self.need_checkout_branch.get())
        self.print_y_or_n('Is git pull needed?', self.need_git_pull.get())
        self.print_y_or_n('Is npm install needed?', self.need_npm_install.get())
        self.print_y_or_n('Is npm update needed?', self.need_npm_update.get())
        self.print_y_or_n('Is npm prod needed?', self.need_npm_prod.get())

    def prepare_commands(self, branch, path):

        # Track and print the values defined
        self.gather_values()
        print('\nPreparing command set...')

        # Navigate into the given path
        command_set = [f'cd {path}']

        # IMPORTANT:
        # In case that NPM doesn't run tru ssh session, you might need to
        # correct the node pointer in the target machine.
        # I have used the following commands below for creating symlinks.
        # ln -s /home/deploy/.nvm/versions/node/v8.11.3/bin/node /usr/bin/node
        # ln -s /home/deploy/.nvm/versions/node/v8.11.3/bin/npm /usr/bin/npm

        # If needed, do checkout to branch
        if self.need_checkout_branch.get():
            command_set.append(f'git checkout {branch}')

        # Initiate git pull
        if self.need_git_pull.get():
            command_set.append(f'git pull origin {branch}')

        # If needed, do npm install
        if self.need_npm_install.get():
            command_set.append('npm install')

        # If needed, do npm update
        if self.need_npm_update.get():
            command_set.append('npm update')

        # If needed, do npm update
        if self.need_npm_prod.get():
            command_set.append('npm run prod')
        else:
            command_set.append('npm run dev')

        command_set.append('exit')

        verbiage_commands = ''
        actual_commands = ''
        for index, item in enumerate(command_set):
            if index == 0:
                verbiage_commands += item
                actual_commands += item
            else:
                verbiage_commands += '\n' + item
                actual_commands += ' && ' + item

        print('----------------------------------------')
        print(verbiage_commands)
        print('----------------------------------------')

        return actual_commands

    def deploy_to_dev(self):
        self.deploy_to('dev')

    def deploy_to_stage(self):
        self.deploy_to('stage')

    def deploy_to(self, target):
        target = target.upper()
        print(f'Deploying to {target} Server...\n')

        # Prepare commands
        branch = getattr(self, f'{target.lower()}_branch_name').get()
        path = getattr(self, f'{target}_PATH')
        commands = self.prepare_commands(branch, path)

        # Connect to HOST
        host = getattr(self, f'{target}_IP')
        self.connect_via_ssh(host, commands)
        #     # Connect to Multiple HOSTs
        #     hosts = [x.strip() for x in self.PROD_IP.split(',')]
        #     for host in hosts:
        #         self.connect_via_ssh(host, commands)

    @staticmethod
    def connect_via_ssh(host, commands):

        ssh_client = None
        try:
            # Split the IP from the username
            cred = host.split('@')

            # Initiate SSH Connection
            print('\n\nConnecting via SSH to ' + host + ' ...')
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
            ssh_client.connect(cred[1], port=22, username=cred[0])
            stdin, stdout, stderr = ssh_client.exec_command(commands)
            stdout.channel.recv_exit_status()

            if stderr:
                print(stderr.readlines())

            for line in stdout.readlines():
                print(line)

        finally:
            ssh_client.close()
            print('SSH Session Ended Successfully')


root = tk.Tk()
root.title('Easy Deploy')
root.geometry('300x700')
app = App(master=root)
app.mainloop()
