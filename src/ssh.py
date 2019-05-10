import paramiko


class Ssh:
    def __init__(self, opts):

        # Define properties
        self.target = opts.get('target')
        self.server = opts.get('server')
        self.branch_name = opts.get('branch_name')
        self.path = opts.get('path')
        self.is_checkout_branch = opts.get('is_checkout_branch')
        self.is_git_pull = opts.get('is_git_pull')
        self.is_npm_install = opts.get('is_npm_install')
        self.is_npm_update = opts.get('is_npm_update')
        self.is_npm_prod = opts.get('is_npm_prod')

    def print_values(self):
        print('Printing out defined values...')
        print('----------------------------------------')
        print('Server:', self.server)
        print('Branch Name:', self.branch_name)
        print('Path:', self.path)
        self.print_y_or_n('Is checkout to branch needed?', self.is_checkout_branch)
        self.print_y_or_n('Is git pull needed?', self.is_git_pull)
        self.print_y_or_n('Is npm install needed?', self.is_npm_install)
        self.print_y_or_n('Is npm update needed?', self.is_npm_update)
        self.print_y_or_n('Is npm run prod needed?', self.is_npm_prod)
        print('----------------------------------------')

    @staticmethod
    def print_y_or_n(content, v):
        print(content, 'Yes' if v else 'No')

    def prepare_commands(self):

        # Track and print the values defined
        self.print_values()
        print('\nPreparing command set...')

        # Navigate into the given path
        command_set = [f'cd {self.path}']

        # IMPORTANT:
        # In case that NPM doesn't run tru ssh session, you might need to
        # correct the node pointer in the target machine.
        # I have used the following commands below for creating symlinks.
        # ln -s /home/deploy/.nvm/versions/node/v8.11.3/bin/node /usr/bin/node
        # ln -s /home/deploy/.nvm/versions/node/v8.11.3/bin/npm /usr/bin/npm

        # If needed, do checkout to branch
        if self.is_checkout_branch:
            command_set.append(f'git checkout {self.branch_name}')

        # Initiate git pull
        if self.is_git_pull:
            command_set.append(f'git pull origin {self.branch_name}')

        # If needed, do npm install
        if self.is_npm_install:
            command_set.append('npm install')

        # If needed, do npm update
        if self.is_npm_update:
            command_set.append('npm update')

        # If needed, do npm update
        if self.is_npm_prod:
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

    def deploy(self):
        print(f'Deploying to {self.target.upper()} Server...\n')

        # Prepare commands
        commands = self.prepare_commands()

        for host in self.server:
            if host:
                self.connect_via_ssh(host, commands)
            else:
                print('Warning: Invalid host address!')

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
