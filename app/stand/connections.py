import sys
# TODO: make it more universal
sys.path.append("/home/evgeniy/msu/aspirantura/disser/codespace/experimentator/")
from app.stand.server_model import Server
import textwrap

def make_ssh_config(filename):
    servers = Server.query.all()
    entries = []

    for srv in servers:
        entries.append((srv.servername, srv.server_ip, srv.username, srv.identity_file))
        #entries.append((srv.servername + 'root', srv.server_ip, srv.username, srv.identity_file))

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
