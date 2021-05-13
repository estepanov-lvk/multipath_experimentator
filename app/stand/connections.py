import fabric 
SSHCONFIG = "./app/stand/ssh_config"
SSHCONFIG_PATH = "./app/stand/"
conn_config = fabric.Config(runtime_ssh_path=SSHCONFIG)
conn_config.load_ssh_config()

head_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_head")
head_config.load_ssh_config()

vm1_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_vm")
vm1_config.load_ssh_config()

vm2_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_vm2")
vm2_config.load_ssh_config()


head_root_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_head_root")
head_root_config.load_ssh_config()

vm1_root_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_vm_root")
vm1_root_config.load_ssh_config()

vm2_root_config = fabric.Config(runtime_ssh_path="./app/stand/ssh_config_vm2_root")
vm2_root_config.load_ssh_config()



def make_ssh_config(filename):
    import sys
    # TODO: make it more universal
    sys.path.append("/home/fdmp/experimentator")
    import textwrap
    from app.stand.server_model import Server
    from app.models import VM
    servers = Server.query.all()
    vms = VM.query.all()
    entries = []

    for srv in servers:
        entries.append((srv.servername, srv.server_ip, srv.username, srv.identity_file))
        #entries.append((srv.servername + 'root', srv.server_ip, srv.username, srv.identity_file))

    for vm in vms:
        entries.append((vm.vmname, vm.vm_ip, vm.username, vm.identity_file))

    with open(filename, 'w') as fd:
        for x in entries:
            fd.write(
                textwrap.dedent("""
                    Host {}
                        Hostname {}
                        User {}
                        IdentityFile {}
                """).format(*x)
            )


if __name__ == '__main__':
    make_ssh_config('app/stand/ssh_config')
